# tests/test_kanban_core.py
"""
Tests for Core Agile & Kanban Board Workflow:
Projects, Sprints, Epics, Issues, Comments, and Status Transitions.
"""

import pytest
from datetime import datetime, timedelta, timezone
from app.models import db, User, Team, Project, Sprint, Epic, Issue, Label, Comment, WorkflowTransition


class TestKanbanAgileWorkflow:
    """Test Agile Project Management and Kanban core domain logic."""
    
    def test_project_and_team_creation(self, app):
        """Test creating teams and assigning projects."""
        with app.app_context():
            lead = User(username='techlead', email='lead@kernel.org', role='team_lead')
            lead.set_password('LeadSecret123!')
            db.session.add(lead)
            db.session.commit()
            
            team = Team(name='Core Systems Team', department='software', is_core_team=True)
            db.session.add(team)
            db.session.commit()
            
            project = Project(
                name='ProjectFlow Kernel Engine',
                key='PFK',
                status='Active',
                workflow_type='agile',
                lead_id=lead.id,
                team_id=team.id
            )
            db.session.add(project)
            db.session.commit()
            
            assert project.id is not None
            assert project.key == 'PFK'
            assert project.lead.username == 'techlead'
            assert project.team.name == 'Core Systems Team'
    
    def test_sprint_and_epic_lifecycle(self, app):
        """Test sprint planning and epics grouping."""
        with app.app_context():
            project = Project(name='Agile Alpha', key='ALP', status='Active')
            db.session.add(project)
            db.session.commit()
            
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            sprint = Sprint(
                name='Sprint 1 - Ring0 Foundation',
                project_id=project.id,
                start_date=now,
                end_date=now + timedelta(days=14),
                goal='Ship tamper-evident audit ledger and Argon2id hashing',
                status='active'
            )
            epic = Epic(
                name='Security Hardening',
                project_id=project.id,
                color='#10b981',
                status='active'
            )
            db.session.add_all([sprint, epic])
            db.session.commit()
            
            assert sprint.id is not None
            assert epic.id is not None
            assert len(project.sprints) == 1
            assert len(project.epics) == 1
            assert project.sprints[0].goal.startswith('Ship tamper-evident')
    
    def test_issue_lifecycle_and_kanban_transitions(self, app):
        """Test issue creation, assignments, and workflow transitions."""
        with app.app_context():
            user = User(username='developer', email='dev@kernel.org', role='employee')
            user.set_password('DevPassword123!')
            project = Project(name='Kanban Demo', key='KBD', status='Active')
            db.session.add_all([user, project])
            db.session.commit()
            
            issue = Issue(
                key='KBD-1',
                title='Implement Zero-Trust Audit Ledger',
                project_id=project.id,
                assignee_id=user.id,
                reporter_id=user.id,
                issue_type='story',
                status='todo',
                priority='high'
            )
            db.session.add(issue)
            db.session.commit()
            
            assert issue.id is not None
            assert issue.key == 'KBD-1'
            assert issue.status == 'todo'
            assert issue.assignee.username == 'developer'
            
            # Transition: todo -> in_progress
            issue.status = 'in_progress'
            transition = WorkflowTransition(
                issue_id=issue.id,
                user_id=user.id,
                from_status='todo',
                to_status='in_progress',
                comment='Picked up story for Sprint 1'
            )
            db.session.add(transition)
            db.session.commit()
            
            # Transition: in_progress -> code_review -> done
            issue.status = 'done'
            transition_done = WorkflowTransition(
                issue_id=issue.id,
                user_id=user.id,
                from_status='in_progress',
                to_status='done',
                comment='Merged PR with 100% test pass rate'
            )
            db.session.add(transition_done)
            db.session.commit()
            
            reloaded_issue = Issue.query.filter_by(key='KBD-1').first()
            assert reloaded_issue.status == 'done'
            assert len(reloaded_issue.transitions) == 2
            assert reloaded_issue.transitions[1].to_status == 'done'

    def test_issue_comments_and_labels(self, app):
        """Test adding encrypted comments and labels to issues."""
        with app.app_context():
            user = User(username='reviewer', email='rev@kernel.org', role='employee')
            user.set_password('RevPassword123!')
            project = Project(name='Label Project', key='LBL', status='Active')
            db.session.add_all([user, project])
            db.session.commit()
            
            label = Label(name='SECURITY', color='#ef4444', project_id=project.id)
            issue = Issue(
                key='LBL-101',
                title='Audit Kernel Syscalls',
                project_id=project.id,
                reporter_id=user.id,
                status='open'
            )
            issue.labels.append(label)
            
            comment = Comment(
                issue_id=None,
                user_id=user.id,
                text='Reviewed: memory allocation verified with zero leaks.'
            )
            issue.comments.append(comment)
            
            db.session.add_all([label, issue])
            db.session.commit()
            
            fetched_issue = Issue.query.filter_by(key='LBL-101').first()
            assert len(fetched_issue.labels) == 1
            assert fetched_issue.labels[0].name == 'SECURITY'
            assert len(fetched_issue.comments) == 1
            # Check comment text property transparently decrypts
            assert 'zero leaks' in fetched_issue.comments[0].text

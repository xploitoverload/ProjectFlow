#!/usr/bin/env python
# create_sample_data.py - Create sample data matching the Jira images

from app import app, db
from models import (
    User, Team, Project, Issue, Epic, Label, Comment, Sprint,
    WorkflowTransition, IssueLink, Attachment, IssueWatcher
)
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def create_sample_data():
    """Create sample data for demonstration"""
    
    print("Creating sample data...")
    
    # Clean up existing data
    db.drop_all()
    db.create_all()
    print("✓ Database recreated")
    
    # Create users
    admin_user = User(
        username='admin',
        role='admin',
        avatar_color='#667eea'
    )
    admin_user.email = 'admin@example.com'
    admin_user.set_password('password123')
    
    user1 = User(
        username='john_doe',
        role='developer',
        avatar_color='#0c66e4'
    )
    user1.email = 'john@example.com'
    user1.set_password('password123')
    
    user2 = User(
        username='jane_smith',
        role='developer',
        avatar_color='#22a06b'
    )
    user2.email = 'jane@example.com'
    user2.set_password('password123')
    
    user3 = User(
        username='bob_wilson',
        role='designer',
        avatar_color='#e2b203'
    )
    user3.email = 'bob@example.com'
    user3.set_password('password123')
    
    db.session.add_all([admin_user, user1, user2, user3])
    db.session.commit()
    print("✓ Users created")
    
    # Create team
    team = Team(name='Beyond Gravity', description='Software development team')
    db.session.add(team)
    db.session.commit()
    print("✓ Team created")
    
    # Assign users to team
    admin_user.team_id = team.id
    user1.team_id = team.id
    user2.team_id = team.id
    user3.team_id = team.id
    db.session.commit()
    
    # Create project
    project = Project(
        name='Lunar Rover',
        key='NUC',
        status='Active',
        workflow_type='agile',
        team_id=team.id,
        created_by=admin_user.id
    )
    project.description = 'Space exploration mission software'
    db.session.add(project)
    db.session.commit()
    print("✓ Project created")
    
    # Create sprint
    sprint = Sprint(
        name='Sprint 1',
        project_id=project.id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=14),
        goal='Implement core features',
        status='active'
    )
    db.session.add(sprint)
    db.session.commit()
    print("✓ Sprint created")
    
    # Create epic
    epic = Epic(
        name='Web App Development',
        project_id=project.id,
        color='#0052cc',
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=60),
        status='active'
    )
    epic.description = 'Build complete web application'
    db.session.add(epic)
    db.session.commit()
    print("✓ Epic created")
    
    # Create labels
    labels = []
    label_configs = [
        ('ACCOUNTS', '#E2B203'),
        ('BILLING', '#AE2A19'),
        ('FORMS', '#8B2CA4'),
        ('FEEDBACK', '#FEC57B'),
    ]
    
    for name, color in label_configs:
        label = Label(
            name=name,
            color=color,
            project_id=project.id
        )
        labels.append(label)
        db.session.add(label)
    db.session.commit()
    print("✓ Labels created")
    
    # Create issues (matching the images)
    issues_data = [
        # TO DO Column
        {
            'key': 'NUC-344',
            'title': 'Optimize experience for mobile web',
            'status': 'open',
            'priority': 'low',
            'type': 'task',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels[0]],  # ACCOUNTS
            'points': 5,
        },
        {
            'key': 'NUC-360',
            'title': 'Onboard workout options (OWO)',
            'status': 'todo',
            'priority': 'high',
            'type': 'task',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels[0]],  # ACCOUNTS
            'points': 3,
        },
        {
            'key': 'NUC-339',
            'title': 'Billing system integration - frontend',
            'status': 'todo',
            'priority': 'medium',
            'type': 'task',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels[1], labels[2]],  # BILLING, FORMS
            'points': 3,
        },
        {
            'key': 'NUC-341',
            'title': 'Quick payment',
            'status': 'todo',
            'priority': 'high',
            'type': 'task',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels[3]],  # FEEDBACK
            'points': 3,
        },
        
        # IN PROGRESS Column
        {
            'key': 'NUC-342',
            'title': 'Fast trip search',
            'status': 'in_progress',
            'priority': 'high',
            'type': 'story',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels[0]],  # ACCOUNTS
            'points': 5,
        },
        {
            'key': 'NUC-338',
            'title': 'Affiliate links integration - frontend',
            'status': 'in_progress',
            'priority': 'medium',
            'type': 'task',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels[1]],  # BILLING
            'points': 2,
        },
        {
            'key': 'NUC-336',
            'title': 'Quick booking for accommodations - website',
            'status': 'in_progress',
            'priority': 'high',
            'type': 'story',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels[2]],  # FORMS
            'points': 5,
        },
        {
            'key': 'NUC-346',
            'title': 'Adapt web app to new payments provider',
            'status': 'in_progress',
            'priority': 'low',
            'type': 'task',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels[2]],  # FORMS
            'points': 2,
        },
        {
            'key': 'NUC-343',
            'title': 'Fluid booking on tablets',
            'status': 'in_progress',
            'priority': 'medium',
            'type': 'bug',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels[3]],  # FEEDBACK
            'points': 2,
        },
        
        # IN REVIEW Column
        {
            'key': 'NUC-387',
            'title': 'Revise and streamline booking flow',
            'status': 'code_review',
            'priority': 'high',
            'type': 'story',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels[0]],  # ACCOUNTS
            'points': 2,
        },
        {
            'key': 'NUC-349',
            'title': 'Color of pale yellow on our pages looks incorrect',
            'status': 'code_review',
            'priority': 'low',
            'type': 'bug',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels[3]],  # FEEDBACK
            'points': 1,
        },
        
        # DONE Column
        {
            'key': 'NUC-345',
            'title': 'BugFix BG Web-store app crashing',
            'status': 'done',
            'priority': 'critical',
            'type': 'bug',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels[2]],  # FORMS
            'points': 5,
        },
        {
            'key': 'NUC-350',
            'title': 'Software bug fix for BG Web-store app crashing',
            'status': 'done',
            'priority': 'high',
            'type': 'bug',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels[1]],  # BILLING
            'points': 3,
        },
        {
            'key': 'NUC-351',
            'title': 'High outage: Software bug fix - BG Web-store app crashing',
            'status': 'done',
            'priority': 'critical',
            'type': 'bug',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels[1]],  # BILLING
            'points': 4,
        },
        {
            'key': 'NUC-352',
            'title': 'Web-store purchasing performance issue fix',
            'status': 'done',
            'priority': 'medium',
            'type': 'task',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels[2]],  # FORMS
            'points': 3,
        },
    ]
    
    # Create issues
    position_by_status = {}
    for issue_data in issues_data:
        status = issue_data['status']
        position = position_by_status.get(status, 0) + 1
        position_by_status[status] = position
        
        issue = Issue(
            key=issue_data['key'],
            title=issue_data['title'],
            project_id=project.id,
            epic_id=epic.id,
            sprint_id=sprint.id,
            status=issue_data['status'],
            priority=issue_data['priority'],
            issue_type=issue_data['type'],
            assignee_id=issue_data['assignee'].id,
            reporter_id=issue_data['reporter'].id,
            story_points=issue_data['points'],
            position=position,
            time_estimate=issue_data['points'] * 4,  # Assume 4 hours per point
        )
        issue.labels = issue_data['labels']
        
        # Add some dates for timeline
        days_from_now = (position - 1) * 3
        issue.start_date = datetime.utcnow() + timedelta(days=days_from_now)
        issue.end_date = issue.start_date + timedelta(days=7)
        
        db.session.add(issue)
    
    db.session.commit()
    print("✓ Issues created (15 issues)")
    
    # Create comments
    all_issues = Issue.query.filter_by(project_id=project.id).all()
    
    comment1 = Comment(
        issue_id=all_issues[0].id,
        user_id=user1.id,
        text='I think we should prioritize this for the next sprint.'
    )
    
    comment2 = Comment(
        issue_id=all_issues[1].id,
        user_id=user2.id,
        text='Already started working on this. Should be ready by Friday.'
    )
    
    comment3 = Comment(
        issue_id=all_issues[2].id,
        user_id=user3.id,
        text='Need design approval before proceeding.'
    )
    
    db.session.add_all([comment1, comment2, comment3])
    db.session.commit()
    print("✓ Comments created")
    
    # Create workflow transitions
    transitions = [
        WorkflowTransition(
            issue_id=all_issues[11].id,
            from_status='open',
            to_status='in_progress',
            user_id=user1.id,
            comment='Starting work on this'
        ),
        WorkflowTransition(
            issue_id=all_issues[11].id,
            from_status='in_progress',
            to_status='code_review',
            user_id=user1.id,
            comment='Ready for review'
        ),
        WorkflowTransition(
            issue_id=all_issues[11].id,
            from_status='code_review',
            to_status='done',
            user_id=user2.id,
            comment='Approved and merged'
        ),
    ]
    
    db.session.add_all(transitions)
    db.session.commit()
    print("✓ Workflow transitions created")
    
    # Create issue links (dependencies)
    # NUC-342 blocks NUC-346
    link1 = IssueLink(
        source_issue_id=all_issues[4].id,
        target_issue_id=all_issues[7].id,
        link_type='blocks'
    )
    
    # NUC-336 relates to NUC-343
    link2 = IssueLink(
        source_issue_id=all_issues[6].id,
        target_issue_id=all_issues[8].id,
        link_type='relates_to'
    )
    
    db.session.add_all([link1, link2])
    db.session.commit()
    print("✓ Issue links created")
    
    # Create watchers
    watch1 = IssueWatcher(
        issue_id=all_issues[0].id,
        user_id=user2.id
    )
    
    watch2 = IssueWatcher(
        issue_id=all_issues[4].id,
        user_id=user3.id
    )
    
    db.session.add_all([watch1, watch2])
    db.session.commit()
    print("✓ Watchers created")
    
    print("\n" + "="*50)
    print("✓ Sample data created successfully!")
    print("="*50)
    print("\nProject Details:")
    print(f"  Project: {project.name} ({project.key})")
    print(f"  Team: {team.name}")
    print(f"  Issues: {len(all_issues)}")
    print(f"  Team Members: 4")
    print(f"  Sprint: {sprint.name}")
    print(f"  Epic: {epic.name}")
    print("\nTest Users:")
    print(f"  - admin (admin user)")
    print(f"  - john_doe (developer)")
    print(f"  - jane_smith (developer)")
    print(f"  - bob_wilson (designer)")
    print("\nAll users use password: password123")
    print("\nYou can now login and view the dashboard!")
    print("="*50 + "\n")

if __name__ == '__main__':
    with app.app_context():
        create_sample_data()

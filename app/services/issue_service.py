# app/services/issue_service.py
"""
Issue Service
Handles issue/task management business logic.
"""

from datetime import datetime
from app.utils.security import sanitize_input, log_security_event
from app.utils.validators import (
    validate_required, validate_length, validate_date,
    validate_status, validate_priority, validate_issue_type,
    validate_integer, validate_float, ValidationError
)


class IssueService:
    """Service for handling issue operations."""
    
    VALID_STATUSES = ['open', 'todo', 'in_progress', 'code_review', 
                      'testing', 'ready_deploy', 'done', 'closed', 'reopened']
    
    VALID_PRIORITIES = ['lowest', 'low', 'medium', 'high', 'highest', 'critical']
    
    VALID_TYPES = ['story', 'task', 'bug', 'epic', 'subtask']
    
    @staticmethod
    def create_issue(project_id, title, description=None, issue_type='task',
                    priority='medium', assignee_id=None, reporter_id=None,
                    story_points=None, time_estimate=None, due_date=None,
                    sprint_id=None, epic_id=None, parent_id=None):
        """
        Create a new issue.
        
        Returns:
            tuple: (success: bool, issue: Issue or None, message: str)
        """
        from app.models import Issue, Project, db
        
        try:
            # Validate project exists
            project = Project.query.get(project_id)
            if not project:
                return False, None, 'Project not found'
            
            # Validate inputs
            title = sanitize_input(validate_required(title, 'title'))
            validate_length(title, 'title', min_length=1, max_length=200)
            
            validate_issue_type(issue_type)
            validate_priority(priority)
            
            # Generate issue key
            key = IssueService._generate_issue_key(project_id)
            
            # Parse dates
            if isinstance(due_date, str):
                due_date = validate_date(due_date, 'due_date')
            
            # Validate numeric fields
            if story_points is not None:
                story_points = validate_integer(story_points, 'story_points', min_value=1, max_value=100)
            
            if time_estimate is not None:
                time_estimate = validate_float(time_estimate, 'time_estimate', min_value=0, max_value=1000)
            
            # Get max position for new issues
            max_position = db.session.query(db.func.max(Issue.position)).filter_by(
                project_id=project_id, status='open'
            ).scalar() or 0
            
            # Create issue
            issue = Issue(
                key=key,
                title=title,
                project_id=project_id,
                issue_type=issue_type,
                priority=priority,
                status='open',
                assignee_id=int(assignee_id) if assignee_id else None,
                reporter_id=reporter_id,
                story_points=story_points,
                time_estimate=time_estimate,
                due_date=due_date,
                sprint_id=int(sprint_id) if sprint_id else None,
                epic_id=int(epic_id) if epic_id else None,
                parent_id=int(parent_id) if parent_id else None,
                position=max_position + 1
            )
            
            if description:
                issue.description = sanitize_input(description, allow_html=True)
            
            db.session.add(issue)
            db.session.commit()
            
            log_security_event(
                'ISSUE_CREATED',
                user_id=reporter_id,
                details=f'Created issue: {key} in project {project.key}',
                severity='INFO'
            )
            
            return True, issue, 'Issue created successfully'
            
        except ValidationError as e:
            return False, None, str(e)
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error creating issue: {str(e)}'
    
    @staticmethod
    def update_issue(issue_id, data, updated_by=None):
        """Update issue information."""
        from app.models import Issue, WorkflowTransition, db
        
        try:
            issue = Issue.query.get(issue_id)
            if not issue:
                return False, None, 'Issue not found'
            
            old_status = issue.status
            
            if 'title' in data:
                issue.title = sanitize_input(data['title'])
            
            if 'description' in data:
                issue.description = sanitize_input(data['description'], allow_html=True)
            
            if 'status' in data:
                new_status = data['status']
                validate_status(new_status)
                
                if new_status != old_status:
                    # Record workflow transition
                    transition = WorkflowTransition(
                        issue_id=issue.id,
                        from_status=old_status,
                        to_status=new_status,
                        user_id=updated_by
                    )
                    db.session.add(transition)
                    
                    issue.status = new_status
                    
                    # Set completion time
                    if new_status in ['done', 'closed'] and old_status not in ['done', 'closed']:
                        issue.closed_at = datetime.utcnow()
                    elif new_status not in ['done', 'closed']:
                        issue.closed_at = None
            
            if 'priority' in data:
                validate_priority(data['priority'])
                issue.priority = data['priority']
            
            if 'issue_type' in data:
                validate_issue_type(data['issue_type'])
                issue.issue_type = data['issue_type']
            
            if 'assignee_id' in data:
                issue.assignee_id = int(data['assignee_id']) if data['assignee_id'] else None
            
            if 'story_points' in data:
                issue.story_points = validate_integer(data['story_points'], 'story_points', min_value=1, max_value=100)
            
            if 'time_estimate' in data:
                issue.time_estimate = validate_float(data['time_estimate'], 'time_estimate', min_value=0)
            
            if 'time_spent' in data:
                issue.time_spent = validate_float(data['time_spent'], 'time_spent', min_value=0)
            
            if 'due_date' in data:
                issue.due_date = validate_date(data['due_date'], 'due_date')
            
            if 'sprint_id' in data:
                issue.sprint_id = int(data['sprint_id']) if data['sprint_id'] else None
            
            if 'epic_id' in data:
                issue.epic_id = int(data['epic_id']) if data['epic_id'] else None
            
            issue.updated_at = datetime.utcnow()
            db.session.commit()
            
            log_security_event(
                'ISSUE_UPDATED',
                user_id=updated_by,
                details=f'Updated issue: {issue.key}',
                severity='INFO'
            )
            
            return True, issue, 'Issue updated successfully'
            
        except ValidationError as e:
            return False, None, str(e)
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error updating issue: {str(e)}'
    
    @staticmethod
    def update_status(issue_id, new_status, updated_by=None):
        """Quick status update for drag-and-drop."""
        return IssueService.update_issue(issue_id, {'status': new_status}, updated_by)
    
    @staticmethod
    def delete_issue(issue_id, deleted_by=None):
        """Delete an issue."""
        from app.models import Issue, db
        
        try:
            issue = Issue.query.get(issue_id)
            if not issue:
                return False, 'Issue not found'
            
            issue_key = issue.key
            project_id = issue.project_id
            
            db.session.delete(issue)
            db.session.commit()
            
            log_security_event(
                'ISSUE_DELETED',
                user_id=deleted_by,
                details=f'Deleted issue: {issue_key}',
                severity='WARNING'
            )
            
            return True, 'Issue deleted successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error deleting issue: {str(e)}'
    
    @staticmethod
    def get_issue_by_id(issue_id):
        """Get issue by ID."""
        from app.models import Issue
        return Issue.query.get(issue_id)
    
    @staticmethod
    def get_issue_by_key(key):
        """Get issue by key."""
        from app.models import Issue
        return Issue.query.filter_by(key=key).first()
    
    @staticmethod
    def get_issues_by_project(project_id, filters=None):
        """Get issues for a project with optional filters."""
        from app.models import Issue
        
        query = Issue.query.filter_by(project_id=project_id)
        
        if filters:
            if 'status' in filters and filters['status']:
                query = query.filter_by(status=filters['status'])
            if 'priority' in filters and filters['priority']:
                query = query.filter_by(priority=filters['priority'])
            if 'assignee_id' in filters and filters['assignee_id']:
                query = query.filter_by(assignee_id=int(filters['assignee_id']))
            if 'issue_type' in filters and filters['issue_type']:
                query = query.filter_by(issue_type=filters['issue_type'])
            if 'sprint_id' in filters and filters['sprint_id']:
                query = query.filter_by(sprint_id=int(filters['sprint_id']))
            if 'epic_id' in filters and filters['epic_id']:
                query = query.filter_by(epic_id=int(filters['epic_id']))
        
        return query.order_by(Issue.position).all()
    
    @staticmethod
    def get_issues_grouped_by_status(project_id):
        """Get issues grouped by status for Kanban board."""
        from app.models import Issue
        
        issues = Issue.query.filter_by(project_id=project_id).order_by(Issue.position).all()
        
        grouped = {status: [] for status in IssueService.VALID_STATUSES}
        
        for issue in issues:
            if issue.status in grouped:
                grouped[issue.status].append(issue)
        
        return grouped
    
    @staticmethod
    def add_comment(issue_id, user_id, text):
        """Add a comment to an issue."""
        from app.models import Issue, Comment, db
        
        try:
            issue = Issue.query.get(issue_id)
            if not issue:
                return False, None, 'Issue not found'
            
            text = sanitize_input(validate_required(text, 'text'), allow_html=True)
            
            comment = Comment(
                issue_id=issue_id,
                user_id=user_id
            )
            comment.text = text
            
            db.session.add(comment)
            issue.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True, comment, 'Comment added successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error adding comment: {str(e)}'
    
    @staticmethod
    def link_issues(source_id, target_id, link_type, created_by=None):
        """Create a link between two issues."""
        from app.models import Issue, IssueLink, db
        
        try:
            source = Issue.query.get(source_id)
            target = Issue.query.get(target_id)
            
            if not source or not target:
                return False, None, 'Issue not found'
            
            if source_id == target_id:
                return False, None, 'Cannot link an issue to itself'
            
            valid_link_types = ['blocks', 'is_blocked_by', 'relates_to', 'duplicates', 'clones']
            if link_type not in valid_link_types:
                return False, None, f'Invalid link type. Must be one of: {", ".join(valid_link_types)}'
            
            # Check for existing link
            existing = IssueLink.query.filter_by(
                source_issue_id=source_id,
                target_issue_id=target_id
            ).first()
            
            if existing:
                return False, None, 'Link already exists'
            
            # Check for circular dependency
            if link_type in ['blocks', 'is_blocked_by']:
                reverse = IssueLink.query.filter_by(
                    source_issue_id=target_id,
                    target_issue_id=source_id,
                    link_type='blocks' if link_type == 'is_blocked_by' else 'is_blocked_by'
                ).first()
                if reverse:
                    return False, None, 'Circular dependency detected'
            
            link = IssueLink(
                source_issue_id=source_id,
                target_issue_id=target_id,
                link_type=link_type,
                created_by=created_by
            )
            
            db.session.add(link)
            db.session.commit()
            
            return True, link, 'Link created successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error creating link: {str(e)}'
    
    @staticmethod
    def log_time(issue_id, hours, user_id):
        """Log time spent on an issue."""
        from app.models import Issue, db
        
        try:
            issue = Issue.query.get(issue_id)
            if not issue:
                return False, 'Issue not found'
            
            hours = validate_float(hours, 'hours', min_value=0, max_value=24)
            
            issue.time_spent = (issue.time_spent or 0) + hours
            issue.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True, f'Logged {hours} hours'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error logging time: {str(e)}'
    
    @staticmethod
    def _generate_issue_key(project_id):
        """Generate unique issue key like PROJ-123."""
        from app.models import Issue, Project
        
        project = Project.query.get(project_id)
        prefix = project.key or ''.join([c for c in project.name.upper() if c.isalnum()])[:4]
        
        # Get the last issue number for this project
        last_issue = Issue.query.filter_by(project_id=project_id).order_by(Issue.id.desc()).first()
        
        if last_issue and last_issue.key:
            try:
                number = int(last_issue.key.split('-')[-1]) + 1
            except ValueError:
                number = Issue.query.filter_by(project_id=project_id).count() + 1
        else:
            number = 1
        
        return f"{prefix}-{number}"

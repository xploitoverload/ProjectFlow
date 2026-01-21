# app/services/project_service.py
"""
Project Service
Handles project management business logic.
"""

from datetime import datetime, timedelta
from app.utils.security import sanitize_input, log_security_event
from app.utils.validators import (
    validate_required, validate_length, validate_date,
    validate_date_range, validate_project_status, 
    validate_workflow_type, validate_project_key, ValidationError
)


class ProjectService:
    """Service for handling project operations."""
    
    @staticmethod
    def create_project(name, key=None, description=None, status='Not Started',
                      workflow_type='agile', team_id=None, start_date=None,
                      end_date=None, created_by=None):
        """
        Create a new project.
        
        Returns:
            tuple: (success: bool, project: Project or None, message: str)
        """
        from app.models import Project, db
        
        try:
            # Validate inputs
            name = sanitize_input(validate_required(name, 'name'))
            validate_length(name, 'name', min_length=2, max_length=200)
            
            # Generate key if not provided
            if not key:
                key = ProjectService._generate_project_key(name)
            else:
                key = validate_project_key(key)
            
            # Check for duplicate key
            if Project.query.filter_by(key=key).first():
                return False, None, f'Project key {key} already exists'
            
            validate_project_status(status)
            validate_workflow_type(workflow_type)
            
            # Parse dates
            if isinstance(start_date, str):
                start_date = validate_date(start_date, 'start_date')
            if isinstance(end_date, str):
                end_date = validate_date(end_date, 'end_date')
            
            if start_date and end_date:
                validate_date_range(start_date, end_date)
            
            # Create project
            project = Project(
                name=name,
                key=key,
                status=status,
                workflow_type=workflow_type,
                team_id=int(team_id) if team_id else None,
                start_date=start_date or datetime.utcnow(),
                end_date=end_date,
                created_by=created_by
            )
            
            if description:
                project.description = sanitize_input(description)
            
            db.session.add(project)
            db.session.commit()
            
            # Create default labels for the project
            ProjectService._create_default_labels(project.id)
            
            log_security_event(
                'PROJECT_CREATED',
                user_id=created_by,
                details=f'Created project: {name} ({key})',
                severity='INFO'
            )
            
            return True, project, 'Project created successfully'
            
        except ValidationError as e:
            return False, None, str(e)
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error creating project: {str(e)}'
    
    @staticmethod
    def update_project(project_id, data, updated_by=None):
        """Update project information."""
        from app.models import Project, db
        
        try:
            project = Project.query.get(project_id)
            if not project:
                return False, None, 'Project not found'
            
            old_status = project.status
            
            if 'name' in data:
                project.name = sanitize_input(data['name'])
            
            if 'description' in data:
                project.description = sanitize_input(data['description'])
            
            if 'status' in data:
                validate_project_status(data['status'])
                project.status = data['status']
                
                # Set end date when completed
                if data['status'] == 'Completed' and not project.end_date:
                    project.end_date = datetime.utcnow()
            
            if 'workflow_type' in data:
                validate_workflow_type(data['workflow_type'])
                project.workflow_type = data['workflow_type']
            
            if 'team_id' in data:
                project.team_id = int(data['team_id']) if data['team_id'] else None
            
            if 'start_date' in data:
                project.start_date = validate_date(data['start_date'], 'start_date')
            
            if 'end_date' in data:
                project.end_date = validate_date(data['end_date'], 'end_date')
            
            db.session.commit()
            
            log_security_event(
                'PROJECT_UPDATED',
                user_id=updated_by,
                details=f'Updated project: {project.name}, status: {old_status} -> {project.status}',
                severity='INFO'
            )
            
            return True, project, 'Project updated successfully'
            
        except ValidationError as e:
            return False, None, str(e)
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error updating project: {str(e)}'
    
    @staticmethod
    def delete_project(project_id, deleted_by=None):
        """Delete a project and all related data."""
        from app.models import Project, db
        
        try:
            project = Project.query.get(project_id)
            if not project:
                return False, 'Project not found'
            
            project_name = project.name
            project_key = project.key
            
            # Cascade delete will handle related entities
            db.session.delete(project)
            db.session.commit()
            
            log_security_event(
                'PROJECT_DELETED',
                user_id=deleted_by,
                details=f'Deleted project: {project_name} ({project_key})',
                severity='WARNING'
            )
            
            return True, 'Project deleted successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error deleting project: {str(e)}'
    
    @staticmethod
    def get_project_by_id(project_id):
        """Get project by ID."""
        from app.models import Project
        return Project.query.get(project_id)
    
    @staticmethod
    def get_project_by_key(key):
        """Get project by key."""
        from app.models import Project
        return Project.query.filter_by(key=key).first()
    
    @staticmethod
    def get_all_projects():
        """Get all projects."""
        from app.models import Project
        return Project.query.order_by(Project.created_at.desc()).all()
    
    @staticmethod
    def get_projects_by_team(team_id):
        """Get all projects for a team."""
        from app.models import Project
        return Project.query.filter_by(team_id=team_id).order_by(Project.created_at.desc()).all()
    
    @staticmethod
    def get_projects_by_status(status):
        """Get projects by status."""
        from app.models import Project
        return Project.query.filter_by(status=status).all()
    
    @staticmethod
    def get_user_accessible_projects(user):
        """Get all projects accessible to a user based on role."""
        from app.models import Project
        
        if user.role in ['admin', 'super_admin']:
            return Project.query.all()
        elif user.team_id:
            return Project.query.filter_by(team_id=user.team_id).all()
        else:
            return []
    
    @staticmethod
    def get_project_statistics(project_id):
        """Get comprehensive statistics for a project."""
        from app.models import Project, Issue, ProjectUpdate
        
        project = Project.query.get(project_id)
        if not project:
            return None
        
        issues = Issue.query.filter_by(project_id=project_id).all()
        updates = ProjectUpdate.query.filter_by(project_id=project_id).all()
        
        total_issues = len(issues)
        
        stats = {
            'total_issues': total_issues,
            'by_status': {},
            'by_priority': {},
            'by_type': {},
            'completion_rate': 0,
            'total_hours': sum(u.hours_worked or 0 for u in updates),
            'avg_progress': 0
        }
        
        # Count by status
        for issue in issues:
            status = issue.status
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            priority = issue.priority
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            issue_type = issue.issue_type
            stats['by_type'][issue_type] = stats['by_type'].get(issue_type, 0) + 1
        
        # Calculate completion rate
        completed = stats['by_status'].get('done', 0) + stats['by_status'].get('closed', 0)
        if total_issues > 0:
            stats['completion_rate'] = int((completed / total_issues) * 100)
        
        # Average progress from updates
        if updates:
            stats['avg_progress'] = sum(u.progress_percentage or 0 for u in updates) / len(updates)
        
        return stats
    
    @staticmethod
    def get_gantt_data(projects=None):
        """Get Gantt chart data for projects."""
        from app.models import Project
        
        if projects is None:
            projects = Project.query.filter(Project.start_date.isnot(None)).all()
        
        gantt_data = []
        for project in projects:
            if project.start_date:
                end_date = project.end_date or (project.start_date + timedelta(days=30))
                
                # Calculate progress based on status
                progress_map = {
                    'Not Started': 0,
                    'In Progress': 50,
                    'Active': 50,
                    'At Risk': 60,
                    'On Hold': 25,
                    'Blocked': 30,
                    'Completed': 100
                }
                
                gantt_data.append({
                    'id': project.id,
                    'name': project.name,
                    'key': project.key,
                    'start': project.start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d'),
                    'status': project.status,
                    'team': project.team.name if project.team else 'Unassigned',
                    'progress': progress_map.get(project.status, 0)
                })
        
        return gantt_data
    
    @staticmethod
    def _generate_project_key(name):
        """Generate a project key from name."""
        # Take first letters of words, uppercase, max 10 chars
        words = name.upper().split()
        if len(words) >= 2:
            key = ''.join(w[0] for w in words[:4])
        else:
            key = ''.join(c for c in name.upper() if c.isalnum())[:4]
        
        # Ensure minimum length
        if len(key) < 2:
            key = name.upper()[:4]
        
        return key[:10]
    
    @staticmethod
    def _create_default_labels(project_id):
        """Create default labels for a new project."""
        from app.models import Label, db
        
        default_labels = [
            ('BUG', '#e74c3c'),
            ('FEATURE', '#27ae60'),
            ('ENHANCEMENT', '#3498db'),
            ('DOCUMENTATION', '#9b59b6'),
            ('URGENT', '#e91e63'),
            ('LOW-PRIORITY', '#95a5a6')
        ]
        
        for name, color in default_labels:
            label = Label(
                name=name,
                color=color,
                project_id=project_id
            )
            db.session.add(label)
        
        db.session.commit()

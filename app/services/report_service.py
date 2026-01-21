# app/services/report_service.py
"""
Report Service
Handles reporting and analytics business logic.
"""

from datetime import datetime, timedelta
from app.utils.security import sanitize_input, log_security_event
from app.utils.validators import (
    validate_required, validate_integer, validate_float,
    validate_enum, ValidationError
)


class ReportService:
    """Service for handling reports and analytics."""
    
    VALID_STATUSES = ['on_track', 'at_risk', 'blocked']
    VALID_PERIODS = ['daily', 'weekly', 'monthly']
    
    @staticmethod
    def create_status_update(project_id, user_id, description, status='on_track',
                            progress=0, hours_worked=0, blockers=None,
                            notes=None, team_members=None, completion_days=None,
                            reporting_period='daily'):
        """
        Create a new status update/report.
        
        Returns:
            tuple: (success: bool, update: ProjectUpdate or None, message: str)
        """
        from app.models import Project, ProjectUpdate, db
        
        try:
            # Validate project exists
            project = Project.query.get(project_id)
            if not project:
                return False, None, 'Project not found'
            
            # Validate inputs
            description = sanitize_input(validate_required(description, 'description'))
            status = validate_enum(status, 'status', ReportService.VALID_STATUSES)
            progress = validate_integer(progress, 'progress', min_value=0, max_value=100)
            hours_worked = validate_float(hours_worked, 'hours_worked', min_value=0, max_value=24)
            
            if reporting_period:
                reporting_period = validate_enum(reporting_period, 'reporting_period', 
                                                 ReportService.VALID_PERIODS)
            
            # Create update
            update = ProjectUpdate(
                project_id=project_id,
                user_id=user_id,
                status=status,
                progress_percentage=progress,
                hours_worked=hours_worked,
                reporting_period=reporting_period or 'daily',
                date=datetime.utcnow()
            )
            
            update.update_text = description
            
            if blockers:
                update.blockers = sanitize_input(blockers)
            
            if notes:
                update.completion_notes = sanitize_input(notes)
            
            if team_members:
                update.team_members_count = validate_integer(team_members, 'team_members', min_value=0)
            
            if completion_days:
                update.estimated_completion_days = validate_float(completion_days, 'completion_days', min_value=0)
            
            db.session.add(update)
            
            # Update project status based on report
            if status == 'blocked':
                project.status = 'Blocked'
            elif status == 'at_risk':
                project.status = 'At Risk'
            elif status == 'on_track' and project.status in ['Blocked', 'At Risk']:
                project.status = 'Active'
            
            db.session.commit()
            
            log_security_event(
                'STATUS_UPDATE_CREATED',
                user_id=user_id,
                details=f'Created status update for project {project.name}: {status}',
                severity='INFO'
            )
            
            return True, update, 'Status update created successfully'
            
        except ValidationError as e:
            return False, None, str(e)
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error creating status update: {str(e)}'
    
    @staticmethod
    def get_project_updates(project_id, limit=50, offset=0):
        """Get status updates for a project."""
        from app.models import ProjectUpdate
        
        return ProjectUpdate.query.filter_by(project_id=project_id)\
            .order_by(ProjectUpdate.date.desc())\
            .limit(limit).offset(offset).all()
    
    @staticmethod
    def get_user_updates(user_id, filter_type='all', status_filter=None, 
                        search_query=None, sort_by='date'):
        """Get status updates for a specific user."""
        from app.models import ProjectUpdate, Project
        
        # Calculate date range
        now = datetime.utcnow()
        date_ranges = {
            'daily': now - timedelta(days=1),
            'weekly': now - timedelta(weeks=1),
            'monthly': now - timedelta(days=30),
            'all': datetime.min
        }
        
        start_date = date_ranges.get(filter_type, datetime.min)
        
        # Query updates
        updates = ProjectUpdate.query.filter(
            ProjectUpdate.user_id == user_id,
            ProjectUpdate.date >= start_date
        ).all()
        
        # Apply search filter
        if search_query:
            search_lower = search_query.lower()
            filtered = []
            for u in updates:
                if hasattr(u, 'project') and u.project:
                    if search_lower in u.project.name.lower():
                        filtered.append(u)
            updates = filtered
        
        # Apply status filter
        if status_filter and status_filter in ReportService.VALID_STATUSES:
            updates = [u for u in updates if u.status == status_filter]
        
        # Apply sorting
        if sort_by == 'progress':
            updates.sort(key=lambda u: u.progress_percentage or 0, reverse=True)
        elif sort_by == 'status':
            status_order = {'blocked': 0, 'at_risk': 1, 'on_track': 2}
            updates.sort(key=lambda u: status_order.get(u.status, 3))
        else:
            updates.sort(key=lambda u: u.date, reverse=True)
        
        return updates
    
    @staticmethod
    def get_user_statistics(user_id, filter_type='all'):
        """Get statistics for a user's updates."""
        from app.models import ProjectUpdate
        
        now = datetime.utcnow()
        date_ranges = {
            'daily': now - timedelta(days=1),
            'weekly': now - timedelta(weeks=1),
            'monthly': now - timedelta(days=30),
            'all': datetime.min
        }
        
        start_date = date_ranges.get(filter_type, datetime.min)
        
        updates = ProjectUpdate.query.filter(
            ProjectUpdate.user_id == user_id,
            ProjectUpdate.date >= start_date
        ).all()
        
        if not updates:
            return {
                'total': 0,
                'on_track': 0,
                'at_risk': 0,
                'blocked': 0,
                'avg_progress': 0,
                'total_hours': 0
            }
        
        return {
            'total': len(updates),
            'on_track': sum(1 for u in updates if u.status == 'on_track'),
            'at_risk': sum(1 for u in updates if u.status == 'at_risk'),
            'blocked': sum(1 for u in updates if u.status == 'blocked'),
            'avg_progress': int(sum(u.progress_percentage or 0 for u in updates) / len(updates)),
            'total_hours': sum(u.hours_worked or 0 for u in updates)
        }
    
    @staticmethod
    def get_project_analytics(project_id, days=30):
        """Get comprehensive analytics for a project."""
        from app.models import Project, Issue, ProjectUpdate
        
        project = Project.query.get(project_id)
        if not project:
            return None
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get issues
        issues = Issue.query.filter_by(project_id=project_id).all()
        
        # Get updates in date range
        updates = ProjectUpdate.query.filter(
            ProjectUpdate.project_id == project_id,
            ProjectUpdate.date >= start_date
        ).order_by(ProjectUpdate.date).all()
        
        # Calculate velocity (issues completed per week)
        completed_issues = [i for i in issues if i.closed_at and i.closed_at >= start_date]
        weeks = days / 7
        velocity = len(completed_issues) / weeks if weeks > 0 else 0
        
        # Calculate burn-down data
        burn_down = ReportService._calculate_burndown(issues, days)
        
        # Calculate cumulative flow
        cumulative_flow = ReportService._calculate_cumulative_flow(issues, days)
        
        return {
            'project': project,
            'total_issues': len(issues),
            'completed_issues': len(completed_issues),
            'velocity': round(velocity, 1),
            'updates': updates,
            'burn_down': burn_down,
            'cumulative_flow': cumulative_flow,
            'avg_cycle_time': ReportService._calculate_avg_cycle_time(completed_issues),
            'status_distribution': ReportService._calculate_status_distribution(issues)
        }
    
    @staticmethod
    def get_team_analytics(team_id, days=30):
        """Get analytics for a team across all projects."""
        from app.models import Project, Issue, User, ProjectUpdate
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get team projects
        projects = Project.query.filter_by(team_id=team_id).all()
        project_ids = [p.id for p in projects]
        
        # Get team members
        members = User.query.filter_by(team_id=team_id).all()
        
        # Get all issues for team projects
        issues = Issue.query.filter(Issue.project_id.in_(project_ids)).all()
        
        # Calculate per-member statistics
        member_stats = []
        for member in members:
            member_issues = [i for i in issues if i.assignee_id == member.id]
            member_completed = [i for i in member_issues if i.status in ['done', 'closed']]
            
            member_updates = ProjectUpdate.query.filter(
                ProjectUpdate.user_id == member.id,
                ProjectUpdate.date >= start_date
            ).all()
            
            member_stats.append({
                'user': member,
                'total_issues': len(member_issues),
                'completed_issues': len(member_completed),
                'total_hours': sum(u.hours_worked or 0 for u in member_updates),
                'avg_progress': (sum(u.progress_percentage or 0 for u in member_updates) / 
                               len(member_updates)) if member_updates else 0
            })
        
        return {
            'projects': projects,
            'total_issues': len(issues),
            'member_stats': member_stats,
            'overall_completion': (sum(1 for i in issues if i.status in ['done', 'closed']) / 
                                  len(issues) * 100) if issues else 0
        }
    
    @staticmethod
    def _calculate_burndown(issues, days):
        """Calculate burndown chart data."""
        from datetime import date
        
        data = []
        total = len(issues)
        
        for i in range(days, -1, -1):
            day = datetime.utcnow() - timedelta(days=i)
            remaining = sum(1 for issue in issues 
                          if not issue.closed_at or issue.closed_at > day)
            data.append({
                'date': day.strftime('%Y-%m-%d'),
                'remaining': remaining,
                'ideal': total - (total * (days - i) / days) if days > 0 else 0
            })
        
        return data
    
    @staticmethod
    def _calculate_cumulative_flow(issues, days):
        """Calculate cumulative flow diagram data."""
        statuses = ['open', 'todo', 'in_progress', 'code_review', 
                   'testing', 'ready_deploy', 'done', 'closed']
        
        # Simplified - just return current status distribution
        return {status: sum(1 for i in issues if i.status == status) for status in statuses}
    
    @staticmethod
    def _calculate_avg_cycle_time(completed_issues):
        """Calculate average cycle time for completed issues."""
        if not completed_issues:
            return 0
        
        cycle_times = []
        for issue in completed_issues:
            if issue.closed_at and issue.created_at:
                cycle_time = (issue.closed_at - issue.created_at).days
                cycle_times.append(cycle_time)
        
        return round(sum(cycle_times) / len(cycle_times), 1) if cycle_times else 0
    
    @staticmethod
    def _calculate_status_distribution(issues):
        """Calculate status distribution for issues."""
        distribution = {}
        total = len(issues)
        
        for issue in issues:
            status = issue.status
            distribution[status] = distribution.get(status, 0) + 1
        
        # Convert to percentages
        return {status: round(count / total * 100, 1) if total > 0 else 0 
                for status, count in distribution.items()}

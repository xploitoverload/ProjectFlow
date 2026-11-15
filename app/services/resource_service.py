"""
Resource & Team Capacity Planning Service
Handles workload distribution, weekly capacity limits, utilization percentages,
and over-allocation detection across projects and teams.
"""

from datetime import datetime, date, timedelta
from app.models import db, User, Team, Project, Issue


def to_date(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        try:
            return datetime.strptime(val[:10], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
    return None


class ResourceService:
    """Enterprise resource capacity and workload planning engine."""

    HOURS_PER_WORKING_DAY = 8.0
    DEFAULT_WEEKLY_HOURS = 40.0
    DEFAULT_HOURS_PER_STORY_POINT = 8.0
    DEFAULT_TASK_ESTIMATE_HOURS = 8.0

    @classmethod
    def calculate_task_hours(cls, issue):
        """Calculate estimated hours for an issue using time_estimate, story_points, or default."""
        if issue.time_estimate and issue.time_estimate > 0:
            return float(issue.time_estimate)
        if issue.story_points and issue.story_points > 0:
            return float(issue.story_points) * cls.DEFAULT_HOURS_PER_STORY_POINT
        return cls.DEFAULT_TASK_ESTIMATE_HOURS

    @classmethod
    def calculate_window_capacity_hours(cls, start_d, end_d, hours_per_week=40.0):
        """
        Calculate available working capacity in hours between start_d and end_d inclusive.
        Assumes Monday-Friday working week.
        """
        s = to_date(start_d)
        e = to_date(end_d)
        if not s or not e or s > e:
            return hours_per_week
        
        # Count working days (Mon=0 .. Fri=4)
        working_days = 0
        curr = s
        while curr <= e:
            if curr.weekday() < 5:
                working_days += 1
            curr += timedelta(days=1)
            
        daily_hours = hours_per_week / 5.0
        return max(daily_hours, working_days * daily_hours)

    @classmethod
    def get_user_workload(cls, user_id, start_date=None, end_date=None, project_id=None):
        """
        Calculate workload, capacity, and allocation status for a specific user.
        """
        user = User.query.get(user_id)
        if not user:
            return None, 'User not found'

        s_date = to_date(start_date) or date.today()
        e_date = to_date(end_date) or (s_date + timedelta(days=6))  # Default 1 week window

        weekly_hours = getattr(user, 'weekly_capacity_hours', None) or cls.DEFAULT_WEEKLY_HOURS
        capacity_hours = cls.calculate_window_capacity_hours(s_date, e_date, weekly_hours)

        query = Issue.query.filter(
            Issue.assignee_id == user_id,
            Issue.status != 'done'
        )
        if project_id:
            query = query.filter(Issue.project_id == project_id)

        all_open_issues = query.all()
        
        active_issues = []
        total_estimated = 0.0
        total_spent = 0.0

        for iss in all_open_issues:
            iss_start = to_date(iss.start_date) or s_date
            iss_due = to_date(iss.due_date) or (iss_start + timedelta(days=4))
            
            # Check overlap: (iss_start <= e_date) and (iss_due >= s_date)
            if iss_start <= e_date and iss_due >= s_date:
                est_hrs = cls.calculate_task_hours(iss)
                spent_hrs = float(iss.time_spent or 0.0)
                rem_hrs = max(0.0, est_hrs - spent_hrs)

                active_issues.append({
                    'id': iss.id,
                    'key': iss.key,
                    'title': iss.title,
                    'status': iss.status,
                    'priority': iss.priority,
                    'project_id': iss.project_id,
                    'start_date': iss_start.isoformat(),
                    'due_date': iss_due.isoformat(),
                    'time_estimate': est_hrs,
                    'time_spent': spent_hrs,
                    'remaining_hours': rem_hrs,
                    'story_points': iss.story_points
                })
                total_estimated += est_hrs
                total_spent += spent_hrs

        total_remaining = max(0.0, total_estimated - total_spent)
        utilization_pct = round((total_remaining / capacity_hours) * 100.0, 1) if capacity_hours > 0 else 0.0

        if utilization_pct > 100.0:
            status = 'over_allocated'
        elif utilization_pct >= 80.0:
            status = 'high_capacity'
        elif utilization_pct >= 30.0:
            status = 'optimal'
        else:
            status = 'under_utilized'

        workload = {
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'department': user.department,
                'avatar_color': user.avatar_color
            },
            'window': {
                'start_date': s_date.isoformat(),
                'end_date': e_date.isoformat(),
                'days': (e_date - s_date).days + 1
            },
            'capacity_hours': round(capacity_hours, 1),
            'allocated_hours': round(total_estimated, 1),
            'spent_hours': round(total_spent, 1),
            'remaining_hours': round(total_remaining, 1),
            'utilization_percentage': utilization_pct,
            'allocation_status': status,
            'is_over_allocated': status == 'over_allocated',
            'assigned_tasks_count': len(active_issues),
            'tasks': active_issues
        }
        return workload, None

    @classmethod
    def get_team_capacity(cls, team_id, start_date=None, end_date=None):
        """
        Calculate aggregate team capacity, individual workloads, and over-allocation risks.
        """
        team = Team.query.get(team_id)
        if not team:
            return None, 'Team not found'

        s_date = to_date(start_date) or date.today()
        e_date = to_date(end_date) or (s_date + timedelta(days=6))

        members = User.query.filter_by(team_id=team_id, is_active=True).all()
        
        member_workloads = []
        total_team_capacity = 0.0
        total_team_allocated = 0.0
        total_team_remaining = 0.0
        over_allocated_cnt = 0

        for member in members:
            wl, _ = cls.get_user_workload(member.id, start_date=s_date, end_date=e_date)
            if wl:
                member_workloads.append(wl)
                total_team_capacity += wl['capacity_hours']
                total_team_allocated += wl['allocated_hours']
                total_team_remaining += wl['remaining_hours']
                if wl['is_over_allocated']:
                    over_allocated_cnt += 1

        team_utilization = round((total_team_remaining / total_team_capacity) * 100.0, 1) if total_team_capacity > 0 else 0.0

        return {
            'team': {
                'id': team.id,
                'name': team.name,
                'department': team.department,
                'color': team.color,
                'members_count': len(members)
            },
            'window': {
                'start_date': s_date.isoformat(),
                'end_date': e_date.isoformat()
            },
            'total_capacity_hours': round(total_team_capacity, 1),
            'total_allocated_hours': round(total_team_allocated, 1),
            'total_remaining_hours': round(total_team_remaining, 1),
            'team_utilization_percentage': team_utilization,
            'over_allocated_members_count': over_allocated_cnt,
            'members': member_workloads
        }, None

    @classmethod
    def get_project_resource_utilization(cls, project_id, start_date=None, end_date=None):
        """
        Analyze resource allocation across all contributors to a project.
        """
        project = Project.query.get(project_id)
        if not project:
            return None, 'Project not found'

        s_date = to_date(start_date) or date.today()
        e_date = to_date(end_date) or (s_date + timedelta(days=13)) # Default 2-week view

        open_issues = Issue.query.filter_by(project_id=project_id).filter(Issue.status != 'done').all()
        
        unassigned_issues = []
        assigned_user_ids = set()

        for iss in open_issues:
            if iss.assignee_id:
                assigned_user_ids.add(iss.assignee_id)
            else:
                unassigned_issues.append({
                    'id': iss.id,
                    'key': iss.key,
                    'title': iss.title,
                    'estimated_hours': cls.calculate_task_hours(iss),
                    'priority': iss.priority
                })

        resources = []
        total_project_hours = 0.0
        over_allocated_cnt = 0

        for uid in assigned_user_ids:
            wl, _ = cls.get_user_workload(uid, start_date=s_date, end_date=e_date, project_id=project_id)
            if wl:
                resources.append(wl)
                total_project_hours += wl['remaining_hours']
                if wl['is_over_allocated']:
                    over_allocated_cnt += 1

        unassigned_hours = sum(iss['estimated_hours'] for iss in unassigned_issues)

        return {
            'project': {
                'id': project.id,
                'name': project.name,
                'key': project.key
            },
            'window': {
                'start_date': s_date.isoformat(),
                'end_date': e_date.isoformat()
            },
            'total_active_resources': len(resources),
            'over_allocated_resources_count': over_allocated_cnt,
            'total_allocated_hours': round(total_project_hours, 1),
            'unassigned_tasks_count': len(unassigned_issues),
            'unassigned_hours': round(unassigned_hours, 1),
            'resources': resources,
            'unassigned_tasks': unassigned_issues
        }, None

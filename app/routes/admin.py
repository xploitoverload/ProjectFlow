# app/routes/admin.py
"""
Admin Routes
Handles user management, team management, and admin dashboard.
Requires admin or super_admin role for all operations.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from app.middleware import admin_required
from app.services import UserService, ProjectService, AuditService
from app.utils.security import validate_csrf_token, sanitize_input
from app.security.audit import log_security_event, log_admin_action

admin_bp = Blueprint('admin', __name__)


def verify_admin_privilege():
    """
    Additional check to prevent privilege escalation.
    Verifies that the current session truly has admin privileges.
    """
    from app.models import User
    user = User.query.get(session.get('user_id'))
    if not user or user.role not in ['admin', 'super_admin']:
        log_security_event(
            'PRIVILEGE_ESCALATION_ATTEMPT',
            user_id=session.get('user_id'),
            details='Attempted access to admin route without admin role',
            severity='CRITICAL'
        )
        abort(403)
    return user


@admin_bp.route('/')
@admin_required
def admin_dashboard():
    """Admin dashboard with overview."""
    from app.models import User, Team, Project, Issue
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Double-check admin privilege (defense in depth)
    admin_user = verify_admin_privilege()
    
    # Get counts
    user_count = User.query.count()
    team_count = Team.query.count()
    project_count = Project.query.count()
    issue_count = Issue.query.count()
    
    # Get online users (active in last 5 minutes)
    five_mins_ago = datetime.utcnow() - timedelta(minutes=5)
    online_users_count = User.query.filter(User.last_activity >= five_mins_ago).count() if hasattr(User, 'last_activity') else 0
    
    # Get active users (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    active_users_count = User.query.filter(User.last_login >= yesterday).count() if hasattr(User, 'last_login') else 0
    
    # Get project status breakdown
    project_status = {}
    projects = Project.query.all()
    for project in projects:
        status = project.status or 'Unknown'
        project_status[status] = project_status.get(status, 0) + 1
    
    # Get recent projects
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all() if hasattr(Project, 'created_at') else []
    
    # Get recent users with activity status
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
    # Get online users list
    online_users = User.query.filter(User.last_activity >= five_mins_ago).order_by(User.last_activity.desc()).all() if hasattr(User, 'last_activity') else []
    
    # Get users and teams for context
    users = User.query.all()
    teams = Team.query.all()
    
    # Get recent security events
    security_events = AuditService.get_security_events(hours=24)
    
    # Get suspicious activity
    suspicious = AuditService.get_suspicious_activity()
    
    # Get audit statistics
    audit_stats = AuditService.get_statistics(days=7)
    
    log_admin_action(
        session.get('user_id'),
        'ADMIN_DASHBOARD_ACCESS',
        {'ip': request.remote_addr}
    )
    
    return render_template('admin/dashboard.html',
                          user_count=user_count,
                          team_count=team_count,
                          project_count=project_count,
                          issue_count=issue_count,
                          total_issues=issue_count,
                          active_users_count=active_users_count,
                          online_users_count=online_users_count,
                          online_users=online_users,
                          project_status=project_status,
                          projects=recent_projects,
                          recent_projects=recent_projects,
                          recent_users=recent_users,
                          users=users,
                          teams=teams,
                          security_events=security_events[:10],
                          suspicious=suspicious,
                          audit_stats=audit_stats)


@admin_bp.route('/users')
@admin_required
def admin_users():
    """User management page."""
    from app.models import User, Team
    
    users = User.query.all()
    teams = Team.query.all()
    
    return render_template('admin/users.html', users=users, teams=teams)


@admin_bp.route('/user/add', methods=['POST'])
@admin_required
def add_user():
    """Add a new user."""
    # CSRF is validated automatically by Flask-WTF
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'employee')
    team_id = request.form.get('team_id')
    
    success, user, message = UserService.create_user(
        username=username,
        email=email,
        password=password,
        role=role,
        team_id=team_id,
        created_by=session.get('user_id')
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/user/<int:user_id>/edit', methods=['POST'])
@admin_required
def edit_user(user_id):
    """Edit user information."""
    # CSRF validated by Flask-WTF
    data = {
        'email': request.form.get('email', '').strip(),
        'role': request.form.get('role'),
        'team_id': request.form.get('team_id')
    }
    
    success, user, message = UserService.update_user(
        user_id=user_id,
        data=data,
        updated_by=session.get('user_id')
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user."""
    # CSRF validated by Flask-WTF
    success, message = UserService.delete_user(
        user_id=user_id,
        deleted_by=session.get('user_id')
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/user/<int:user_id>/unlock', methods=['POST'])
@admin_required
def unlock_user(user_id):
    """Unlock a locked user account."""
    # CSRF validated by Flask-WTF
    success, message = UserService.unlock_user(
        user_id=user_id,
        unlocked_by=session.get('user_id')
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/teams')
@admin_required
def admin_teams():
    """Team management page."""
    from app.models import Team, Project
    
    teams = Team.query.all()
    projects = Project.query.all()
    return render_template('admin/teams.html', teams=teams, projects=projects)


@admin_bp.route('/team/add', methods=['POST'])
@admin_required
def add_team():
    """Add a new team with type and project assignments."""
    from app.models import Team, Project, db
    
    # CSRF validated by Flask-WTF
    name = sanitize_input(request.form.get('name', '').strip())
    description = sanitize_input(request.form.get('description', '').strip())
    team_type = sanitize_input(request.form.get('team_type', 'general').strip())
    color = request.form.get('color', '#6366f1')
    project_ids = request.form.getlist('project_ids')
    
    if not name:
        flash('Team name is required', 'error')
        return redirect(url_for('admin.admin_teams'))
    
    team = Team(
        name=name, 
        team_type=team_type,
        is_core_team=False  # Project teams are not core teams
    )
    team.description = description
    team.color = color
    
    # Assign projects to team (many-to-many)
    if project_ids:
        for pid in project_ids:
            try:
                project = Project.query.get(int(pid))
                if project:
                    team.assigned_projects.append(project)
            except (ValueError, TypeError):
                pass
    
    db.session.add(team)
    db.session.commit()
    
    AuditService.log_event(
        'TEAM_CREATED',
        user_id=session.get('user_id'),
        details=f'Created team: {name} (Type: {team_type})',
        category='DATA_MODIFICATION'
    )
    
    flash('Team created successfully', 'success')
    return redirect(url_for('admin.admin_teams'))


@admin_bp.route('/team/<int:team_id>/edit', methods=['POST'])
@admin_required
def edit_team(team_id):
    """Edit team information."""
    from app.models import Team, db
    
    # CSRF validated by Flask-WTF
    team = Team.query.get_or_404(team_id)
    
    name = sanitize_input(request.form.get('name', '').strip())
    description = sanitize_input(request.form.get('description', '').strip())
    
    if not name:
        flash('Team name is required', 'error')
        return redirect(url_for('admin.admin_teams'))
    
    team.name = name
    team.description = description
    
    db.session.commit()
    
    AuditService.log_event(
        'TEAM_UPDATED',
        user_id=session.get('user_id'),
        details=f'Updated team: {name}',
        category='DATA_MODIFICATION'
    )
    
    flash('Team updated successfully', 'success')
    return redirect(url_for('admin.admin_teams'))


@admin_bp.route('/team/<int:team_id>/delete', methods=['POST'])
@admin_required
def delete_team(team_id):
    """Delete a team."""
    from app.models import Team, db
    
    # CSRF validated by Flask-WTF
    team = Team.query.get_or_404(team_id)
    team_name = team.name
    
    db.session.delete(team)
    db.session.commit()
    
    AuditService.log_event(
        'TEAM_DELETED',
        user_id=session.get('user_id'),
        details=f'Deleted team: {team_name}',
        category='DATA_MODIFICATION',
        severity='WARNING'
    )
    
    flash('Team deleted successfully', 'success')
    return redirect(url_for('admin.admin_teams'))


@admin_bp.route('/team/<int:team_id>')
@admin_required
def team_detail(team_id):
    """Team detail page with member management."""
    from app.models import Team, User, Project
    
    team = Team.query.get_or_404(team_id)
    # Get all users not in this team for adding
    available_users = User.query.filter(
        (User.team_id != team_id) | (User.team_id == None)
    ).all()
    # Get team's assigned projects
    assigned_projects = team.assigned_projects.all() if team.assigned_projects else []
    assigned_project_ids = [p.id for p in assigned_projects]
    # Get all projects for assignment dropdown
    all_projects = Project.query.all()
    
    return render_template('admin/team_detail.html', 
                          team=team, 
                          available_users=available_users,
                          projects=assigned_projects,
                          all_projects=all_projects,
                          assigned_project_ids=assigned_project_ids)


@admin_bp.route('/team/<int:team_id>/add-member', methods=['POST'])
@admin_required
def add_team_member(team_id):
    """Add a member to a team."""
    from app.models import Team, User, db
    
    team = Team.query.get_or_404(team_id)
    user_id = request.form.get('user_id')
    
    if not user_id:
        flash('Please select a user to add', 'error')
        return redirect(url_for('admin.team_detail', team_id=team_id))
    
    user = User.query.get(int(user_id))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.team_detail', team_id=team_id))
    
    # Assign user to team
    user.team_id = team_id
    db.session.commit()
    
    AuditService.log_event(
        'TEAM_MEMBER_ADDED',
        user_id=session.get('user_id'),
        details=f'Added {user.username} to team: {team.name}',
        category='DATA_MODIFICATION'
    )
    
    flash(f'{user.username} added to team successfully', 'success')
    return redirect(url_for('admin.team_detail', team_id=team_id))


@admin_bp.route('/team/<int:team_id>/remove-member/<int:user_id>', methods=['POST'])
@admin_required
def remove_team_member(team_id, user_id):
    """Remove a member from a team."""
    from app.models import Team, User, db
    
    team = Team.query.get_or_404(team_id)
    user = User.query.get_or_404(user_id)
    
    if user.team_id != team_id:
        flash('User is not a member of this team', 'error')
        return redirect(url_for('admin.team_detail', team_id=team_id))
    
    username = user.username
    user.team_id = None
    db.session.commit()
    
    AuditService.log_event(
        'TEAM_MEMBER_REMOVED',
        user_id=session.get('user_id'),
        details=f'Removed {username} from team: {team.name}',
        category='DATA_MODIFICATION'
    )
    
    flash(f'{username} removed from team', 'success')
    return redirect(url_for('admin.team_detail', team_id=team_id))


@admin_bp.route('/team/<int:team_id>/assign-project', methods=['POST'])
@admin_required
def assign_project_to_team(team_id):
    """Assign a project to a team."""
    from app.models import Team, Project, db
    
    team = Team.query.get_or_404(team_id)
    project_id = request.form.get('project_id')
    
    if not project_id:
        flash('Please select a project', 'error')
        return redirect(url_for('admin.team_detail', team_id=team_id))
    
    project = Project.query.get(int(project_id))
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('admin.team_detail', team_id=team_id))
    
    if project not in team.assigned_projects.all():
        team.assigned_projects.append(project)
        db.session.commit()
        flash(f'Project "{project.name}" assigned to team', 'success')
    else:
        flash('Project is already assigned to this team', 'info')
    
    return redirect(url_for('admin.team_detail', team_id=team_id))


@admin_bp.route('/team/<int:team_id>/unassign-project/<int:project_id>', methods=['POST'])
@admin_required
def unassign_project_from_team(team_id, project_id):
    """Remove a project from a team."""
    from app.models import Team, Project, db
    
    team = Team.query.get_or_404(team_id)
    project = Project.query.get_or_404(project_id)
    
    if project in team.assigned_projects.all():
        team.assigned_projects.remove(project)
        db.session.commit()
        flash(f'Project "{project.name}" removed from team', 'success')
    else:
        flash('Project is not assigned to this team', 'error')
    
    return redirect(url_for('admin.team_detail', team_id=team_id))


@admin_bp.route('/projects')
@admin_required
def admin_projects():
    """Project management page."""
    from app.models import Project, Team, User
    
    projects = Project.query.all()
    teams = Team.query.all()
    users = User.query.filter(User.is_active == True).all()
    
    return render_template('admin/projects.html', projects=projects, teams=teams, users=users)


@admin_bp.route('/project/add', methods=['POST'])
@admin_required
def add_project():
    """Add a new project."""
    # CSRF validated by Flask-WTF
    name = request.form.get('name', '').strip()
    key = request.form.get('key', '').strip()
    description = request.form.get('description', '').strip()
    status = request.form.get('status', 'Not Started')
    workflow_type = request.form.get('workflow_type', 'agile')
    team_ids = request.form.getlist('team_ids')  # Multi-select for teams
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    lead_id = request.form.get('lead_id')
    
    success, project, message = ProjectService.create_project(
        name=name,
        key=key if key else None,
        description=description,
        status=status,
        workflow_type=workflow_type,
        team_id=None,  # Keep for backward compatibility
        start_date=start_date,
        end_date=end_date,
        created_by=session.get('user_id'),
        lead_id=lead_id if lead_id else None
    )
    
    # Handle many-to-many team assignment
    if success and project and team_ids:
        from app.models import Team, db
        for tid in team_ids:
            team = Team.query.get(int(tid))
            if team:
                project.teams.append(team)
        db.session.commit()
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_projects'))


@admin_bp.route('/project/<int:project_id>/edit', methods=['POST'])
@admin_required
def edit_project(project_id):
    """Edit project information."""
    # CSRF validated by Flask-WTF
    name = request.form.get('name', '').strip()
    key = request.form.get('key', '').strip()
    description = request.form.get('description', '').strip()
    status = request.form.get('status')
    workflow_type = request.form.get('workflow_type')
    team_ids = request.form.getlist('team_ids')  # Multi-select for teams
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    lead_id = request.form.get('lead_id')
    
    success, project, message = ProjectService.update_project(
        project_id=project_id,
        data={
            'name': name,
            'key': key if key else None,
            'description': description,
            'status': status,
            'workflow_type': workflow_type,
            'team_id': None,  # Keep for backward compatibility
            'start_date': start_date,
            'end_date': end_date,
            'lead_id': lead_id if lead_id else None
        },
        updated_by=session.get('user_id')
    )
    
    # Handle many-to-many team assignment
    if success and project:
        from app.models import Team, db
        # Clear existing team assignments and reassign
        project.teams.clear()
        if team_ids:
            for tid in team_ids:
                team = Team.query.get(int(tid))
                if team:
                    project.teams.append(team)
        db.session.commit()
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_projects'))


@admin_bp.route('/project/<int:project_id>/update_status', methods=['POST'])
@admin_required
def update_project_status(project_id):
    """Update project status."""
    # CSRF validated by Flask-WTF
    status = request.form.get('status')
    
    success, project, message = ProjectService.update_project(
        project_id=project_id,
        data={'status': status},
        updated_by=session.get('user_id')
    )
    
    if success:
        flash('Project status updated', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_projects'))


@admin_bp.route('/project/<int:project_id>/delete', methods=['POST'])
@admin_required
def delete_project(project_id):
    """Delete a project."""
    # CSRF validated by Flask-WTF
    success, message = ProjectService.delete_project(
        project_id=project_id,
        deleted_by=session.get('user_id')
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_projects'))


@admin_bp.route('/audit-logs')
@admin_required
def audit_logs():
    """View audit logs."""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    logs = AuditService.get_recent_events(limit=per_page * page)
    
    return render_template('admin/audit_logs.html', 
                          logs=logs[(page-1)*per_page:page*per_page],
                          page=page)


@admin_bp.route('/security')
@admin_required
def security_dashboard():
    """Security monitoring dashboard."""
    # Get security events
    security_events = AuditService.get_security_events(hours=24)
    
    # Get failed logins
    failed_logins = AuditService.get_failed_logins(hours=24)
    
    # Get suspicious activity
    suspicious = AuditService.get_suspicious_activity()
    
    # Get statistics
    stats = AuditService.get_statistics(days=30)
    
    return render_template('admin/security.html',
                          security_events=security_events,
                          failed_logins=failed_logins,
                          suspicious=suspicious,
                          stats=stats)


@admin_bp.route('/database')
@admin_required
def db_management():
    """Database management dashboard."""
    from app.models import User, Team, Project, Issue, db
    import os
    
    # Get database stats
    db_path = 'instance/project_mgmt.db'
    db_size = 0
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path) / (1024 * 1024)  # Convert to MB
    
    stats = {
        'users': User.query.count(),
        'teams': Team.query.count(),
        'projects': Project.query.count(),
        'issues': Issue.query.count(),
        'db_size': round(db_size, 2)
    }
    
    return render_template('admin/database.html', stats=stats)


@admin_bp.route('/settings')
@admin_required
def system_settings():
    """System settings page."""
    from flask import current_app
    
    settings = {
        'app_name': current_app.config.get('APP_NAME', 'ProjectFlow'),
        'debug_mode': current_app.config.get('DEBUG', False),
        'secret_key_set': bool(current_app.config.get('SECRET_KEY')),
        'encryption_enabled': True,
        'max_upload_size': current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024) / (1024 * 1024)
    }
    
    return render_template('admin/settings.html', settings=settings)


@admin_bp.route('/backup')
@admin_required
def backup_restore():
    """Backup and restore page."""
    import os
    from datetime import datetime
    
    # List existing backups
    backup_dir = 'backups'
    backups = []
    
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db') or filename.endswith('.sql'):
                filepath = os.path.join(backup_dir, filename)
                backups.append({
                    'name': filename,
                    'size': round(os.path.getsize(filepath) / (1024 * 1024), 2),
                    'date': datetime.fromtimestamp(os.path.getmtime(filepath))
                })
    
    backups.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('admin/backup.html', backups=backups)


@admin_bp.route('/analytics')
@admin_required
def analytics_dashboard():
    """Analytics dashboard with charts and metrics."""
    from app.models import User, Team, Project, Issue
    from datetime import datetime, timedelta
    from sqlalchemy import func
    import json
    
    verify_admin_privilege()
    
    # Basic counts
    project_count = Project.query.count()
    user_count = User.query.count()
    
    # Online users count (last 5 minutes)
    five_mins_ago = datetime.utcnow() - timedelta(minutes=5)
    online_count = User.query.filter(User.last_activity >= five_mins_ago).count() if hasattr(User, 'last_activity') else 0
    
    # Issue statistics
    total_issues = Issue.query.count()
    completed_issues = Issue.query.filter(Issue.status.in_(['Done', 'Closed', 'Resolved'])).count() if total_issues > 0 else 0
    active_issues = total_issues - completed_issues
    completion_rate = round((completed_issues / total_issues * 100) if total_issues > 0 else 0)
    
    # Project Status Distribution
    project_status_counts = {}
    projects = Project.query.all()
    for project in projects:
        status = project.status or 'Unknown'
        project_status_counts[status] = project_status_counts.get(status, 0) + 1
    
    project_status_data = json.dumps({
        'labels': list(project_status_counts.keys()) if project_status_counts else ['No Projects'],
        'values': list(project_status_counts.values()) if project_status_counts else [0]
    })
    
    # Issue Priority Distribution
    issue_priority_counts = {}
    issues = Issue.query.all()
    for issue in issues:
        priority = issue.priority or 'Medium'
        issue_priority_counts[priority] = issue_priority_counts.get(priority, 0) + 1
    
    # Order priorities
    priority_order = ['Critical', 'Highest', 'High', 'Medium', 'Low', 'Lowest']
    sorted_priorities = []
    sorted_priority_values = []
    for p in priority_order:
        if p in issue_priority_counts:
            sorted_priorities.append(p)
            sorted_priority_values.append(issue_priority_counts[p])
    
    issue_priority_data = json.dumps({
        'labels': sorted_priorities if sorted_priorities else ['No Issues'],
        'values': sorted_priority_values if sorted_priority_values else [0]
    })
    
    # Issue Status Distribution
    issue_status_counts = {}
    for issue in issues:
        status = issue.status or 'Open'
        issue_status_counts[status] = issue_status_counts.get(status, 0) + 1
    
    issue_status_data = json.dumps({
        'labels': list(issue_status_counts.keys()) if issue_status_counts else ['No Issues'],
        'values': list(issue_status_counts.values()) if issue_status_counts else [0]
    })
    
    # Issue Types Distribution
    issue_type_counts = {}
    for issue in issues:
        issue_type = issue.type if hasattr(issue, 'type') and issue.type else 'Task'
        issue_type_counts[issue_type] = issue_type_counts.get(issue_type, 0) + 1
    
    issue_types_data = json.dumps({
        'labels': list(issue_type_counts.keys()) if issue_type_counts else ['No Issues'],
        'values': list(issue_type_counts.values()) if issue_type_counts else [0]
    })
    
    # Team Performance (issues completed per team)
    teams = Team.query.all()
    team_names = []
    team_performance = []
    for team in teams[:6]:  # Limit to 6 teams for chart readability
        team_names.append(team.name)
        # Calculate team's issue completion rate
        team_issues = [i for i in issues if hasattr(i, 'assignee') and i.assignee and i.assignee.team_id == team.id]
        team_completed = len([i for i in team_issues if i.status in ['Done', 'Closed', 'Resolved']])
        rate = round((team_completed / len(team_issues) * 100) if team_issues else 0)
        team_performance.append(rate)
    
    team_performance_data = json.dumps({
        'labels': team_names if team_names else ['No Teams'],
        'values': team_performance if team_performance else [0]
    })
    
    # Project Progress
    project_names = []
    project_progress = []
    for project in projects[:5]:  # Limit to 5 projects
        project_names.append(project.name[:15] + '...' if len(project.name) > 15 else project.name)
        # Calculate progress based on issues
        project_issues = [i for i in issues if i.project_id == project.id]
        completed = len([i for i in project_issues if i.status in ['Done', 'Closed', 'Resolved']])
        progress = round((completed / len(project_issues) * 100) if project_issues else 0)
        project_progress.append(progress)
    
    project_progress_data = json.dumps({
        'labels': project_names if project_names else ['No Projects'],
        'values': project_progress if project_progress else [0]
    })
    
    # Activity over last 7 days
    days = []
    issues_created = []
    issues_resolved = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        days.append(day.strftime('%a'))
        
        # Count issues created on this day
        created = Issue.query.filter(
            Issue.created_at >= day_start,
            Issue.created_at <= day_end
        ).count() if hasattr(Issue, 'created_at') else 0
        issues_created.append(created)
        
        # Count issues resolved on this day
        resolved = Issue.query.filter(
            Issue.updated_at >= day_start,
            Issue.updated_at <= day_end,
            Issue.status.in_(['Done', 'Closed', 'Resolved'])
        ).count() if hasattr(Issue, 'updated_at') else 0
        issues_resolved.append(resolved)
    
    activity_data = json.dumps({
        'labels': days,
        'issues_created': issues_created,
        'issues_resolved': issues_resolved
    })
    
    log_admin_action(
        session.get('user_id'),
        'ANALYTICS_DASHBOARD_ACCESS',
        {'ip': request.remote_addr}
    )
    
    return render_template('admin/analytics.html',
                          project_count=project_count,
                          user_count=user_count,
                          online_count=online_count,
                          active_issues=active_issues,
                          completed_issues=completed_issues,
                          completion_rate=completion_rate,
                          project_status_data=project_status_data,
                          issue_priority_data=issue_priority_data,
                          issue_status_data=issue_status_data,
                          issue_types_data=issue_types_data,
                          team_performance_data=team_performance_data,
                          project_progress_data=project_progress_data,
                          activity_data=activity_data)


@admin_bp.route('/tools')
@admin_required
def admin_tools():
    """Admin Tools Dashboard - Central hub for all admin tools."""
    from app.models import User, Project, Issue
    
    admin_user = verify_admin_privilege()
    
    # Tool categories with their items
    tools = {
        'analytics': {
            'name': 'Analytics & Reports',
            'description': 'View detailed analytics, charts, and performance metrics',
            'icon': 'bar-chart-3',
            'color': '#8957E5',
            'url': url_for('admin.analytics_dashboard'),
            'badge': 'Popular'
        },
        'automation': {
            'name': 'Automation & Workflows',
            'description': 'Create automated rules, triggers, and workflow processes',
            'icon': 'workflow',
            'color': '#238636',
            'url': url_for('admin.admin_automation')
        },
        'service_desk': {
            'name': 'Service Desk',
            'description': 'Manage support tickets, queues, and customer requests',
            'icon': 'headset',
            'color': '#58A6FF',
            'url': url_for('admin.admin_service_desk')
        },
        'integrations': {
            'name': 'Integrations & Apps',
            'description': 'Connect with external services and third-party apps',
            'icon': 'puzzle',
            'color': '#D29922',
            'url': url_for('admin.admin_integrations')
        },
        'search': {
            'name': 'Advanced Search',
            'description': 'Powerful search across all projects, issues, and users',
            'icon': 'search',
            'color': '#F85149',
            'url': url_for('admin.admin_search')
        },
        'change_calendar': {
            'name': 'Change Calendar',
            'description': 'Plan and track scheduled changes and releases',
            'icon': 'calendar-clock',
            'color': '#A371F7',
            'url': url_for('admin.admin_change_calendar')
        },
        'backup': {
            'name': 'Backup & Restore',
            'description': 'Create backups and restore system data',
            'icon': 'hard-drive-download',
            'color': '#7EE787',
            'url': url_for('admin.backup_restore')
        },
        'database': {
            'name': 'Database Management',
            'description': 'Manage database tables, run queries, and optimize',
            'icon': 'database',
            'color': '#79C0FF',
            'url': url_for('admin.db_management')
        },
        'security': {
            'name': 'Security Settings',
            'description': 'Configure security policies and access controls',
            'icon': 'shield-check',
            'color': '#238636',
            'url': url_for('admin.security_dashboard')
        },
        'audit_logs': {
            'name': 'Audit Logs',
            'description': 'View system activity logs and security events',
            'icon': 'scroll-text',
            'color': '#8B949E',
            'url': url_for('admin.audit_logs')
        }
    }
    
    log_admin_action(
        session.get('user_id'),
        'ADMIN_TOOLS_ACCESS',
        {'ip': request.remote_addr}
    )
    
    return render_template('admin/tools.html', tools=tools)


@admin_bp.route('/automation')
@admin_required
def admin_automation():
    """Automation & Workflows tool."""
    admin_user = verify_admin_privilege()
    return render_template('admin/automation.html')


@admin_bp.route('/service-desk')
@admin_required
def admin_service_desk():
    """Service Desk management."""
    admin_user = verify_admin_privilege()
    return render_template('admin/service_desk.html')


@admin_bp.route('/integrations')
@admin_required
def admin_integrations():
    """Integrations & Apps management."""
    admin_user = verify_admin_privilege()
    return render_template('admin/integrations.html')


@admin_bp.route('/search')
@admin_required
def admin_search():
    """Advanced Search across all data."""
    from app.models import User, Project, Issue
    
    admin_user = verify_admin_privilege()
    query = request.args.get('q', '')
    results = {'users': [], 'projects': [], 'issues': []}
    
    if query:
        # Search users
        results['users'] = User.query.filter(
            User.username.ilike(f'%{query}%') | 
            User.email.ilike(f'%{query}%')
        ).limit(10).all()
        
        # Search projects
        results['projects'] = Project.query.filter(
            Project.name.ilike(f'%{query}%') |
            Project.key.ilike(f'%{query}%')
        ).limit(10).all()
        
        # Search issues
        results['issues'] = Issue.query.filter(
            Issue.title.ilike(f'%{query}%') |
            Issue.key.ilike(f'%{query}%')
        ).limit(20).all()
    
    return render_template('admin/search.html', query=query, results=results)


@admin_bp.route('/change-calendar')
@admin_required
def admin_change_calendar():
    """Change Calendar & Risk Management."""
    admin_user = verify_admin_privilege()
    return render_template('admin/change_calendar.html')


@admin_bp.route('/backup/create', methods=['POST'])
@admin_required
def create_backup():
    """Create a database backup."""
    import shutil
    import os
    from datetime import datetime
    
    # CSRF validated by Flask-WTF
    # Create backup directory if not exists
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'backup_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        # Copy database file
        shutil.copy('instance/project_mgmt.db', backup_path)
        
        AuditService.log_event(
            'BACKUP_CREATED',
            user_id=session.get('user_id'),
            details=f'Created backup: {backup_name}',
            category='SYSTEM'
        )
        
        flash(f'Backup created successfully: {backup_name}', 'success')
    except Exception as e:
        flash(f'Failed to create backup: {str(e)}', 'error')
    
    return redirect(url_for('admin.backup_restore'))

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
    
    # Get recent users
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
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
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin.admin_users'))
    
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
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin.admin_users'))
    
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
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin.admin_users'))
    
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
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin.admin_users'))
    
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
    from app.models import Team
    
    teams = Team.query.all()
    return render_template('admin/teams.html', teams=teams)


@admin_bp.route('/team/add', methods=['POST'])
@admin_required
def add_team():
    """Add a new team."""
    from app.models import Team, db
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin.admin_teams'))
    
    name = sanitize_input(request.form.get('name', '').strip())
    description = sanitize_input(request.form.get('description', '').strip())
    
    if not name:
        flash('Team name is required', 'error')
        return redirect(url_for('admin.admin_teams'))
    
    team = Team(name=name)
    team.description = description
    
    db.session.add(team)
    db.session.commit()
    
    AuditService.log_event(
        'TEAM_CREATED',
        user_id=session.get('user_id'),
        details=f'Created team: {name}',
        category='DATA_MODIFICATION'
    )
    
    flash('Team created successfully', 'success')
    return redirect(url_for('admin.admin_teams'))


@admin_bp.route('/team/<int:team_id>/edit', methods=['POST'])
@admin_required
def edit_team(team_id):
    """Edit team information."""
    from app.models import Team, db
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin.admin_teams'))
    
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
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin.admin_teams'))
    
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


@admin_bp.route('/projects')
@admin_required
def admin_projects():
    """Project management page."""
    from app.models import Project, Team
    
    projects = Project.query.all()
    teams = Team.query.all()
    
    return render_template('admin/projects.html', projects=projects, teams=teams)


@admin_bp.route('/project/add', methods=['POST'])
@admin_required
def add_project():
    """Add a new project."""
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin.admin_projects'))
    
    name = request.form.get('name', '').strip()
    key = request.form.get('key', '').strip()
    description = request.form.get('description', '').strip()
    status = request.form.get('status', 'Not Started')
    workflow_type = request.form.get('workflow_type', 'agile')
    team_id = request.form.get('team_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    success, project, message = ProjectService.create_project(
        name=name,
        key=key if key else None,
        description=description,
        status=status,
        workflow_type=workflow_type,
        team_id=team_id,
        start_date=start_date,
        end_date=end_date,
        created_by=session.get('user_id')
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_projects'))


@admin_bp.route('/project/<int:project_id>/edit', methods=['POST'])
@admin_required
def edit_project(project_id):
    """Edit project information."""
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin.admin_projects'))
    
    name = request.form.get('name', '').strip()
    key = request.form.get('key', '').strip()
    description = request.form.get('description', '').strip()
    status = request.form.get('status')
    workflow_type = request.form.get('workflow_type')
    team_id = request.form.get('team_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    success, project, message = ProjectService.update_project(
        project_id=project_id,
        data={
            'name': name,
            'key': key if key else None,
            'description': description,
            'status': status,
            'workflow_type': workflow_type,
            'team_id': team_id,
            'start_date': start_date,
            'end_date': end_date
        },
        updated_by=session.get('user_id')
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_projects'))


@admin_bp.route('/project/<int:project_id>/update_status', methods=['POST'])
@admin_required
def update_project_status(project_id):
    """Update project status."""
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin.admin_projects'))
    
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
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin.admin_projects'))
    
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

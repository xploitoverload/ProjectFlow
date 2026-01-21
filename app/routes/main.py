# app/routes/main.py
"""
Main Routes
Handles dashboard, landing page, and general navigation.
"""

from flask import Blueprint, render_template, redirect, url_for, session, request
from app.middleware import login_required
from app.services import ProjectService, ReportService

main_bp = Blueprint('main', __name__)


@main_bp.route('/test-icons')
def test_icons():
    """Test page for Lucide icons."""
    return render_template('test_icons.html')


@main_bp.route('/')
def index():
    """Landing page or redirect to dashboard."""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard view."""
    from app.models import User, Team
    
    user = User.query.get(session['user_id'])
    
    # Get accessible projects based on role
    projects = ProjectService.get_user_accessible_projects(user)
    
    # Get teams (admin sees all, others see their team)
    if user.role in ['admin', 'super_admin']:
        teams = Team.query.all()
    else:
        teams = [user.team] if user.team else []
    
    # Calculate statistics
    stats = {
        'total': len(projects),
        'not_started': len([p for p in projects if p.status == 'Not Started']),
        'in_progress': len([p for p in projects if p.status in ['In Progress', 'Active']]),
        'on_hold': len([p for p in projects if p.status in ['On Hold', 'Blocked', 'At Risk']]),
        'completed': len([p for p in projects if p.status == 'Completed'])
    }
    
    # Get Gantt data for admin
    gantt_data = None
    if user.role in ['admin', 'super_admin']:
        gantt_data = ProjectService.get_gantt_data(projects)
    
    return render_template('dashboard.html',
                          user=user,
                          projects=projects,
                          teams=teams,
                          stats=stats,
                          gantt_data=gantt_data)


@main_bp.route('/reports')
@login_required
def reports():
    """User reports page."""
    from app.models import User, Project, ProjectUpdate
    
    # Get filter parameters
    filter_type = request.args.get('filter', 'all')
    sort_by = request.args.get('sort', 'date')
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    user = User.query.get(session['user_id'])
    
    # Get user's updates
    updates = ReportService.get_user_updates(
        user.id,
        filter_type=filter_type,
        status_filter=status_filter if status_filter else None,
        search_query=search_query if search_query else None,
        sort_by=sort_by
    )
    
    # Get user's projects
    user_projects = Project.query.join(ProjectUpdate).filter(
        ProjectUpdate.user_id == user.id
    ).distinct().all() if updates else []
    
    projects_list = [{'id': p.id, 'name': p.name, 'key': p.key} for p in user_projects]
    
    # Get statistics
    stats = ReportService.get_user_statistics(user.id, filter_type)
    
    return render_template('reports.html',
                          updates=updates,
                          projects=projects_list,
                          filter_type=filter_type,
                          sort_by=sort_by,
                          search_query=search_query,
                          status_filter=status_filter,
                          stats=stats)


@main_bp.route('/gantt')
@login_required
def gantt_chart():
    """Gantt chart view."""
    from app.models import User, Team
    
    user = User.query.get(session['user_id'])
    
    if user.role not in ['admin', 'super_admin', 'manager']:
        from flask import flash, abort
        flash('Access denied. Manager or admin access required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    projects = ProjectService.get_user_accessible_projects(user)
    teams = Team.query.all()
    gantt_data = ProjectService.get_gantt_data(projects)
    
    return render_template('gantt_chart.html',
                          gantt_data=gantt_data,
                          teams=teams)


@main_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    from app.models import User
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)


@main_bp.route('/settings')
@login_required
def settings():
    """User settings page."""
    from app.models import User
    
    user = User.query.get(session['user_id'])
    return render_template('settings.html', user=user)


@main_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile."""
    from app.models import User, db
    from app.utils.security import validate_csrf_token
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        from flask import flash
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('main.settings'))
    
    user = User.query.get(session['user_id'])
    
    # Update allowed fields
    email = request.form.get('email', '').strip()
    full_name = request.form.get('full_name', '').strip()
    avatar_color = request.form.get('avatar_color', '').strip()
    
    if email:
        user.email = email
    if full_name:
        user.full_name = full_name
    if avatar_color:
        user.avatar_color = avatar_color
    
    db.session.commit()
    
    from flask import flash
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.settings'))

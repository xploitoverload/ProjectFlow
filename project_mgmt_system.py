# app.py - Secure Main Application with Role-Based Access
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from datetime import datetime, timedelta
from models import db, User, Team, Project, ProjectUpdate
from security import (
    login_required, admin_required, generate_csrf_token, validate_csrf_token,
    rate_limit_login, rate_limit_request, sanitize_input, validate_email,
    validate_username, validate_password_strength, validate_sql_input,
    get_client_ip, log_audit, check_account_lockout, record_failed_login,
    reset_failed_login, SecurityHeaders
)
import os

app = Flask(__name__)

# Secure configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db.init_app(app)

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    return SecurityHeaders.add_headers(response)

# Rate limiting middleware
@app.before_request
def rate_limit_middleware():
    ip = get_client_ip()
    if not rate_limit_request(ip):
        abort(429)

# CSRF token available in all templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf_token)

# ============= AUTHENTICATION ROUTES =============

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            log_audit(None, 'CSRF_TOKEN_INVALID', 'Invalid CSRF token on login')
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('login'))
        
        ip = get_client_ip()
        
        if not rate_limit_login(ip):
            log_audit(None, 'RATE_LIMIT_EXCEEDED', f'IP: {ip}')
            flash('Too many login attempts. Please try again later.', 'error')
            return redirect(url_for('login'))
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not validate_username(username):
            flash('Invalid username format', 'error')
            return redirect(url_for('login'))
        
        if not validate_sql_input(username):
            log_audit(None, 'SQL_INJECTION_ATTEMPT', f'Username: {username}, IP: {ip}')
            flash('Invalid input detected', 'error')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            is_locked, message = check_account_lockout(user)
            if is_locked:
                log_audit(user.id, 'LOGIN_ATTEMPT_LOCKED', message)
                flash(message, 'error')
                return redirect(url_for('login'))
            
            if user.check_password(password):
                reset_failed_login(user)
                session.clear()
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                session['team_id'] = user.team_id
                session['last_activity'] = datetime.utcnow().isoformat()
                session.permanent = True
                
                log_audit(user.id, 'LOGIN_SUCCESS', f'IP: {ip}')
                flash(f'Welcome {user.username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                record_failed_login(user)
                log_audit(user.id, 'LOGIN_FAILED', f'IP: {ip}')
                flash('Invalid credentials', 'error')
        else:
            log_audit(None, 'LOGIN_FAILED_USER_NOT_FOUND', f'Username: {username}, IP: {ip}')
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        log_audit(user_id, 'LOGOUT', f'IP: {get_client_ip()}')
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

# ============= MAIN ROUTES =============

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    # ROLE-BASED PROJECT FILTERING
    if user.role == 'admin':
        # Admin sees ALL projects
        projects = Project.query.all()
        teams = Team.query.all()
    else:
        # Employee sees only THEIR TEAM's projects
        if user.team_id:
            projects = Project.query.filter_by(team_id=user.team_id).all()
            teams = [user.team] if user.team else []
        else:
            projects = []
            teams = []
    
    # Statistics
    total_projects = len(projects)
    not_started = len([p for p in projects if p.status == 'Not Started'])
    in_progress = len([p for p in projects if p.status == 'In Progress'])
    on_hold = len([p for p in projects if p.status == 'On Hold'])
    completed = len([p for p in projects if p.status == 'Completed'])
    
    stats = {
        'total': total_projects,
        'not_started': not_started,
        'in_progress': in_progress,
        'on_hold': on_hold,
        'completed': completed
    }
    
    # Gantt chart data for admin
    gantt_data = None
    if user.role == 'admin':
        gantt_data = []
        for project in projects:
            if project.start_date:
                gantt_data.append({
                    'id': project.id,
                    'name': project.name,
                    'start': project.start_date.strftime('%Y-%m-%d'),
                    'end': project.end_date.strftime('%Y-%m-%d') if project.end_date else (project.start_date + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'status': project.status,
                    'team': project.team.name if project.team else 'Unassigned',
                    'progress': 100 if project.status == 'Completed' else (75 if project.status == 'In Progress' else (25 if project.status == 'On Hold' else 0))
                })
    
    return render_template('dashboard.html', user=user, projects=projects, teams=teams, stats=stats, gantt_data=gantt_data)

@app.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        flash('You do not have access to this project', 'error')
        abort(403)
    
    updates = ProjectUpdate.query.filter_by(project_id=project_id).order_by(ProjectUpdate.date.desc()).all()
    return render_template('project_detail.html', project=project, updates=updates)

@app.route('/project/<int:project_id>/add_update', methods=['POST'])
@login_required
def add_update(project_id):
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        log_audit(session['user_id'], 'CSRF_TOKEN_INVALID', 'Invalid CSRF on add_update')
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('project_detail', project_id=project_id))
    
    project = Project.query.get_or_404(project_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        flash('You do not have access to this project', 'error')
        abort(403)
    
    update_text = request.form.get('update_text', '').strip()
    hours_worked = request.form.get('hours_worked', 0)
    
    update_text = sanitize_input(update_text)
    
    if not update_text:
        flash('Update text cannot be empty', 'error')
        return redirect(url_for('project_detail', project_id=project_id))
    
    if not validate_sql_input(update_text):
        log_audit(session['user_id'], 'SQL_INJECTION_ATTEMPT', f'Project ID: {project_id}')
        flash('Invalid input detected', 'error')
        return redirect(url_for('project_detail', project_id=project_id))
    
    try:
        hours = float(hours_worked)
        if hours < 0 or hours > 24:
            flash('Hours must be between 0 and 24', 'error')
            return redirect(url_for('project_detail', project_id=project_id))
    except ValueError:
        flash('Invalid hours format', 'error')
        return redirect(url_for('project_detail', project_id=project_id))
    
    update = ProjectUpdate(
        project_id=project_id,
        user_id=session['user_id'],
        hours_worked=hours
    )
    update.update_text = update_text
    
    db.session.add(update)
    db.session.commit()
    
    log_audit(session['user_id'], 'PROJECT_UPDATE_ADDED', f'Project ID: {project_id}')
    flash('Update added successfully', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/reports')
@login_required
def reports():
    filter_type = request.args.get('filter', 'daily')
    
    if filter_type not in ['daily', 'weekly', 'monthly', 'all']:
        filter_type = 'daily'
    
    now = datetime.utcnow()
    if filter_type == 'daily':
        start_date = now - timedelta(days=1)
    elif filter_type == 'weekly':
        start_date = now - timedelta(weeks=1)
    elif filter_type == 'monthly':
        start_date = now - timedelta(days=30)
    else:
        start_date = datetime.min
    
    user = User.query.get(session['user_id'])
    
    # Filter updates based on role
    if user.role == 'admin':
        updates = ProjectUpdate.query.filter(ProjectUpdate.date >= start_date).order_by(ProjectUpdate.date.desc()).all()
    else:
        # Employee sees only their team's updates
        if user.team_id:
            team_projects = Project.query.filter_by(team_id=user.team_id).all()
            project_ids = [p.id for p in team_projects]
            updates = ProjectUpdate.query.filter(
                ProjectUpdate.date >= start_date,
                ProjectUpdate.project_id.in_(project_ids)
            ).order_by(ProjectUpdate.date.desc()).all()
        else:
            updates = []
    
    return render_template('reports.html', updates=updates, filter_type=filter_type)

# ============= ADMIN ROUTES =============

@app.route('/admin/teams')
@admin_required
def admin_teams():
    teams = Team.query.all()
    return render_template('admin/teams.html', teams=teams)

@app.route('/admin/team/add', methods=['POST'])
@admin_required
def add_team():
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin_teams'))
    
    name = sanitize_input(request.form.get('name', '').strip())
    description = sanitize_input(request.form.get('description', '').strip())
    
    if not name:
        flash('Team name is required', 'error')
        return redirect(url_for('admin_teams'))
    
    team = Team(name=name)
    team.description = description
    
    db.session.add(team)
    db.session.commit()
    
    log_audit(session['user_id'], 'TEAM_CREATED', f'Team: {name}')
    flash('Team added successfully', 'success')
    return redirect(url_for('admin_teams'))

@app.route('/admin/team/<int:team_id>/delete', methods=['POST'])
@admin_required
def delete_team(team_id):
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin_teams'))
    
    team = Team.query.get_or_404(team_id)
    team_name = team.name
    
    db.session.delete(team)
    db.session.commit()
    
    log_audit(session['user_id'], 'TEAM_DELETED', f'Team: {team_name}')
    flash('Team deleted successfully', 'success')
    return redirect(url_for('admin_teams'))

@app.route('/admin/projects')
@admin_required
def admin_projects():
    projects = Project.query.all()
    teams = Team.query.all()
    return render_template('admin/projects.html', projects=projects, teams=teams)

@app.route('/admin/project/add', methods=['POST'])
@admin_required
def add_project():
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin_projects'))
    
    name = sanitize_input(request.form.get('name', '').strip())
    description = sanitize_input(request.form.get('description', '').strip())
    status = request.form.get('status', 'Not Started')
    team_id = request.form.get('team_id')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    valid_statuses = ['Not Started', 'In Progress', 'On Hold', 'Completed']
    if status not in valid_statuses:
        flash('Invalid project status', 'error')
        return redirect(url_for('admin_projects'))
    
    if not name:
        flash('Project name is required', 'error')
        return redirect(url_for('admin_projects'))
    
    # Parse dates
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.utcnow()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
    
    project = Project(
        name=name,
        status=status,
        team_id=int(team_id) if team_id else None,
        start_date=start_date,
        end_date=end_date,
        created_by=session['user_id']
    )
    project.description = description
    
    db.session.add(project)
    db.session.commit()
    
    log_audit(session['user_id'], 'PROJECT_CREATED', f'Project: {name}')
    flash('Project added successfully', 'success')
    return redirect(url_for('admin_projects'))

@app.route('/admin/project/<int:project_id>/update_status', methods=['POST'])
@admin_required
def update_project_status(project_id):
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin_projects'))
    
    project = Project.query.get_or_404(project_id)
    status = request.form.get('status')
    
    valid_statuses = ['Not Started', 'In Progress', 'On Hold', 'Completed']
    if status not in valid_statuses:
        flash('Invalid project status', 'error')
        return redirect(url_for('admin_projects'))
    
    old_status = project.status
    project.status = status
    
    # Auto-set end date if completed
    if status == 'Completed' and not project.end_date:
        project.end_date = datetime.utcnow()
    
    db.session.commit()
    
    log_audit(session['user_id'], 'PROJECT_STATUS_UPDATED', f'Project ID: {project_id}, {old_status} -> {status}')
    flash('Project status updated', 'success')
    return redirect(url_for('admin_projects'))

@app.route('/admin/project/<int:project_id>/delete', methods=['POST'])
@admin_required
def delete_project(project_id):
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin_projects'))
    
    project = Project.query.get_or_404(project_id)
    project_name = project.name
    
    db.session.delete(project)
    db.session.commit()
    
    log_audit(session['user_id'], 'PROJECT_DELETED', f'Project: {project_name} (ID: {project_id})')
    flash('Project deleted successfully', 'success')
    return redirect(url_for('admin_projects'))

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    teams = Team.query.all()
    return render_template('admin/users.html', users=users, teams=teams)

@app.route('/admin/user/add', methods=['POST'])
@admin_required
def add_user():
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin_users'))
    
    username = sanitize_input(request.form.get('username', '').strip())
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'employee')
    team_id = request.form.get('team_id')
    
    if not validate_username(username):
        flash('Invalid username. Use 3-20 alphanumeric characters and underscores only.', 'error')
        return redirect(url_for('admin_users'))
    
    if not validate_email(email):
        flash('Invalid email format', 'error')
        return redirect(url_for('admin_users'))
    
    is_strong, message = validate_password_strength(password)
    if not is_strong:
        flash(message, 'error')
        return redirect(url_for('admin_users'))
    
    if role not in ['admin', 'employee']:
        flash('Invalid role', 'error')
        return redirect(url_for('admin_users'))
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'error')
        return redirect(url_for('admin_users'))
    
    user = User(
        username=username,
        role=role,
        team_id=int(team_id) if team_id else None
    )
    user.email = email
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    log_audit(session['user_id'], 'USER_CREATED', f'Username: {username}, Role: {role}')
    flash('User added successfully', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('admin_users'))
    
    if user_id == session['user_id']:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(user_id)
    username = user.username
    
    db.session.delete(user)
    db.session.commit()
    
    log_audit(session['user_id'], 'USER_DELETED', f'Username: {username}')
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin_users'))

# Error handlers
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error='403 Forbidden', message='You do not have permission to access this resource.'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='404 Not Found', message='The requested resource was not found.'), 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return render_template('error.html', error='429 Too Many Requests', message='Rate limit exceeded. Please try again later.'), 429

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('error.html', error='500 Internal Server Error', message='An internal error occurred.'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)
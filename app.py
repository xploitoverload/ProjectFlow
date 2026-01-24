# app.py - Secure Main Application with Kanban Board Support
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify
from datetime import datetime, timedelta
from models import db, User, Team, Project, ProjectUpdate, Issue, Sprint, Epic, Comment
from security import (
    login_required, admin_required, generate_csrf_token, validate_csrf_token,
    rate_limit_login, rate_limit_request, sanitize_input, validate_email,
    validate_username, validate_password_strength, validate_sql_input,
    get_client_ip, log_audit, check_account_lockout, record_failed_login,
    reset_failed_login, SecurityHeaders
)
import os
from config import config

app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Additional secure configuration
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
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
    return render_template('landing.html')

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

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # In production, send reset email here
            flash('Password reset instructions have been sent to your email.', 'success')
        else:
            # Don't reveal if user exists
            flash('If an account with that email exists, password reset instructions have been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    # In production, validate token
    if request.method == 'POST':
        password = request.form.get('password')
        # Update password logic here
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password for logged-in users"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        user = User.query.get(session['user_id'])
        if user and user.check_password(current_password):
            user.set_password(new_password)
            db.session.commit()
            log_audit(user.id, 'PASSWORD_CHANGED', f'IP: {get_client_ip()}')
            flash('Password changed successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('change_password.html')

# ============= MAIN ROUTES =============

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    # ROLE-BASED PROJECT FILTERING
    if user.role == 'admin':
        projects = Project.query.all()
        teams = Team.query.all()
    else:
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
    
    # Check access
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

# ============= KANBAN BOARD ROUTES =============

@app.route('/project/<int:project_id>/kanban')
@login_required
def project_kanban(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        flash('You do not have access to this project', 'error')
        abort(403)
    
    # Get all issues for this project
    issues = Issue.query.filter_by(project_id=project_id).order_by(Issue.position).all()
    
    # Group issues by status (8 states)
    issues_by_status = {
        'open': [],
        'todo': [],
        'in_progress': [],
        'code_review': [],
        'testing': [],
        'ready_deploy': [],
        'done': [],
        'closed': []
    }
    
    for issue in issues:
        if issue.status in issues_by_status:
            issues_by_status[issue.status].append(issue)
    
    # Calculate statistics
    total_issues = len(issues)
    completed_issues = len(issues_by_status['done'])
    completed_percentage = int((completed_issues / total_issues * 100)) if total_issues > 0 else 0
    total_hours = sum(issue.time_estimate or 0 for issue in issues)
    
    # Get team members
    team_members_list = []
    if project.team:
        team_members_list = User.query.filter_by(team_id=project.team_id).all()
    
    team_members = len(team_members_list)
    
    return render_template('kanban_board.html',
                         project=project,
                         issues_by_status=issues_by_status,
                         total_issues=total_issues,
                         completed_percentage=completed_percentage,
                         total_hours=total_hours,
                         team_members=team_members,
                         team_members_list=team_members_list)

def generate_issue_key(project_id):
    """Generate unique issue key like PROJ-123"""
    project = Project.query.get(project_id)
    prefix = ''.join([c for c in project.name.upper() if c.isalnum()])[:4]
    
    # Get the last issue number for this project
    last_issue = Issue.query.filter_by(project_id=project_id).order_by(Issue.id.desc()).first()
    number = 1 if not last_issue else int(last_issue.key.split('-')[-1]) + 1
    
    return f"{prefix}-{number}"

@app.route('/project/<int:project_id>/issue/add', methods=['POST'])
@login_required
def add_issue(project_id):
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('project_kanban', project_id=project_id))
    
    project = Project.query.get_or_404(project_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        flash('You do not have access to this project', 'error')
        abort(403)
    
    title = sanitize_input(request.form.get('title', '').strip())
    description = sanitize_input(request.form.get('description', '').strip())
    priority = request.form.get('priority', 'medium')
    assignee_id = request.form.get('assigned_to')
    time_estimate = request.form.get('time_estimate', 0)
    due_date_str = request.form.get('due_date')
    
    if not title:
        flash('Issue title is required', 'error')
        return redirect(url_for('project_kanban', project_id=project_id))
    
    try:
        hours = float(time_estimate)
        if hours < 0:
            flash('Hours must be positive', 'error')
            return redirect(url_for('project_kanban', project_id=project_id))
    except ValueError:
        flash('Invalid hours format', 'error')
        return redirect(url_for('project_kanban', project_id=project_id))
    
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('project_kanban', project_id=project_id))
    
    # Get the maximum position for open status (new issues start as "open")
    max_position = db.session.query(db.func.max(Issue.position)).filter_by(
        project_id=project_id, status='open'
    ).scalar() or 0
    
    issue = Issue(
        key=generate_issue_key(project_id),
        title=title,
        project_id=project_id,
        priority=priority,
        assignee_id=int(assignee_id) if assignee_id else None,
        reporter_id=session['user_id'],
        time_estimate=hours,
        due_date=due_date,
        status='open',  # New issues start as "open"
        position=max_position + 1
    )
    issue.description = description
    
    db.session.add(issue)
    db.session.commit()
    
    log_audit(session['user_id'], 'ISSUE_CREATED', f'Issue: {issue.key}, Project ID: {project_id}')
    flash('Issue created successfully', 'success')
    return redirect(url_for('project_kanban', project_id=project_id))

@app.route('/project/<int:project_id>/issue/<int:issue_id>/update_status', methods=['POST'])
@login_required
def update_issue_status(project_id, issue_id):
    project = Project.query.get_or_404(project_id)
    issue = Issue.query.get_or_404(issue_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    if issue.project_id != project_id:
        return jsonify({'success': False, 'error': 'Issue not in project'}), 400
    
    data = request.get_json()
    new_status = data.get('status')
    
    valid_statuses = ['open', 'todo', 'in_progress', 'code_review', 'testing', 'ready_deploy', 'done', 'closed']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    
    old_status = issue.status
    issue.status = new_status
    
    # Mark completion date when moved to done or closed
    if new_status in ['done', 'closed'] and old_status not in ['done', 'closed']:
        issue.completed_at = datetime.utcnow()
    elif new_status not in ['done', 'closed']:
        issue.completed_at = None
    
    db.session.commit()
    
    log_audit(session['user_id'], 'ISSUE_STATUS_UPDATED', 
             f'Issue: {issue.key}, {old_status} -> {new_status}')
    
    return jsonify({'success': True, 'new_status': new_status})

@app.route('/project/<int:project_id>/issue/<int:issue_id>/delete', methods=['POST'])
@login_required
def delete_issue(project_id, issue_id):
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('project_kanban', project_id=project_id))
    
    project = Project.query.get_or_404(project_id)
    issue = Issue.query.get_or_404(issue_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        flash('You do not have access to this project', 'error')
        abort(403)
    
    issue_key = issue.key
    db.session.delete(issue)
    db.session.commit()
    
    log_audit(session['user_id'], 'ISSUE_DELETED', f'Issue: {issue_key}')
    flash('Issue deleted successfully', 'success')
    return redirect(url_for('project_kanban', project_id=project_id))

# ============= TIMELINE/GANTT VIEW ROUTES =============

@app.route('/project/<int:project_id>/timeline')
@login_required
def project_timeline(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        flash('You do not have access to this project', 'error')
        abort(403)
    
    # Get all issues with dates
    issues = Issue.query.filter_by(project_id=project_id).all()
    
    # Get dependencies (issue links)
    from models import IssueLink
    dependencies = IssueLink.query.join(
        Issue, IssueLink.source_issue_id == Issue.id
    ).filter(Issue.project_id == project_id).all()
    
    return render_template('timeline_view.html',
                         project=project,
                         issues=issues,
                         dependencies=dependencies)

# ============= WORKFLOW DIAGRAM ROUTES =============

@app.route('/project/<int:project_id>/workflow')
@login_required
def project_workflow(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        flash('You do not have access to this project', 'error')
        abort(403)
    
    # Get recent workflow transitions
    from models import WorkflowTransition
    recent_transitions = WorkflowTransition.query.join(
        Issue, WorkflowTransition.issue_id == Issue.id
    ).filter(Issue.project_id == project_id).order_by(
        WorkflowTransition.timestamp.desc()
    ).limit(20).all()
    
    return render_template('workflow_diagram.html',
                         project=project,
                         recent_transitions=recent_transitions)

# ============= ISSUE DETAIL / MODAL ROUTES =============

@app.route('/api/project/<int:project_id>/issue/<int:issue_id>')
@login_required
def api_get_issue(project_id, issue_id):
    """API endpoint to get issue details as JSON"""
    project = Project.query.get_or_404(project_id)
    issue = Issue.query.get_or_404(issue_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if issue.project_id != project_id:
        return jsonify({'error': 'Issue not in project'}), 400
    
    return jsonify({
        'id': issue.id,
        'key': issue.key,
        'title': issue.title,
        'description': issue.description,
        'status': issue.status,
        'priority': issue.priority,
        'type': issue.issue_type,
        'assignee': {
            'id': issue.assignee.id,
            'username': issue.assignee.username
        } if issue.assignee else None,
        'reporter': {
            'id': issue.reporter.id,
            'username': issue.reporter.username
        } if issue.reporter else None,
        'created_at': issue.created_at.isoformat(),
        'updated_at': issue.updated_at.isoformat(),
        'due_date': issue.due_date.isoformat() if issue.due_date else None,
        'story_points': issue.story_points,
        'labels': [label.name for label in issue.labels],
        'comments': [
            {
                'id': c.id,
                'text': c.text,
                'author': c.user.username,
                'created_at': c.created_at.isoformat()
            } for c in issue.comments
        ]
    })

@app.route('/api/project/<int:project_id>/issue/<int:issue_id>/comment', methods=['POST'])
@login_required
def api_add_comment(project_id, issue_id):
    """API endpoint to add a comment"""
    project = Project.query.get_or_404(project_id)
    issue = Issue.query.get_or_404(issue_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if issue.project_id != project_id:
        return jsonify({'error': 'Issue not in project'}), 400
    
    data = request.get_json()
    text = sanitize_input(data.get('text', '').strip())
    
    if not text:
        return jsonify({'error': 'Comment text required'}), 400
    
    comment = Comment(
        issue_id=issue_id,
        user_id=session['user_id'],
        text=text
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'id': comment.id,
        'text': comment.text,
        'author': comment.user.username,
        'created_at': comment.created_at.isoformat()
    })

@app.route('/api/project/<int:project_id>/status', methods=['GET'])
@login_required
def api_get_project_status(project_id):
    """API endpoint to get latest project status and updates"""
    project = Project.query.get_or_404(project_id)
    
    # Get latest status update
    latest_update = ProjectUpdate.query.filter_by(project_id=project_id).order_by(
        ProjectUpdate.date.desc()).first()
    
    # Get all updates for dashboard
    all_updates = ProjectUpdate.query.filter_by(project_id=project_id).order_by(
        ProjectUpdate.date.desc()).limit(5).all()
    
    update_data = None
    if latest_update:
        update_data = {
            'id': latest_update.id,
            'status': latest_update.status,
            'progress': latest_update.progress_percentage,
            'update_text': latest_update.update_text,
            'user': latest_update.user.username,
            'date': latest_update.date.isoformat(),
            'hours_worked': latest_update.hours_worked,
            'team_members': latest_update.team_members_count,
            'completion_days': latest_update.estimated_completion_days,
            'blockers': latest_update.blockers
        }
    
    return jsonify({
        'project_id': project.id,
        'name': project.name,
        'status': project.status,
        'latest_update': update_data,
        'recent_updates': [
            {
                'id': u.id,
                'status': u.status,
                'progress': u.progress_percentage,
                'user': u.user.username,
                'date': u.date.isoformat()
            } for u in all_updates
        ]
    })

@app.route('/api/project/<int:project_id>/issue/<int:issue_id>/link', methods=['POST'])
@login_required
def api_link_issues(project_id, issue_id):
    """API endpoint to link two issues"""
    project = Project.query.get_or_404(project_id)
    issue = Issue.query.get_or_404(issue_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    target_issue_id = data.get('target_issue_id')
    link_type = data.get('link_type', 'relates_to')  # blocks, is_blocked_by, relates_to, duplicates
    
    if not target_issue_id:
        return jsonify({'error': 'Target issue required'}), 400
    
    target_issue = Issue.query.get_or_404(target_issue_id)
    
    if target_issue.project_id != project_id:
        return jsonify({'error': 'Target issue not in project'}), 400
    
    # Prevent circular dependencies
    if link_type in ['blocks', 'is_blocked_by']:
        # Check for circular dependency
        from models import IssueLink
        existing = IssueLink.query.filter_by(
            source_issue_id=target_issue_id,
            target_issue_id=issue_id
        ).first()
        if existing:
            return jsonify({'error': 'Circular dependency detected'}), 400
    
    from models import IssueLink
    link = IssueLink(
        source_issue_id=issue_id,
        target_issue_id=target_issue_id,
        link_type=link_type
    )
    
    db.session.add(link)
    db.session.commit()
    
    return jsonify({'success': True, 'link_id': link.id})

# ============= PROJECT REPORTS ROUTES =============

@app.route('/project/<int:project_id>/reports')
@login_required
def project_reports(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        flash('You do not have access to this project', 'error')
        abort(403)
    
    # Calculate project statistics
    all_issues = Issue.query.filter_by(project_id=project_id).all()
    
    stats = {
        'total_issues': len(all_issues),
        'open_issues': len([i for i in all_issues if i.status == 'open']),
        'in_progress': len([i for i in all_issues if i.status == 'in_progress']),
        'done_issues': len([i for i in all_issues if i.status == 'done']),
        'closed_issues': len([i for i in all_issues if i.status == 'closed']),
        'by_priority': {
            'critical': len([i for i in all_issues if i.priority == 'critical']),
            'high': len([i for i in all_issues if i.priority == 'high']),
            'medium': len([i for i in all_issues if i.priority == 'medium']),
            'low': len([i for i in all_issues if i.priority == 'low']),
        },
        'by_type': {
            'story': len([i for i in all_issues if i.issue_type == 'story']),
            'task': len([i for i in all_issues if i.issue_type == 'task']),
            'bug': len([i for i in all_issues if i.issue_type == 'bug']),
            'epic': len([i for i in all_issues if i.issue_type == 'epic']),
        }
    }
    
    # Get recent updates
    updates = ProjectUpdate.query.filter_by(project_id=project_id).order_by(
        ProjectUpdate.date.desc()).limit(10).all()
    
    # Calculate average status and progress
    if updates:
        avg_progress = sum(u.progress_percentage or 0 for u in updates) / len(updates)
        avg_hours = sum(u.hours_worked or 0 for u in updates)
    else:
        avg_progress = 0
        avg_hours = 0
    
    stats['avg_progress'] = int(avg_progress)
    stats['total_hours_worked'] = avg_hours
    stats['recent_updates'] = updates
    
    return render_template('reports.html',
                         project=project,
                         stats=stats)

@app.route('/project/<int:project_id>/add-status', methods=['GET', 'POST'])
@login_required
def add_status_update(project_id):
    """Add status update/report for project"""
    project = Project.query.get_or_404(project_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        flash('You do not have access to this project', 'error')
        abort(403)
    
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            
            update = ProjectUpdate(
                project_id=project_id,
                user_id=session['user_id'],
                update_text=sanitize_input(data.get('description', '')),
                status=data.get('status', 'on_track'),
                progress_percentage=int(data.get('progress', 0)),
                hours_worked=float(data.get('hours_worked', 0)),
                team_members_count=int(data.get('team_members', 0)) if data.get('team_members') else None,
                estimated_completion_days=float(data.get('completion_days', 0)) if data.get('completion_days') else None,
            )
            
            if data.get('blockers'):
                update.blockers = sanitize_input(data.get('blockers'))
            if data.get('notes'):
                update.completion_notes = sanitize_input(data.get('notes'))
            
            db.session.add(update)
            
            # Auto-update project status based on latest update
            if update.status == 'on_track':
                project.status = 'Active'
            elif update.status == 'at_risk':
                project.status = 'At Risk'
            elif update.status == 'blocked':
                project.status = 'Blocked'
            
            db.session.commit()
            
            # Log audit trail
            log_audit(session['user_id'], 'STATUS_UPDATE_ADDED', 
                     f'Added status update for project {project.name}: {update.status}')
            
            if request.is_json:
                return jsonify({'success': True, 'id': update.id}), 201
            
            flash('Status update added successfully!', 'success')
            return redirect(url_for('project_reports', project_id=project_id))
        
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 400
            flash(f'Error adding status update: {str(e)}', 'error')
    
    return render_template('add_status.html', project=project)

@app.route('/api/project/<int:project_id>/status-update', methods=['POST'])
@login_required
def api_add_status_update(project_id):
    """API endpoint for adding status updates"""
    project = Project.query.get_or_404(project_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    try:
        update = ProjectUpdate(
            project_id=project_id,
            user_id=session['user_id'],
            update_text=sanitize_input(data.get('description', '')),
            status=data.get('status', 'on_track'),
            progress_percentage=int(data.get('progress', 0)),
            hours_worked=float(data.get('hours_worked', 0)),
            team_members_count=int(data.get('team_members', 0)) if data.get('team_members') else None,
            estimated_completion_days=float(data.get('completion_days', 0)) if data.get('completion_days') else None,
        )
        
        if data.get('blockers'):
            update.blockers = sanitize_input(data.get('blockers'))
        if data.get('notes'):
            update.completion_notes = sanitize_input(data.get('notes'))
        
        db.session.add(update)
        
        # Auto-update project status
        if update.status == 'on_track':
            project.status = 'Active'
        elif update.status == 'at_risk':
            project.status = 'At Risk'
        elif update.status == 'blocked':
            project.status = 'Blocked'
        
        db.session.commit()
        
        log_audit(session['user_id'], 'STATUS_UPDATE_ADDED',
                 f'Added status update for project {project.name}')
        
        return jsonify({
            'success': True,
            'id': update.id,
            'status': update.status,
            'progress': update.progress_percentage,
            'date': update.date.strftime('%Y-%m-%d %H:%M:%S'),
            'user': user.username
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/project/<int:project_id>/status-updates', methods=['GET'])
@login_required
def api_get_status_updates(project_id):
    """Get status updates for a project"""
    project = Project.query.get_or_404(project_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        return jsonify({'error': 'Access denied'}), 403
    
    updates = ProjectUpdate.query.filter_by(project_id=project_id).order_by(
        ProjectUpdate.date.desc()).limit(50).all()
    
    return jsonify({
        'updates': [
            {
                'id': u.id,
                'description': u.update_text,
                'status': u.status,
                'progress': u.progress_percentage,
                'hours_worked': u.hours_worked,
                'blockers': u.blockers,
                'notes': u.completion_notes,
                'team_members': u.team_members_count,
                'completion_days': u.estimated_completion_days,
                'date': u.date.strftime('%Y-%m-%d %H:%M:%S'),
                'user': u.user.username
            }
            for u in updates
        ]
    })

@app.route('/project/<int:project_id>/issues')
@login_required
def project_issues(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        flash('You do not have access to this project', 'error')
        abort(403)
    
    # Get filter parameters
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    assignee_filter = request.args.get('assignee')
    
    query = Issue.query.filter_by(project_id=project_id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    if assignee_filter:
        query = query.filter_by(assignee_id=int(assignee_filter))
    
    issues = query.all()
    
    return render_template('issues_list.html',
                         project=project,
                         issues=issues)

@app.route('/project/<int:project_id>/components')
@login_required
def project_components(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check access
    user = User.query.get(session['user_id'])
    if user.role != 'admin' and project.team_id != user.team_id:
        flash('You do not have access to this project', 'error')
        abort(403)
    
    return render_template('components.html', project=project)

# ============= REPORTS AND ADMIN ROUTES =============

@app.route('/reports')
@login_required
def reports():
    filter_type = request.args.get('filter', 'all')
    sort_by = request.args.get('sort', 'date')
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    if filter_type not in ['daily', 'weekly', 'monthly', 'all']:
        filter_type = 'all'
    
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
    
    # Get ONLY current user's updates (not team's)
    updates = ProjectUpdate.query.filter(
        ProjectUpdate.user_id == user.id,
        ProjectUpdate.date >= start_date
    ).all()
    
    # Apply search filter
    if search_query:
        search_lower = search_query.lower()
        updates = [u for u in updates if search_lower in (u.project.name.lower() if u.project else '')]
    
    # Apply status filter
    if status_filter and status_filter in ['on_track', 'at_risk', 'blocked']:
        updates = [u for u in updates if u.status == status_filter]
    
    # Apply sorting
    if sort_by == 'progress':
        updates.sort(key=lambda u: u.progress_percentage or 0, reverse=True)
    elif sort_by == 'status':
        status_order = {'blocked': 0, 'at_risk': 1, 'on_track': 2}
        updates.sort(key=lambda u: status_order.get(u.status, 3))
    else:
        updates.sort(key=lambda u: u.date, reverse=True)
    
    # Get user's projects
    user_projects = Project.query.join(ProjectUpdate).filter(
        ProjectUpdate.user_id == user.id
    ).distinct().all() if updates else []
    
    # Convert projects to serializable format
    projects_list = [{'id': p.id, 'name': p.name, 'key': p.key} for p in user_projects]
    
    # Calculate statistics
    all_user_updates = ProjectUpdate.query.filter(
        ProjectUpdate.user_id == user.id,
        ProjectUpdate.date >= start_date
    ).all()
    
    on_track_count = sum(1 for u in all_user_updates if u.status == 'on_track')
    at_risk_count = sum(1 for u in all_user_updates if u.status == 'at_risk')
    blocked_count = sum(1 for u in all_user_updates if u.status == 'blocked')
    avg_progress = sum(u.progress_percentage or 0 for u in all_user_updates) / len(all_user_updates) if all_user_updates else 0
    
    return render_template('reports.html', 
                         updates=updates, 
                         projects=projects_list,
                         filter_type=filter_type,
                         sort_by=sort_by,
                         search_query=search_query,
                         status_filter=status_filter,
                         stats={
                             'on_track': on_track_count,
                             'at_risk': at_risk_count,
                             'blocked': blocked_count,
                             'total': len(all_user_updates),
                             'avg_progress': int(avg_progress)
                         })

@app.route('/reports/add-report', methods=['POST'])
@login_required
def add_report():
    try:
        data = request.get_json() if request.is_json else request.form
        
        project_id = data.get('project_id')
        reporting_period = data.get('reporting_period', 'daily')
        status = data.get('status', 'on_track')
        progress_percentage = int(data.get('progress_percentage', 0))
        update_text = data.get('description', '')
        hours_worked = float(data.get('hours_worked', 0)) if data.get('hours_worked') else 0
        team_members_count = int(data.get('team_members', 0)) if data.get('team_members') else 0
        estimated_completion_days = float(data.get('completion_days', 0)) if data.get('completion_days') else 0
        blockers = data.get('blockers', '')
        
        if not project_id or not update_text or not status:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if status not in ['on_track', 'at_risk', 'blocked']:
            return jsonify({'error': 'Invalid status'}), 400
        
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        user = User.query.get(session['user_id'])
        
        new_update = ProjectUpdate(
            project_id=project_id,
            user_id=user.id,
            update_text=update_text,
            status=status,
            progress_percentage=progress_percentage,
            reporting_period=reporting_period,
            hours_worked=hours_worked,
            team_members_count=team_members_count,
            estimated_completion_days=estimated_completion_days,
            blockers=blockers,
            date=datetime.utcnow()
        )
        
        db.session.add(new_update)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Report added successfully', 'id': new_update.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
    workflow_type = request.form.get('workflow_type', 'agile')
    team_id = request.form.get('team_id')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    valid_statuses = ['Not Started', 'In Progress', 'On Hold', 'Completed']
    if status not in valid_statuses:
        flash('Invalid project status', 'error')
        return redirect(url_for('admin_projects'))
    
    if workflow_type not in ['agile', 'waterfall', 'hybrid']:
        workflow_type = 'agile'
    
    if not name:
        flash('Project name is required', 'error')
        return redirect(url_for('admin_projects'))
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.utcnow()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
    
    project = Project(
        name=name,
        status=status,
        workflow_type=workflow_type,
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

@app.route('/gantt')
@login_required
def gantt_chart():
    user = User.query.get(session['user_id'])
    
    if user.role != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('dashboard'))
    
    projects = Project.query.all()
    teams = Team.query.all()
    
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
    
    return render_template('gantt_chart.html', gantt_data=gantt_data, teams=teams)

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
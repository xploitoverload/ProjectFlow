# app/routes/projects.py
"""
Project Routes
Handles project views, kanban boards, and issue management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, jsonify
from app.middleware import login_required, project_access_required, permission_required
from app.services import ProjectService, IssueService, ReportService
from app.utils.security import validate_csrf_token, sanitize_input
from app.security.validation import sanitize_html, InputValidator, validate_file_upload
from app.security.audit import log_security_event
from app.models import db

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/<int:project_id>')
@login_required
@project_access_required
def project_detail(project_id):
    """Project detail view."""
    from app.models import ProjectUpdate
    
    project = ProjectService.get_project_by_id(project_id)
    updates = ProjectUpdate.query.filter_by(project_id=project_id)\
        .order_by(ProjectUpdate.date.desc()).all()
    
    return render_template('project_detail.html',
                          project=project,
                          updates=updates)


@projects_bp.route('/<int:project_id>/add_update', methods=['POST'])
@login_required
@project_access_required
def add_update(project_id):
    """Add project update."""
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('projects.project_detail', project_id=project_id))
    
    update_text = request.form.get('update_text', '').strip()
    hours_worked = request.form.get('hours_worked', 0)
    
    if not update_text:
        flash('Update text cannot be empty', 'error')
        return redirect(url_for('projects.project_detail', project_id=project_id))
    
    try:
        hours = float(hours_worked)
        if hours < 0 or hours > 24:
            flash('Hours must be between 0 and 24', 'error')
            return redirect(url_for('projects.project_detail', project_id=project_id))
    except ValueError:
        hours = 0
    
    success, update, message = ReportService.create_status_update(
        project_id=project_id,
        user_id=session['user_id'],
        description=update_text,
        hours_worked=hours
    )
    
    if success:
        flash('Update added successfully', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('projects.project_detail', project_id=project_id))


@projects_bp.route('/<int:project_id>/kanban')
@login_required
@project_access_required
def project_kanban(project_id):
    """Kanban board view."""
    from app.models import User
    
    project = ProjectService.get_project_by_id(project_id)
    
    # Get issues grouped by status
    issues_by_status = IssueService.get_issues_grouped_by_status(project_id)
    
    # Calculate statistics
    all_issues = []
    for status_issues in issues_by_status.values():
        all_issues.extend(status_issues)
    
    total_issues = len(all_issues)
    completed_issues = len(issues_by_status.get('done', [])) + len(issues_by_status.get('closed', []))
    completed_percentage = int((completed_issues / total_issues * 100)) if total_issues > 0 else 0
    total_hours = sum(issue.time_estimate or 0 for issue in all_issues)
    
    # Get team members
    team_members_list = []
    if project.team:
        team_members_list = User.query.filter_by(team_id=project.team_id).all()
    
    # Provide canonical status keys and user-facing labels for the template
    statuses = IssueService.VALID_STATUSES
    status_labels = {
        'open': 'Open',
        'todo': 'To Do',
        'in_progress': 'In Progress',
        'code_review': 'Code Review',
        'testing': 'Testing',
        'ready_deploy': 'Ready to Deploy',
        'done': 'Done',
        'closed': 'Closed',
        'reopened': 'Reopened'
    }

    return render_template('kanban_board.html',
                          project=project,
                          issues_by_status=issues_by_status,
                          statuses=statuses,
                          status_labels=status_labels,
                          total_issues=total_issues,
                          completed_percentage=completed_percentage,
                          total_hours=total_hours,
                          team_members=len(team_members_list),
                          team_members_list=team_members_list)


@projects_bp.route('/<int:project_id>/issue/add', methods=['POST'])
@login_required
@project_access_required
def add_issue(project_id):
    """Add a new issue."""
    # Flask-WTF automatically validates CSRF tokens
    # No manual validation needed
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    priority = request.form.get('priority', 'medium')
    issue_type = request.form.get('issue_type', 'task')
    status = request.form.get('status', 'todo')
    assignee_id = request.form.get('assignee_id')
    time_estimate = request.form.get('time_estimate', 0)
    
    # Convert time_estimate to float
    try:
        time_estimate = float(time_estimate) if time_estimate else 0
    except (ValueError, TypeError):
        time_estimate = 0
    
    due_date = request.form.get('due_date')
    
    success, issue, message = IssueService.create_issue(
        project_id=project_id,
        title=title,
        description=description,
        priority=priority,
        issue_type=issue_type,
        status=status,
        assignee_id=assignee_id,
        reporter_id=session['user_id'],
        time_estimate=time_estimate,
        due_date=due_date
    )
    
    if success:
        flash('Issue created successfully', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('projects.project_kanban', project_id=project_id))

@projects_bp.route('/<int:project_id>/issue/<int:issue_id>/delete', methods=['POST'])
@login_required
@project_access_required
def delete_issue(project_id, issue_id):
    """Delete an issue."""
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('projects.project_kanban', project_id=project_id))
    
    success, message = IssueService.delete_issue(
        issue_id=issue_id,
        deleted_by=session['user_id']
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('projects.project_kanban', project_id=project_id))


@projects_bp.route('/<int:project_id>/issue/<int:issue_id>/status', methods=['POST'])
@login_required
@project_access_required
def update_issue_status(project_id, issue_id):
    """Update issue status from form or AJAX."""
    from app.models import Issue
    
    issue = Issue.query.get_or_404(issue_id)
    if issue.project_id != project_id:
        abort(404)
    
    # Handle JSON requests (from drag-and-drop)
    if request.is_json:
        new_status = request.json.get('status')
        csrf_token = request.headers.get('X-CSRFToken')
    else:
        # Handle form requests
        new_status = request.form.get('status')
        csrf_token = request.form.get('csrf_token')
    
    if not validate_csrf_token(csrf_token):
        if request.is_json:
            return jsonify({'success': False, 'message': 'Security error'}), 403
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    if not new_status:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Status is required'}), 400
        flash('Status is required', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    success, updated_issue, message = IssueService.update_status(
        issue_id=issue_id,
        new_status=new_status,
        updated_by=session['user_id']
    )
    
    if request.is_json:
        return jsonify({
            'success': success,
            'message': message,
            'issue': {
                'id': updated_issue.id,
                'key': updated_issue.key,
                'status': updated_issue.status
            } if success else None
        })
    
    if success:
        flash('Status updated successfully', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))



@projects_bp.route('/<int:project_id>/issue/<int:issue_id>')
@login_required
@project_access_required
def issue_view(project_id, issue_id):
    """View issue detail page."""
    from app.models import Issue, Comment, User, Label
    
    project = ProjectService.get_project_by_id(project_id)
    issue = Issue.query.get_or_404(issue_id)
    
    if issue.project_id != project_id:
        abort(404)
    
    # Get comments
    comments = Comment.query.filter_by(issue_id=issue_id).order_by(Comment.created_at.desc()).all()
    
    # Get team members for assignment
    team_members = []
    if project.team:
        team_members = User.query.filter_by(team_id=project.team_id).all()
    
    # Get labels
    labels = Label.query.filter_by(project_id=project_id).all()
    
    return render_template('issue_detail.html',
                          project=project,
                          issue=issue,
                          comments=comments,
                          team_members=team_members,
                          labels=labels)


@projects_bp.route('/<int:project_id>/issue/<int:issue_id>/edit', methods=['GET', 'POST'])
@login_required
@project_access_required
def edit_issue(project_id, issue_id):
    """Edit issue page."""
    from app.models import Issue, User, Label, Sprint, Epic
    
    project = ProjectService.get_project_by_id(project_id)
    issue = Issue.query.get_or_404(issue_id)
    
    if issue.project_id != project_id:
        abort(404)
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('projects.edit_issue', project_id=project_id, issue_id=issue_id))
        
        data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', ''),
            'priority': request.form.get('priority', 'medium'),
            'status': request.form.get('status', issue.status),
            'issue_type': request.form.get('issue_type', 'task'),
            'assignee_id': request.form.get('assignee_id') or None,
            'story_points': request.form.get('story_points') or None,
            'time_estimate': request.form.get('time_estimate') or None,
            'due_date': request.form.get('due_date') or None,
            'sprint_id': request.form.get('sprint_id') or None,
            'epic_id': request.form.get('epic_id') or None,
        }
        
        success, updated_issue, message = IssueService.update_issue(
            issue_id=issue_id,
            data=data,
            updated_by=session['user_id']
        )
        
        if success:
            flash('Issue updated successfully', 'success')
            return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
        else:
            flash(message, 'error')
    
    # Get team members for assignment
    team_members = []
    if project.team:
        team_members = User.query.filter_by(team_id=project.team_id).all()
    
    # Get labels, sprints, epics
    labels = Label.query.filter_by(project_id=project_id).all()
    sprints = Sprint.query.filter_by(project_id=project_id).all()
    epics = Epic.query.filter_by(project_id=project_id).all()
    
    return render_template('issue_edit.html',
                          project=project,
                          issue=issue,
                          team_members=team_members,
                          labels=labels,
                          sprints=sprints,
                          epics=epics)


@projects_bp.route('/<int:project_id>/timeline')
@login_required
@project_access_required
def project_timeline(project_id):
    """Timeline/Gantt view for project issues."""
    from app.models import Issue, IssueLink
    
    project = ProjectService.get_project_by_id(project_id)
    issues = Issue.query.filter_by(project_id=project_id).all()
    
    # Get dependencies
    dependencies = IssueLink.query.join(
        Issue, IssueLink.source_issue_id == Issue.id
    ).filter(Issue.project_id == project_id).all()
    
    return render_template('timeline_view.html',
                          project=project,
                          issues=issues,
                          dependencies=dependencies)


@projects_bp.route('/<int:project_id>/workflow')
@login_required
@project_access_required
def project_workflow(project_id):
    """Workflow diagram view."""
    from app.models import Issue, WorkflowTransition
    
    project = ProjectService.get_project_by_id(project_id)
    
    # Get recent transitions
    recent_transitions = WorkflowTransition.query.join(
        Issue, WorkflowTransition.issue_id == Issue.id
    ).filter(Issue.project_id == project_id).order_by(
        WorkflowTransition.timestamp.desc()
    ).limit(20).all()
    
    return render_template('workflow_diagram.html',
                          project=project,
                          recent_transitions=recent_transitions)


@projects_bp.route('/<int:project_id>/reports')
@login_required
@project_access_required
def project_reports(project_id):
    """Project reports and analytics."""
    project = ProjectService.get_project_by_id(project_id)
    stats = ProjectService.get_project_statistics(project_id)
    
    # Get recent updates
    from app.models import ProjectUpdate
    updates = ProjectUpdate.query.filter_by(project_id=project_id)\
        .order_by(ProjectUpdate.date.desc()).limit(10).all()
    
    stats['recent_updates'] = updates
    
    return render_template('reports.html',
                          project=project,
                          stats=stats)


@projects_bp.route('/<int:project_id>/add-status', methods=['GET', 'POST'])
@login_required
@project_access_required
def add_status_update(project_id):
    """Add status update page."""
    project = ProjectService.get_project_by_id(project_id)
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('projects.add_status_update', project_id=project_id))
        
        success, update, message = ReportService.create_status_update(
            project_id=project_id,
            user_id=session['user_id'],
            description=request.form.get('description', ''),
            status=request.form.get('status', 'on_track'),
            progress=int(request.form.get('progress', 0)),
            hours_worked=float(request.form.get('hours_worked', 0)),
            blockers=request.form.get('blockers'),
            notes=request.form.get('notes'),
            team_members=request.form.get('team_members'),
            completion_days=request.form.get('completion_days'),
            reporting_period=request.form.get('reporting_period', 'daily')
        )
        
        if success:
            flash('Status update added successfully!', 'success')
            return redirect(url_for('projects.project_reports', project_id=project_id))
        else:
            flash(message, 'error')
    
    return render_template('add_status.html', project=project)


# =============================================
# File Attachment Routes
# =============================================

@projects_bp.route('/<int:project_id>/issue/<int:issue_id>/attachments', methods=['POST'])
@login_required
@project_access_required
def upload_attachment(project_id, issue_id):
    """Upload file attachment to an issue with security validation."""
    import os
    from werkzeug.utils import secure_filename
    from app.models import Issue, Attachment, db
    from flask import current_app
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    issue = Issue.query.get_or_404(issue_id)
    if issue.project_id != project_id:
        abort(404)
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    # Use secure file validation (magic bytes + extension check)
    is_valid, error = validate_file_upload(file)
    if not is_valid:
        log_security_event(
            'INVALID_FILE_UPLOAD',
            user_id=session.get('user_id'),
            details=f"File upload rejected: {error}",
            severity='WARNING'
        )
        flash(error, 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    # Create uploads directory securely
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', str(project_id))
    os.makedirs(upload_folder, exist_ok=True)
    
    # Secure filename and prevent path traversal
    original_filename = file.filename
    filename = secure_filename(file.filename)
    if not filename:
        flash('Invalid filename', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    # Add timestamp to avoid conflicts and prevent enumeration
    import time
    import secrets
    unique_filename = f"{int(time.time())}_{secrets.token_hex(8)}_{filename}"
    filepath = os.path.join(upload_folder, unique_filename)
    
    # Ensure filepath stays within upload folder (double-check)
    if not os.path.abspath(filepath).startswith(os.path.abspath(upload_folder)):
        log_security_event(
            'PATH_TRAVERSAL_ATTEMPT',
            user_id=session.get('user_id'),
            details=f"Path traversal attempt in filename: {original_filename}",
            severity='CRITICAL'
        )
        abort(400)
    
    file.save(filepath)
    
    # Create attachment record
    attachment = Attachment(
        issue_id=issue_id,
        filename=filename,
        filepath=filepath,
        file_size=os.path.getsize(filepath),
        mime_type=file.content_type,
        uploaded_by=session['user_id']
    )
    db.session.add(attachment)
    db.session.commit()
    
    log_security_event(
        'FILE_UPLOADED',
        user_id=session.get('user_id'),
        details=f"File uploaded to issue {issue_id}: {filename}",
        severity='INFO'
    )
    
    flash('File uploaded successfully', 'success')
    return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))


@projects_bp.route('/<int:project_id>/issue/<int:issue_id>/attachment/<int:attachment_id>/delete', methods=['POST'])
@login_required
@project_access_required
def delete_attachment(project_id, issue_id, attachment_id):
    """Delete file attachment with proper authorization."""
    import os
    from app.models import Issue, Attachment, db
    from app.security.authorization import check_ownership
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    issue = Issue.query.get_or_404(issue_id)
    if issue.project_id != project_id:
        abort(404)
    
    attachment = Attachment.query.get_or_404(attachment_id)
    if attachment.issue_id != issue_id:
        abort(404)
    
    # Check authorization: owner, admin, or manager
    user_role = session.get('role', 'user')
    is_owner = check_ownership(attachment, session.get('user_id'), 'uploaded_by')
    is_privileged = user_role in ['admin', 'super_admin', 'manager']
    
    if not is_owner and not is_privileged:
        log_security_event(
            'UNAUTHORIZED_DELETE_ATTEMPT',
            user_id=session.get('user_id'),
            details=f"Unauthorized attempt to delete attachment {attachment_id}",
            severity='WARNING'
        )
        flash('You do not have permission to delete this attachment', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    # Delete file from disk
    if os.path.exists(attachment.filepath):
        os.remove(attachment.filepath)
    
    db.session.delete(attachment)
    db.session.commit()
    
    log_security_event(
        'ATTACHMENT_DELETED',
        user_id=session.get('user_id'),
        details=f"Attachment {attachment_id} deleted from issue {issue_id}",
        severity='INFO'
    )
    
    flash('Attachment deleted successfully', 'success')
    return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))


# =============================================
# Sprint Management Routes
# =============================================

@projects_bp.route('/<int:project_id>/sprints')
@login_required
@project_access_required
def sprints_list(project_id):
    """List all sprints for a project."""
    from app.models import Sprint, Issue
    
    project = ProjectService.get_project_by_id(project_id)
    sprints = Sprint.query.filter_by(project_id=project_id).order_by(Sprint.start_date.desc()).all()
    
    # Calculate sprint statistics
    for sprint in sprints:
        sprint.issue_count = Issue.query.filter_by(sprint_id=sprint.id).count()
        sprint.completed_count = Issue.query.filter_by(sprint_id=sprint.id, status='done').count()
    
    return render_template('sprints.html', project=project, sprints=sprints)


@projects_bp.route('/<int:project_id>/sprint/add', methods=['GET', 'POST'])
@login_required
@project_access_required
def add_sprint(project_id):
    """Create a new sprint."""
    from app.models import Sprint, db
    from datetime import datetime
    
    project = ProjectService.get_project_by_id(project_id)
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('projects.add_sprint', project_id=project_id))
        
        name = request.form.get('name', '').strip()
        goal = request.form.get('goal', '').strip()
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        if not name:
            flash('Sprint name is required', 'error')
            return redirect(url_for('projects.add_sprint', project_id=project_id))
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        sprint = Sprint(
            project_id=project_id,
            name=name,
            goal=goal,
            start_date=start_date,
            end_date=end_date,
            status='planned'
        )
        db.session.add(sprint)
        db.session.commit()
        
        flash('Sprint created successfully', 'success')
        return redirect(url_for('projects.sprints_list', project_id=project_id))
    
    return render_template('sprint_form.html', project=project, sprint=None)


@projects_bp.route('/<int:project_id>/sprint/<int:sprint_id>/edit', methods=['GET', 'POST'])
@login_required
@project_access_required
def edit_sprint(project_id, sprint_id):
    """Edit an existing sprint."""
    from app.models import Sprint, db
    from datetime import datetime
    
    project = ProjectService.get_project_by_id(project_id)
    sprint = Sprint.query.get_or_404(sprint_id)
    
    if sprint.project_id != project_id:
        abort(404)
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('projects.edit_sprint', project_id=project_id, sprint_id=sprint_id))
        
        sprint.name = request.form.get('name', '').strip()
        sprint.goal = request.form.get('goal', '').strip()
        sprint.status = request.form.get('status', 'planned')
        
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        sprint.start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        sprint.end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        db.session.commit()
        
        flash('Sprint updated successfully', 'success')
        return redirect(url_for('projects.sprints_list', project_id=project_id))
    
    return render_template('sprint_form.html', project=project, sprint=sprint)


@projects_bp.route('/<int:project_id>/sprint/<int:sprint_id>/delete', methods=['POST'])
@login_required
@project_access_required
def delete_sprint(project_id, sprint_id):
    """Delete a sprint."""
    from app.models import Sprint, Issue, db
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('projects.sprints_list', project_id=project_id))
    
    sprint = Sprint.query.get_or_404(sprint_id)
    if sprint.project_id != project_id:
        abort(404)
    
    # Remove sprint association from issues
    Issue.query.filter_by(sprint_id=sprint_id).update({'sprint_id': None})
    
    db.session.delete(sprint)
    db.session.commit()
    
    flash('Sprint deleted successfully', 'success')
    return redirect(url_for('projects.sprints_list', project_id=project_id))


# =============================================
# Epic Management Routes
# =============================================

@projects_bp.route('/<int:project_id>/epics')
@login_required
@project_access_required
def epics_list(project_id):
    """List all epics for a project."""
    from app.models import Epic, Issue
    
    project = ProjectService.get_project_by_id(project_id)
    epics = Epic.query.filter_by(project_id=project_id).order_by(Epic.created_at.desc()).all()
    
    # Calculate epic statistics
    for epic in epics:
        epic.issue_count = Issue.query.filter_by(epic_id=epic.id).count()
        epic.completed_count = Issue.query.filter_by(epic_id=epic.id, status='done').count()
    
    return render_template('epics.html', project=project, epics=epics)


@projects_bp.route('/<int:project_id>/epic/add', methods=['GET', 'POST'])
@login_required
@project_access_required
def add_epic(project_id):
    """Create a new epic."""
    from app.models import Epic, db
    
    project = ProjectService.get_project_by_id(project_id)
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('projects.add_epic', project_id=project_id))
        
        name = request.form.get('name', '').strip()
        summary = request.form.get('summary', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#7C3AED')
        
        if not name:
            flash('Epic name is required', 'error')
            return redirect(url_for('projects.add_epic', project_id=project_id))
        
        epic = Epic(
            project_id=project_id,
            name=name,
            summary=summary,
            description=description,
            color=color,
            status='open'
        )
        db.session.add(epic)
        db.session.commit()
        
        flash('Epic created successfully', 'success')
        return redirect(url_for('projects.epics_list', project_id=project_id))
    
    return render_template('epic_form.html', project=project, epic=None)


@projects_bp.route('/<int:project_id>/epic/<int:epic_id>/edit', methods=['GET', 'POST'])
@login_required
@project_access_required
def edit_epic(project_id, epic_id):
    """Edit an existing epic."""
    from app.models import Epic, db
    
    project = ProjectService.get_project_by_id(project_id)
    epic = Epic.query.get_or_404(epic_id)
    
    if epic.project_id != project_id:
        abort(404)
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('projects.edit_epic', project_id=project_id, epic_id=epic_id))
        
        epic.name = request.form.get('name', '').strip()
        epic.summary = request.form.get('summary', '').strip()
        epic.description = request.form.get('description', '').strip()
        epic.color = request.form.get('color', '#7C3AED')
        epic.status = request.form.get('status', 'open')
        
        db.session.commit()
        
        flash('Epic updated successfully', 'success')
        return redirect(url_for('projects.epics_list', project_id=project_id))
    
    return render_template('epic_form.html', project=project, epic=epic)


@projects_bp.route('/<int:project_id>/epic/<int:epic_id>/delete', methods=['POST'])
@login_required
@project_access_required
def delete_epic(project_id, epic_id):
    """Delete an epic."""
    from app.models import Epic, Issue, db
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('projects.epics_list', project_id=project_id))
    
    epic = Epic.query.get_or_404(epic_id)
    if epic.project_id != project_id:
        abort(404)
    
    # Remove epic association from issues
    Issue.query.filter_by(epic_id=epic_id).update({'epic_id': None})
    
    db.session.delete(epic)
    db.session.commit()
    
    flash('Epic deleted successfully', 'success')
    return redirect(url_for('projects.epics_list', project_id=project_id))


# =============================================
# Label Management Routes
# =============================================

@projects_bp.route('/<int:project_id>/labels')
@login_required
@project_access_required
def labels_list(project_id):
    """List all labels for a project."""
    from app.models import Label
    
    project = ProjectService.get_project_by_id(project_id)
    labels = Label.query.filter_by(project_id=project_id).order_by(Label.name).all()
    
    return render_template('labels.html', project=project, labels=labels)


@projects_bp.route('/<int:project_id>/label/add', methods=['GET', 'POST'])
@login_required
@project_access_required
def add_label(project_id):
    """Create a new label."""
    from app.models import Label, db
    
    project = ProjectService.get_project_by_id(project_id)
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('projects.add_label', project_id=project_id))
        
        name = request.form.get('name', '').strip()
        color = request.form.get('color', '#6B7280')
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Label name is required', 'error')
            return redirect(url_for('projects.add_label', project_id=project_id))
        
        # Check if label already exists
        existing = Label.query.filter_by(project_id=project_id, name=name).first()
        if existing:
            flash('A label with this name already exists', 'error')
            return redirect(url_for('projects.add_label', project_id=project_id))
        
        label = Label(
            project_id=project_id,
            name=name,
            color=color,
            description=description
        )
        db.session.add(label)
        db.session.commit()
        
        flash('Label created successfully', 'success')
        return redirect(url_for('projects.labels_list', project_id=project_id))
    
    return render_template('label_form.html', project=project, label=None)


@projects_bp.route('/<int:project_id>/label/<int:label_id>/edit', methods=['GET', 'POST'])
@login_required
@project_access_required
def edit_label(project_id, label_id):
    """Edit an existing label."""
    from app.models import Label, db
    
    project = ProjectService.get_project_by_id(project_id)
    label = Label.query.get_or_404(label_id)
    
    if label.project_id != project_id:
        abort(404)
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('projects.edit_label', project_id=project_id, label_id=label_id))
        
        label.name = request.form.get('name', '').strip()
        label.color = request.form.get('color', '#6B7280')
        label.description = request.form.get('description', '').strip()
        
        db.session.commit()
        
        flash('Label updated successfully', 'success')
        return redirect(url_for('projects.labels_list', project_id=project_id))
    
    return render_template('label_form.html', project=project, label=label)


@projects_bp.route('/<int:project_id>/label/<int:label_id>/delete', methods=['POST'])
@login_required
@project_access_required
def delete_label(project_id, label_id):
    """Delete a label."""
    from app.models import Label, db
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('projects.labels_list', project_id=project_id))
    
    label = Label.query.get_or_404(label_id)
    if label.project_id != project_id:
        abort(404)
    
    db.session.delete(label)
    db.session.commit()
    
    flash('Label deleted successfully', 'success')
    return redirect(url_for('projects.labels_list', project_id=project_id))


@projects_bp.route('/<int:project_id>/issue/<int:issue_id>/labels', methods=['POST'])
@login_required
@project_access_required
def update_issue_labels(project_id, issue_id):
    """Add or remove labels from an issue."""
    from app.models import Issue, Label, db
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    issue = Issue.query.get_or_404(issue_id)
    if issue.project_id != project_id:
        abort(404)
    
    # Get selected label IDs
    label_ids = request.form.getlist('label_ids')
    
    # Clear existing labels and add selected ones
    issue.labels = []
    for label_id in label_ids:
        label = Label.query.get(int(label_id))
        if label and label.project_id == project_id:
            issue.labels.append(label)
    
    db.session.commit()
    
    flash('Labels updated successfully', 'success')
    return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))


# =============================================
# Comment Routes
# =============================================

@projects_bp.route('/<int:project_id>/issue/<int:issue_id>/comment', methods=['POST'])
@login_required
@project_access_required
def add_comment(project_id, issue_id):
    """Add a comment to an issue."""
    from app.models import Issue, Comment, db
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    issue = Issue.query.get_or_404(issue_id)
    if issue.project_id != project_id:
        abort(404)
    
    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    comment = Comment(
        issue_id=issue_id,
        author_id=session['user_id'],
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully', 'success')
    return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))


@projects_bp.route('/<int:project_id>/issue/<int:issue_id>/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
@project_access_required
def delete_comment(project_id, issue_id, comment_id):
    """Delete a comment with proper authorization."""
    from app.models import Comment, db
    from app.security.authorization import check_ownership
    
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash('Security error. Please try again.', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    comment = Comment.query.get_or_404(comment_id)
    if comment.issue_id != issue_id:
        abort(404)
    
    # Check authorization: owner, admin, or manager
    user_role = session.get('role', 'user')
    is_owner = check_ownership(comment, session.get('user_id'), 'author_id')
    is_privileged = user_role in ['admin', 'super_admin', 'manager']
    
    if not is_owner and not is_privileged:
        log_security_event(
            'UNAUTHORIZED_DELETE_ATTEMPT',
            user_id=session.get('user_id'),
            details=f"Unauthorized attempt to delete comment {comment_id}",
            severity='WARNING'
        )
        flash('You do not have permission to delete this comment', 'error')
        return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))
    
    db.session.delete(comment)
    db.session.commit()
    
    log_security_event(
        'COMMENT_DELETED',
        user_id=session.get('user_id'),
        details=f"Comment {comment_id} deleted from issue {issue_id}",
        severity='INFO'
    )
    
    flash('Comment deleted successfully', 'success')
    return redirect(url_for('projects.issue_view', project_id=project_id, issue_id=issue_id))


# =============================================
# Additional Project View Routes
# =============================================

@projects_bp.route('/<int:project_id>/backlog')
@login_required
@project_access_required
def project_backlog(project_id):
    """Project backlog view - lists all issues not in active sprints."""
    from app.models import Issue, Sprint
    
    project = ProjectService.get_project_by_id(project_id)
    
    # Get all issues that are not assigned to an active sprint or have no sprint
    issues = Issue.query.filter_by(project_id=project_id)\
        .filter((Issue.sprint_id.is_(None)) | 
                (Issue.sprint_id.in_(
                    db.session.query(Sprint.id)
                    .filter(Sprint.project_id == project_id)
                    .filter(Sprint.status.in_(['planning', 'completed']))
                )))\
        .order_by(Issue.created_at.desc())\
        .all()
    
    return render_template('backlog.html', project=project, issues=issues)


@projects_bp.route('/<int:project_id>/issues')
@login_required
@project_access_required
def project_issues(project_id):
    """List all issues for a project."""
    from app.models import Issue
    
    project = ProjectService.get_project_by_id(project_id)
    
    # Get filter parameters
    status_filter = request.args.get('status')
    type_filter = request.args.get('type')
    assignee_filter = request.args.get('assignee')
    
    query = Issue.query.filter_by(project_id=project_id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(issue_type=type_filter)
    if assignee_filter:
        query = query.filter_by(assignee_id=int(assignee_filter))
    
    issues = query.order_by(Issue.created_at.desc()).all()
    
    return render_template('issues_list.html', project=project, issues=issues)


@projects_bp.route('/<int:project_id>/board')
@login_required
@project_access_required
def project_board(project_id):
    """Alias for kanban board."""
    return redirect(url_for('projects.project_kanban', project_id=project_id))


@projects_bp.route('/<int:project_id>/code')
@login_required
@project_access_required
def project_code(project_id):
    """Project code repository view (placeholder)."""
    project = ProjectService.get_project_by_id(project_id)
    flash('Code repository integration coming soon!', 'info')
    return redirect(url_for('projects.project_detail', project_id=project_id))


@projects_bp.route('/<int:project_id>/security')
@login_required
@project_access_required
def project_security(project_id):
    """Project security dashboard (placeholder)."""
    project = ProjectService.get_project_by_id(project_id)
    flash('Security dashboard coming soon!', 'info')
    return redirect(url_for('projects.project_detail', project_id=project_id))


@projects_bp.route('/<int:project_id>/releases')
@login_required
@project_access_required
def project_releases(project_id):
    """Project releases view (placeholder)."""
    project = ProjectService.get_project_by_id(project_id)
    flash('Release management coming soon!', 'info')
    return redirect(url_for('projects.project_detail', project_id=project_id))


@projects_bp.route('/<int:project_id>/deployments')
@login_required
@project_access_required
def project_deployments(project_id):
    """Project deployments view (placeholder)."""
    project = ProjectService.get_project_by_id(project_id)
    flash('Deployment tracking coming soon!', 'info')
    return redirect(url_for('projects.project_detail', project_id=project_id))


@projects_bp.route('/<int:project_id>/settings')
@login_required
@project_access_required
def project_settings(project_id):
    """Project settings page."""
    from app.models import User, Team
    
    project = ProjectService.get_project_by_id(project_id)
    
    # Check if user has permission to edit project settings
    user = User.query.get(session['user_id'])
    
    if user.role not in ['admin', 'super_admin'] and project.owner_id != user.id:
        flash('You do not have permission to edit project settings', 'error')
        return redirect(url_for('projects.project_detail', project_id=project_id))
    
    teams = Team.query.all()
    return render_template('project_settings.html', project=project, teams=teams)


# app/routes/api.py
"""
API Routes (v1)
RESTful API endpoints with proper validation and authentication.
All endpoints require authentication and include IDOR prevention.
"""

from flask import Blueprint, request, jsonify, session
from app.middleware.auth import api_auth_required, rate_limit_check
from app.services import ProjectService, IssueService, ReportService
from app.utils.security import sanitize_input
from app.security.audit import log_security_event
from app.security.validation import InputValidator, sanitize_html

api_bp = Blueprint('api', __name__)


def check_project_access(project_id):
    """
    Check if the current user has access to a project.
    Returns (has_access: bool, project: Project or None).
    """
    from app.models import User
    
    user = User.query.get(session.get('user_id'))
    if not user:
        return False, None
    
    project = ProjectService.get_project_by_id(project_id)
    if not project:
        return False, None
    
    # Admin/super_admin can access all
    if user.role in ['admin', 'super_admin']:
        return True, project
    
    # Check team membership
    if project.team_id and user.team_id == project.team_id:
        return True, project
    
    # Log suspicious access
    log_security_event(
        'IDOR_ATTEMPT',
        user_id=user.id,
        details=f"User attempted to access project {project_id} without authorization",
        severity='WARNING'
    )
    return False, None


# ============= PROJECT APIs =============

@api_bp.route('/projects', methods=['GET'])
@api_auth_required
def get_projects():
    """Get all accessible projects."""
    from app.models import User
    
    user = User.query.get(session['user_id'])
    projects = ProjectService.get_user_accessible_projects(user)
    
    return jsonify({
        'success': True,
        'data': [{
            'id': p.id,
            'name': p.name,
            'key': p.key,
            'status': p.status,
            'workflow_type': p.workflow_type,
            'team': p.team.name if p.team else None,
            'start_date': p.start_date.isoformat() if p.start_date else None,
            'end_date': p.end_date.isoformat() if p.end_date else None
        } for p in projects]
    })


@api_bp.route('/project/<int:project_id>', methods=['GET'])
@api_auth_required
def get_project(project_id):
    """Get project details."""
    has_access, project = check_project_access(project_id)
    
    if not has_access or not project:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    stats = ProjectService.get_project_statistics(project_id)
    
    return jsonify({
        'success': True,
        'data': {
            'id': project.id,
            'name': project.name,
            'key': project.key,
            'description': project.description,
            'status': project.status,
            'workflow_type': project.workflow_type,
            'team': project.team.name if project.team else None,
            'statistics': stats
        }
    })


@api_bp.route('/project/<int:project_id>/status', methods=['GET'])
@api_auth_required
def get_project_status(project_id):
    """Get project status and recent updates."""
    from app.models import ProjectUpdate
    
    has_access, project = check_project_access(project_id)
    
    if not has_access or not project:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    updates = ReportService.get_project_updates(project_id, limit=5)
    
    latest = updates[0] if updates else None
    
    return jsonify({
        'success': True,
        'data': {
            'project_id': project.id,
            'name': project.name,
            'status': project.status,
            'latest_update': {
                'id': latest.id,
                'status': latest.status,
                'progress': latest.progress_percentage,
                'description': latest.update_text,
                'user': latest.user.username,
                'date': latest.date.isoformat()
            } if latest else None,
            'recent_updates': [{
                'id': u.id,
                'status': u.status,
                'progress': u.progress_percentage,
                'user': u.user.username,
                'date': u.date.isoformat()
            } for u in updates]
        }
    })


# ============= ISSUE APIs =============

@api_bp.route('/project/<int:project_id>/issues', methods=['GET'])
@api_auth_required
def get_issues(project_id):
    """Get issues for a project."""
    has_access, project = check_project_access(project_id)
    
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    filters = {
        'status': request.args.get('status'),
        'priority': request.args.get('priority'),
        'assignee_id': request.args.get('assignee'),
        'issue_type': request.args.get('type')
    }
    
    issues = IssueService.get_issues_by_project(project_id, filters)
    
    return jsonify({
        'success': True,
        'data': [{
            'id': i.id,
            'key': i.key,
            'title': i.title,
            'status': i.status,
            'priority': i.priority,
            'type': i.issue_type,
            'assignee': i.assignee.username if i.assignee else None,
            'due_date': i.due_date.isoformat() if i.due_date else None
        } for i in issues]
    })


@api_bp.route('/project/<int:project_id>/issue/<int:issue_id>', methods=['GET'])
@api_auth_required
def get_issue(project_id, issue_id):
    """Get issue details."""
    has_access, project = check_project_access(project_id)
    
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    issue = IssueService.get_issue_by_id(issue_id)
    
    if not issue or issue.project_id != project_id:
        return jsonify({'success': False, 'error': 'Issue not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
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
            'story_points': issue.story_points,
            'time_estimate': issue.time_estimate,
            'time_spent': issue.time_spent,
            'created_at': issue.created_at.isoformat(),
            'updated_at': issue.updated_at.isoformat(),
            'due_date': issue.due_date.isoformat() if issue.due_date else None,
            'labels': [l.name for l in issue.labels],
            'comments': [{
                'id': c.id,
                'text': c.text,
                'author': c.user.username,
                'created_at': c.created_at.isoformat()
            } for c in issue.comments]
        }
    })


@api_bp.route('/project/<int:project_id>/issue/<int:issue_id>/update_status', methods=['POST'])
@api_auth_required
@rate_limit_check(max_requests=30, window_seconds=60)
def update_issue_status(project_id, issue_id):
    """Update issue status (for drag-and-drop)."""
    has_access, project = check_project_access(project_id)
    
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    issue = IssueService.get_issue_by_id(issue_id)
    
    if not issue or issue.project_id != project_id:
        return jsonify({'success': False, 'error': 'Issue not found'}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'success': False, 'error': 'Status required'}), 400
    
    # Validate status value
    valid_statuses = ['backlog', 'todo', 'in_progress', 'in_review', 'testing', 'blocked', 'done', 'closed']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'error': 'Invalid status value'}), 400
    
    success, updated_issue, message = IssueService.update_status(
        issue_id=issue_id,
        new_status=new_status,
        updated_by=session['user_id']
    )
    
    if success:
        return jsonify({
            'success': True,
            'data': {'new_status': updated_issue.status}
        })
    else:
        return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/project/<int:project_id>/issue/<int:issue_id>/comment', methods=['POST'])
@api_auth_required
@rate_limit_check(max_requests=20, window_seconds=60)
def add_comment(project_id, issue_id):
    """Add a comment to an issue."""
    has_access, project = check_project_access(project_id)
    
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    issue = IssueService.get_issue_by_id(issue_id)
    
    if not issue or issue.project_id != project_id:
        return jsonify({'success': False, 'error': 'Issue not found'}), 404
    
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'success': False, 'error': 'Comment text required'}), 400
    
    # Validate and sanitize comment text
    is_valid, error = InputValidator.validate_string(text, min_length=1, max_length=5000)
    if not is_valid:
        return jsonify({'success': False, 'error': error}), 400
    
    # Sanitize HTML in comment
    text = sanitize_html(text)
    
    success, comment, message = IssueService.add_comment(
        issue_id=issue_id,
        user_id=session['user_id'],
        text=text
    )
    
    if success:
        return jsonify({
            'success': True,
            'data': {
                'id': comment.id,
                'text': comment.text,
                'author': comment.user.username,
                'created_at': comment.created_at.isoformat()
            }
        }), 201
    else:
        return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/project/<int:project_id>/issue/<int:issue_id>/link', methods=['POST'])
@api_auth_required
def link_issues(project_id, issue_id):
    """Link two issues."""
    has_access, project = check_project_access(project_id)
    
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    issue = IssueService.get_issue_by_id(issue_id)
    
    if not issue or issue.project_id != project_id:
        return jsonify({'success': False, 'error': 'Issue not found'}), 404
    
    data = request.get_json()
    target_issue_id = data.get('target_issue_id')
    link_type = data.get('link_type', 'relates_to')
    
    if not target_issue_id:
        return jsonify({'success': False, 'error': 'Target issue required'}), 400
    
    # Validate target issue ID
    try:
        target_issue_id = int(target_issue_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid target issue ID'}), 400
    
    # Validate link type
    valid_link_types = ['relates_to', 'blocks', 'is_blocked_by', 'duplicates', 'is_duplicated_by', 'parent_of', 'child_of']
    if link_type not in valid_link_types:
        return jsonify({'success': False, 'error': 'Invalid link type'}), 400
    
    success, link, message = IssueService.link_issues(
        source_id=issue_id,
        target_id=target_issue_id,
        link_type=link_type,
        created_by=session['user_id']
    )
    
    if success:
        return jsonify({
            'success': True,
            'data': {'link_id': link.id}
        }), 201
    else:
        return jsonify({'success': False, 'error': message}), 400


# ============= STATUS UPDATE APIs =============

@api_bp.route('/project/<int:project_id>/status-update', methods=['POST'])
@api_auth_required
@rate_limit_check(max_requests=10, window_seconds=60)
def add_status_update(project_id):
    """Add a status update to a project."""
    has_access, project = check_project_access(project_id)
    
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    data = request.get_json()
    
    # Validate and sanitize inputs
    description = sanitize_html(data.get('description', ''))
    status = data.get('status', 'on_track')
    
    # Validate status value
    valid_statuses = ['on_track', 'at_risk', 'behind', 'completed', 'blocked']
    if status not in valid_statuses:
        return jsonify({'success': False, 'error': 'Invalid status value'}), 400
    
    try:
        progress = int(data.get('progress', 0))
        hours_worked = float(data.get('hours_worked', 0))
        if progress < 0 or progress > 100:
            return jsonify({'success': False, 'error': 'Progress must be between 0 and 100'}), 400
        if hours_worked < 0 or hours_worked > 24:
            return jsonify({'success': False, 'error': 'Hours must be between 0 and 24'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid numeric values'}), 400
    
    success, update, message = ReportService.create_status_update(
        project_id=project_id,
        user_id=session['user_id'],
        description=description,
        status=status,
        progress=progress,
        hours_worked=hours_worked,
        blockers=sanitize_html(data.get('blockers', '')),
        notes=sanitize_html(data.get('notes', '')),
        team_members=data.get('team_members'),
        completion_days=data.get('completion_days'),
        reporting_period=data.get('reporting_period', 'daily')
    )
    
    if success:
        return jsonify({
            'success': True,
            'data': {
                'id': update.id,
                'status': update.status,
                'progress': update.progress_percentage,
                'date': update.date.isoformat(),
                'user': update.user.username
            }
        }), 201
    else:
        return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/project/<int:project_id>/status-updates', methods=['GET'])
@api_auth_required
def get_status_updates(project_id):
    """Get status updates for a project."""
    has_access, project = check_project_access(project_id)
    
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    # Validate and sanitize query params
    try:
        limit = min(max(int(request.args.get('limit', 50)), 1), 100)  # Between 1 and 100
        offset = max(int(request.args.get('offset', 0)), 0)  # At least 0
    except (ValueError, TypeError):
        limit = 50
        offset = 0
    
    updates = ReportService.get_project_updates(project_id, limit=limit, offset=offset)
    
    return jsonify({
        'success': True,
        'data': [{
            'id': u.id,
            'description': u.update_text,
            'status': u.status,
            'progress': u.progress_percentage,
            'hours_worked': u.hours_worked,
            'blockers': u.blockers,
            'notes': u.completion_notes,
            'team_members': u.team_members_count,
            'completion_days': u.estimated_completion_days,
            'date': u.date.isoformat(),
            'user': u.user.username
        } for u in updates]
    })


# ============= REPORTS API =============

@api_bp.route('/reports/add', methods=['POST'])
@api_auth_required
@rate_limit_check(max_requests=10, window_seconds=60)
def add_report():
    """Add a new report from the reports page."""
    data = request.get_json()
    
    project_id = data.get('project_id')
    if not project_id:
        return jsonify({'success': False, 'error': 'Project ID required'}), 400
    
    # Validate project ID
    try:
        project_id = int(project_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid project ID'}), 400
    
    # Check project access
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    # Validate and sanitize inputs
    description = sanitize_html(data.get('description', ''))
    status = data.get('status', 'on_track')
    
    valid_statuses = ['on_track', 'at_risk', 'behind', 'completed', 'blocked']
    if status not in valid_statuses:
        return jsonify({'success': False, 'error': 'Invalid status value'}), 400
    
    try:
        progress = int(data.get('progress_percentage', 0))
        hours_worked = float(data.get('hours_worked', 0))
        if progress < 0 or progress > 100:
            return jsonify({'success': False, 'error': 'Progress must be between 0 and 100'}), 400
        if hours_worked < 0 or hours_worked > 24:
            return jsonify({'success': False, 'error': 'Hours must be between 0 and 24'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid numeric values'}), 400
    
    success, update, message = ReportService.create_status_update(
        project_id=project_id,
        user_id=session['user_id'],
        description=description,
        status=status,
        progress=progress,
        hours_worked=hours_worked,
        blockers=sanitize_html(data.get('blockers', '')),
        team_members=data.get('team_members'),
        completion_days=data.get('completion_days'),
        reporting_period=data.get('reporting_period', 'daily')
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Report added successfully',
            'data': {'id': update.id}
        }), 201
    else:
        return jsonify({'success': False, 'error': message}), 400


# ============= ERROR HANDLERS =============

@api_bp.errorhandler(400)
def bad_request(e):
    return jsonify({'success': False, 'error': 'Bad request', 'code': 400}), 400


@api_bp.errorhandler(401)
def unauthorized(e):
    return jsonify({'success': False, 'error': 'Unauthorized', 'code': 401}), 401


@api_bp.errorhandler(403)
def forbidden(e):
    return jsonify({'success': False, 'error': 'Forbidden', 'code': 403}), 403


@api_bp.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Not found', 'code': 404}), 404


@api_bp.errorhandler(429)
def rate_limited(e):
    return jsonify({'success': False, 'error': 'Rate limit exceeded', 'code': 429}), 429


@api_bp.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'error': 'Internal server error', 'code': 500}), 500

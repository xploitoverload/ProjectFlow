# app/routes/api.py
"""
API Routes (v1)
RESTful API endpoints with proper validation and authentication.
All endpoints require authentication and include IDOR prevention.
"""

from flask import Blueprint, request, jsonify, session
from flask_login import current_user
from app.models import db, Issue, Project, User
from app.middleware.auth import api_auth_required, rate_limit_check
from app.services import ProjectService, IssueService, ReportService
from app.services.notification_service import NotificationService
from app.utils.security import sanitize_input
from app.security.audit import log_security_event
from app.security.validation import InputValidator, sanitize_html

api_bp = Blueprint('api', __name__)


def check_project_access(project_id):
    """
    Check if the current user has access to a project.
    Delegates to ProjectService.user_has_access for single authoritative policy (DRY).
    Returns (has_access: bool, project: Project or None).
    """
    from app.models import User
    
    user = User.query.get(session.get('user_id'))
    if not user:
        return False, None
    
    project = ProjectService.get_project_by_id(project_id)
    if not project:
        return False, None
    
    if ProjectService.user_has_access(user, project):
        return True, project
    
    # Log suspicious unauthorized access
    log_security_event(
        'IDOR_ATTEMPT',
        user_id=user.id,
        details=f"User attempted to access project {project_id} without authorization",
        severity='WARNING'
    )
    return False, None


# ============= AUTHENTICATION & TOKEN APIs =============

@api_bp.route('/auth/token', methods=['POST'])
def obtain_token():
    """
    Obtain a cryptographically signed Bearer API token.
    Accepts JSON: {"username": "...", "password": "..."}
    or uses current authenticated session.
    """
    from app.services.auth_service import AuthService
    
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    
    user = None
    if username and password:
        success, user, message = AuthService.authenticate(username, password)
        if not success:
            return jsonify({'success': False, 'error': message}), 401
    elif session.get('user_id'):
        user = User.query.get(session['user_id'])
    
    if not user:
        return jsonify({'success': False, 'error': 'Missing credentials or active session'}), 401
        
    token = AuthService.generate_bearer_token(user, expires_sec=86400)
    return jsonify({
        'success': True,
        'token': token,
        'token_type': 'Bearer',
        'expires_in': 86400,
        'user': user.to_dict()
    }), 200


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


@api_bp.route('/projects', methods=['POST'])
@api_auth_required
def create_project_api():
    """Create a new project via API."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body must be JSON'}), 400
        
    name = data.get('name')
    if not name:
        return jsonify({'success': False, 'error': 'Field name is required'}), 400
        
    key = data.get('key')
    description = data.get('description', '')
    status = data.get('status', 'Not Started')
    workflow_type = data.get('workflow_type', 'agile')
    team_id = data.get('team_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    user_id = session.get('user_id')
    
    success, project, message = ProjectService.create_project(
        name=name,
        key=key,
        description=description,
        status=status,
        workflow_type=workflow_type,
        team_id=team_id,
        start_date=start_date,
        end_date=end_date,
        created_by=user_id,
        lead_id=user_id
    )
    
    if not success:
        return jsonify({'success': False, 'error': message}), 400
        
    return jsonify({
        'success': True,
        'data': project.to_dict(),
        'message': 'Project created successfully'
    }), 201


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


@api_bp.route('/project/<int:project_id>/issues', methods=['POST'])
@api_auth_required
def create_issue_api(project_id):
    """Create a new issue in a project via API."""
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found or access denied'}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body must be JSON'}), 400
        
    title = data.get('title')
    if not title:
        return jsonify({'success': False, 'error': 'Field title is required'}), 400
        
    description = data.get('description')
    issue_type = data.get('issue_type', 'task')
    priority = data.get('priority', 'medium')
    status = data.get('status', 'todo')
    assignee_id = data.get('assignee_id')
    sprint_id = data.get('sprint_id')
    epic_id = data.get('epic_id')
    story_points = data.get('story_points')
    due_date = data.get('due_date')
    reporter_id = session.get('user_id')
    
    success, issue, message = IssueService.create_issue(
        project_id=project_id,
        title=title,
        description=description,
        issue_type=issue_type,
        priority=priority,
        status=status,
        assignee_id=assignee_id,
        reporter_id=reporter_id,
        story_points=story_points,
        due_date=due_date,
        sprint_id=sprint_id,
        epic_id=epic_id
    )
    
    if not success:
        return jsonify({'success': False, 'error': message}), 400
        
    # Trigger automation workflows if configured
    try:
        from app.automation.workflow import workflow_engine, TriggerType
        workflow_engine.trigger_workflow(
            TriggerType.ISSUE_CREATED,
            issue.to_dict()
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Workflow execution on issue creation encountered an error: %s", e)
        
    return jsonify({
        'success': True,
        'data': issue.to_dict(),
        'message': 'Issue created successfully'
    }), 201


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


# ============= RECENT ITEMS & STARRED =============

@api_bp.route('/recent-items', methods=['GET'])
@api_auth_required
def get_recent_items():
    """Get recently viewed items for current user."""
    from app.services.recent_items_service import RecentItemsService
    
    limit = request.args.get('limit', 10, type=int)
    item_type = request.args.get('type')  # Optional filter by type
    
    if item_type:
        items = RecentItemsService.get_recent_by_type(item_type, limit=limit)
    else:
        items = RecentItemsService.get_recent_items(limit=limit)
    
    return jsonify({
        'success': True,
        'data': [{
            'id': item.id,
            'type': item.item_type,
            'item_id': item.item_id,
            'title': item.item_title,
            'key': item.item_key,
            'viewed_at': item.viewed_at.isoformat()
        } for item in items]
    })


@api_bp.route('/search/autocomplete', methods=['GET'])
@api_auth_required
def search_autocomplete():
    """Get autocomplete suggestions for search."""
    from app.models import Issue, Project, User
    
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'success': True, 'data': {'issues': [], 'projects': [], 'users': []}})
    
    # Search issues by key or title
    issues = Issue.query.filter(
        db.or_(
            Issue.key.ilike(f'%{query}%'),
            Issue.title.ilike(f'%{query}%')
        )
    ).limit(5).all()
    
    # Search projects by name or key
    projects = Project.query.filter(
        db.or_(
            Project.name.ilike(f'%{query}%'),
            Project.key.ilike(f'%{query}%')
        )
    ).limit(5).all()
    
    # Search users for @mentions or direct username match
    clean_query = query[1:] if query.startswith('@') else query
    users = User.query.filter(
        User.username.ilike(f'%{clean_query}%')
    ).limit(5).all()
    
    return jsonify({
        'success': True,
        'data': {
            'issues': [{
                'id': issue.id,
                'key': issue.key,
                'title': issue.title,
                'type': issue.issue_type,
                'status': issue.status
            } for issue in issues],
            'projects': [{
                'id': project.id,
                'key': project.key,
                'name': project.name
            } for project in projects],
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email
            } for user in users]
        }
    })


@api_bp.route('/starred-items', methods=['GET'])
@api_auth_required
def get_starred_items():
    """Get starred items for current user."""
    from app.services.recent_items_service import StarredItemsService
    
    item_type = request.args.get('type')  # Optional filter by type
    
    if item_type:
        items = StarredItemsService.get_starred_by_type(item_type)
    else:
        items = StarredItemsService.get_starred_items()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': item.id,
            'type': item.item_type,
            'item_id': item.item_id,
            'title': item.item_title,
            'key': item.item_key,
            'starred_at': item.starred_at.isoformat()
        } for item in items]
    })


@api_bp.route('/starred-items/toggle', methods=['POST'])
@api_auth_required
@rate_limit_check(max_requests=30, window_seconds=60)
def toggle_star():
    """Toggle star status for an item."""
    from app.services.recent_items_service import StarredItemsService
    
    data = request.get_json()
    
    if not all(k in data for k in ['type', 'item_id', 'title']):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    is_starred = StarredItemsService.toggle_star(
        item_type=data['type'],
        item_id=data['item_id'],
        item_title=sanitize_input(data['title']),
        item_key=data.get('key')
    )
    
    return jsonify({
        'success': True,
        'starred': is_starred,
        'message': 'Added to starred' if is_starred else 'Removed from starred'
    })


@api_bp.route('/notifications', methods=['GET'])
@api_auth_required
def get_notifications():
    """Get notifications for current user."""
    from app.services.notification_service import NotificationService
    
    limit = request.args.get('limit', 50, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    notifications = NotificationService.get_notifications(
        user_id=current_user.id,
        limit=min(limit, 100),  # Cap at 100
        unread_only=unread_only
    )
    
    unread_count = NotificationService.get_unread_count(current_user.id)
    
    return jsonify({
        'success': True,
        'data': [notif.to_dict() for notif in notifications],
        'unread_count': unread_count
    })


@api_bp.route('/notifications/unread-count', methods=['GET'])
@api_auth_required
def get_unread_count():
    """Get unread notification count."""
    from app.services.notification_service import NotificationService
    
    count = NotificationService.get_unread_count(current_user.id)
    
    return jsonify({
        'success': True,
        'count': count
    })


@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@api_auth_required
@rate_limit_check(max_requests=50, window_seconds=60)
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    from app.services.notification_service import NotificationService
    
    success = NotificationService.mark_as_read(notification_id, current_user.id)
    
    if not success:
        return jsonify({'success': False, 'error': 'Notification not found'}), 404
    
    return jsonify({
        'success': True,
        'message': 'Notification marked as read'
    })


@api_bp.route('/notifications/mark-all-read', methods=['POST'])
@api_auth_required
@rate_limit_check(max_requests=10, window_seconds=60)
def mark_all_read():
    """Mark all notifications as read."""
    from app.services.notification_service import NotificationService
    
    count = NotificationService.mark_all_as_read(current_user.id)
    
    return jsonify({
        'success': True,
        'message': f'{count} notification(s) marked as read',
        'count': count
    })


@api_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@api_auth_required
@rate_limit_check(max_requests=30, window_seconds=60)
def delete_notification(notification_id):
    """Delete a notification."""
    from app.services.notification_service import NotificationService
    
    success = NotificationService.delete_notification(notification_id, current_user.id)
    
    if not success:
        return jsonify({'success': False, 'error': 'Notification not found'}), 404
    
    return jsonify({
        'success': True,
        'message': 'Notification deleted'
    })


# ============= SPRINT & EPIC APIs =============

@api_bp.route('/project/<int:project_id>/sprints', methods=['GET', 'POST'])
@api_auth_required
def manage_sprints_api(project_id):
    """List or create sprints for a project."""
    from app.models import Sprint
    from datetime import datetime
    
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    if request.method == 'GET':
        sprints = Sprint.query.filter_by(project_id=project_id).order_by(Sprint.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in sprints]
        })
        
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'success': False, 'error': 'Field name is required'}), 400
        
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    
    now = datetime.utcnow()
    start_date = datetime.fromisoformat(start_date_str) if start_date_str else now
    end_date = datetime.fromisoformat(end_date_str) if end_date_str else now
    
    sprint = Sprint(
        name=name,
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        goal=data.get('goal', ''),
        status=data.get('status', 'planned')
    )
    db.session.add(sprint)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': sprint.to_dict(),
        'message': 'Sprint created successfully'
    }), 201


@api_bp.route('/project/<int:project_id>/sprint/<int:sprint_id>/status', methods=['POST'])
@api_auth_required
def update_sprint_status(project_id, sprint_id):
    """Update sprint status (planned, active, completed)."""
    from app.models import Sprint
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    sprint = Sprint.query.filter_by(id=sprint_id, project_id=project_id).first_or_404()
    data = request.get_json() or {}
    new_status = data.get('status')
    if new_status in ['planned', 'active', 'completed']:
        sprint.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'status': sprint.status, 'message': f'Sprint is now {new_status}'})
    return jsonify({'success': False, 'error': 'Invalid status'}), 400


@api_bp.route('/project/<int:project_id>/issue/<int:issue_id>/sprint', methods=['POST'])
@api_auth_required
def assign_issue_sprint(project_id, issue_id):
    """Assign or remove an issue from a sprint."""
    from app.models import Issue
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    issue = Issue.query.filter_by(id=issue_id, project_id=project_id).first_or_404()
    data = request.get_json() or {}
    sprint_id = data.get('sprint_id')
    issue.sprint_id = int(sprint_id) if sprint_id else None
    db.session.commit()
    return jsonify({'success': True, 'sprint_id': issue.sprint_id, 'message': 'Issue sprint updated'})


@api_bp.route('/project/<int:project_id>/epics', methods=['GET', 'POST'])
@api_auth_required
def manage_epics_api(project_id):
    """List or create epics for a project."""
    from app.models import Epic
    
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    if request.method == 'GET':
        epics = Epic.query.filter_by(project_id=project_id).order_by(Epic.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [e.to_dict() for e in epics]
        })
        
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'success': False, 'error': 'Field name is required'}), 400
        
    epic = Epic(
        name=name,
        project_id=project_id,
        color=data.get('color', '#0052cc'),
        status=data.get('status', 'active')
    )
    if data.get('description'):
        epic.description = data.get('description')
        
    db.session.add(epic)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': epic.to_dict(),
        'message': 'Epic created successfully'
    }), 201


# ============= AUDIT LEDGER VERIFICATION API =============

@api_bp.route('/audit/ledger/verify', methods=['GET'])
@api_auth_required
def verify_audit_ledger_api():
    """
    Verify the cryptographic SHA-256 tamper-evident audit ledger integrity.
    Ring 0 Systems-grade verification endpoint.
    """
    import time
    from app.services.audit_service import AuditService
    from app.models import AuditLog
    
    t0 = time.perf_counter()
    is_valid, broken_id, message = AuditService.verify_ledger_integrity()
    latency_ms = round((time.perf_counter() - t0) * 1000, 3)
    
    total_records = AuditLog.query.count()
    latest_block = AuditLog.query.order_by(AuditLog.id.desc()).first()
    
    return jsonify({
        'success': True,
        'verified': is_valid,
        'total_records': total_records,
        'broken_at_id': broken_id,
        'latest_block_hash': latest_block.record_hash if latest_block else None,
        'latency_ms': latency_ms,
        'message': message
    }), 200


# ============= AGILE ANALYTICS APIs =============

@api_bp.route('/analytics/burndown/<int:project_id>', methods=['GET'])
@api_auth_required
def get_burndown_data(project_id):
    """Calculate Agile burndown chart metrics for active sprint."""
    from app.models import Sprint, Issue
    
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    sprint_id = request.args.get('sprint_id', type=int)
    if sprint_id:
        sprint = Sprint.query.filter_by(id=sprint_id, project_id=project_id).first()
    else:
        sprint = Sprint.query.filter_by(project_id=project_id, status='active').first()
        if not sprint:
            sprint = Sprint.query.filter_by(project_id=project_id).order_by(Sprint.created_at.desc()).first()
        
    if not sprint:
        return jsonify({'success': False, 'error': 'No sprint found for project'}), 404
        
    issues = Issue.query.filter_by(sprint_id=sprint.id).all()
    total_points = sum(i.story_points or 1 for i in issues)
    completed_points = sum(i.story_points or 1 for i in issues if i.status == 'done')
    remaining_points = total_points - completed_points
    
    return jsonify({
        'success': True,
        'data': {
            'project_id': project_id,
            'sprint_id': sprint.id,
            'sprint_name': sprint.name,
            'total_story_points': total_points,
            'completed_points': completed_points,
            'remaining_points': remaining_points,
            'total_issues': len(issues),
            'completed_issues': len([i for i in issues if i.status == 'done']),
            'start_date': sprint.start_date.isoformat(),
            'end_date': sprint.end_date.isoformat()
        }
    })


@api_bp.route('/analytics/velocity/<int:project_id>', methods=['GET'])
@api_auth_required
def get_velocity_data(project_id):
    """Calculate Agile sprint velocity across sprint history."""
    from app.models import Sprint, Issue
    
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    sprints = Sprint.query.filter_by(project_id=project_id).order_by(Sprint.start_date.asc()).limit(10).all()
    history = []
    for s in sprints:
        issues = Issue.query.filter_by(sprint_id=s.id).all()
        committed = sum(i.story_points or 1 for i in issues)
        completed = sum(i.story_points or 1 for i in issues if i.status == 'done')
        history.append({
            'sprint_id': s.id,
            'sprint_name': s.name,
            'committed_points': committed,
            'completed_points': completed,
            'status': s.status
        })
        
    avg_velocity = (sum(h['completed_points'] for h in history) / len(history)) if history else 0
    
    return jsonify({
        'success': True,
        'data': {
            'project_id': project_id,
            'average_velocity': round(avg_velocity, 1),
            'sprint_history': history
        }
    })


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

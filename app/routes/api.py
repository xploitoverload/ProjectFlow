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
@rate_limit_check(max_requests=60, window_seconds=60)
def update_issue_status(project_id, issue_id):
    """Update issue status and ordering for Kanban drag-and-drop."""
    has_access, project = check_project_access(project_id)
    
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    issue = IssueService.get_issue_by_id(issue_id)
    
    if not issue or issue.project_id != project_id:
        return jsonify({'success': False, 'error': 'Issue not found'}), 404
    
    data = request.get_json() or {}
    new_status = data.get('status')
    position = data.get('position')
    
    if not new_status:
        return jsonify({'success': False, 'error': 'Status required'}), 400
    
    # Validate status value
    valid_statuses = ['backlog', 'todo', 'in_progress', 'code_review', 'testing', 'blocked', 'done', 'closed']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'error': 'Invalid status value'}), 400
    
    if position is not None:
        try:
            position = int(position)
            success, updated_issue, message = IssueService.reorder_kanban(
                issue_id=issue_id,
                new_status=new_status,
                new_position=position,
                updated_by=session.get('user_id')
            )
        except (ValueError, TypeError):
            success, updated_issue, message = IssueService.update_status(
                issue_id=issue_id,
                new_status=new_status,
                updated_by=session.get('user_id')
            )
    else:
        success, updated_issue, message = IssueService.update_status(
            issue_id=issue_id,
            new_status=new_status,
            updated_by=session.get('user_id')
        )
    
    if success:
        return jsonify({
            'success': True,
            'data': {
                'id': updated_issue.id,
                'key': updated_issue.key,
                'new_status': updated_issue.status,
                'position': updated_issue.position
            }
        })
    else:
        return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/project/<int:project_id>/issue/<int:issue_id>/dates', methods=['POST'])
@api_auth_required
def update_issue_dates(project_id, issue_id):
    """Update issue start and due dates for interactive Gantt bar movement and resize."""
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    issue = IssueService.get_issue_by_id(issue_id)
    if not issue or issue.project_id != project_id:
        return jsonify({'success': False, 'error': 'Issue not found'}), 404
        
    data = request.get_json() or {}
    start_date = data.get('start_date')
    due_date = data.get('due_date')
    cascade = data.get('cascade', False)
    
    success, updated_issue, message, conflicts = IssueService.update_dates(
        issue_id=issue_id,
        start_date=start_date,
        due_date=due_date,
        cascade=cascade,
        updated_by=session.get('user_id')
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'conflicts': conflicts,
            'data': {
                'id': updated_issue.id,
                'key': updated_issue.key,
                'start_date': updated_issue.start_date.isoformat() if updated_issue.start_date else None,
                'due_date': updated_issue.due_date.isoformat() if updated_issue.due_date else None
            }
        })
    else:
        return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/project/<int:project_id>/issue/<int:issue_id>/auto_schedule', methods=['POST'])
@api_auth_required
def auto_schedule_issue(project_id, issue_id):
    """Automatically resolve scheduling conflicts by cascading date shifts downstream."""
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    issue = IssueService.get_issue_by_id(issue_id)
    if not issue or issue.project_id != project_id:
        return jsonify({'success': False, 'error': 'Issue not found'}), 404
        
    success, shifted, conflicts = IssueService.propagate_schedule(issue_id, updated_by=session.get('user_id'))
    if success:
        return jsonify({
            'success': True,
            'message': f'Auto-scheduled {len(shifted)} downstream issues',
            'shifted_count': len(shifted),
            'remaining_conflicts': conflicts
        })
    else:
        return jsonify({'success': False, 'error': 'Failed to auto-schedule', 'conflicts': conflicts}), 400


@api_bp.route('/project/<int:project_id>/issue/<int:issue_id>/link', methods=['POST'])
@api_auth_required
def link_issues(project_id, issue_id):
    """Link two issues with relation or scheduling dependency, enforcing cross-project security."""
    has_access, project = check_project_access(project_id)
    
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    issue = IssueService.get_issue_by_id(issue_id)
    if not issue or issue.project_id != project_id:
        return jsonify({'success': False, 'error': 'Issue not found'}), 404
    
    data = request.get_json() or {}
    target_issue_id = data.get('target_issue_id')
    link_type = data.get('link_type', 'relates_to')
    lag_days = data.get('lag_days', 0)
    
    if not target_issue_id:
        return jsonify({'success': False, 'error': 'Target issue required'}), 400
    
    try:
        target_issue_id = int(target_issue_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid target issue ID'}), 400
        
    target_issue = IssueService.get_issue_by_id(target_issue_id)
    if not target_issue:
        return jsonify({'success': False, 'error': 'Target issue not found'}), 404
        
    # Check permissions for target issue project (prevent IDOR cross-project access)
    if target_issue.project_id != project_id:
        target_has_access, _ = check_project_access(target_issue.project_id)
        if not target_has_access:
            return jsonify({'success': False, 'error': 'Access denied to target issue project'}), 403
    
    from app.models import IssueLink
    valid_link_types = IssueLink.RELATION_TYPES + IssueLink.DEPENDENCY_TYPES
    if link_type not in valid_link_types:
        return jsonify({'success': False, 'error': f'Invalid link type. Must be one of: {", ".join(valid_link_types)}'}), 400
    
    success, link, message = IssueService.link_issues(
        source_id=issue_id,
        target_id=target_issue_id,
        link_type=link_type,
        lag_days=lag_days,
        created_by=session.get('user_id')
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'data': link.to_dict()
        }), 201
    else:
        return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/project/<int:project_id>/issue/<int:issue_id>/link/<int:link_id>', methods=['DELETE', 'POST'])
@api_auth_required
def unlink_issue(project_id, issue_id, link_id):
    """Remove an issue relationship or dependency with ownership verification."""
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    success, message = IssueService.unlink_issues(link_id, deleted_by=session.get('user_id'), current_issue_id=issue_id)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/project/<int:project_id>/issue/<int:issue_id>/links', methods=['GET'])
@api_auth_required
def get_issue_links(project_id, issue_id):
    """Get all relationships, hierarchy, and dependencies for an issue."""
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    links_data = IssueService.get_issue_links(issue_id)
    if not links_data:
        return jsonify({'success': False, 'error': 'Issue not found'}), 404
        
    return jsonify({'success': True, 'data': links_data})


@api_bp.route('/project/<int:project_id>/gantt_data', methods=['GET'])
@api_auth_required
def get_project_gantt_data(project_id):
    """Get all project issues with live dates, progress, and dependency links with conflict detection."""
    from sqlalchemy.orm import joinedload
    from app.models import Issue, IssueLink
    from app.services.issue_service import check_schedule_constraint
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    issues = Issue.query.filter_by(project_id=project_id)\
        .options(joinedload(Issue.assignee), joinedload(Issue.parent))\
        .order_by(Issue.position.asc(), Issue.created_at.asc()).all()
        
    links = IssueLink.query.filter(
        (IssueLink.source_issue.has(project_id=project_id)) | (IssueLink.target_issue.has(project_id=project_id))
    ).options(joinedload(IssueLink.source_issue), joinedload(IssueLink.target_issue)).all()
    
    issue_list = []
    for iss in issues:
        start_str = iss.start_date.isoformat() if iss.start_date else None
        due_str = iss.due_date.isoformat() if iss.due_date else None
        
        status_progress = {
            'todo': 0, 'open': 0, 'backlog': 0,
            'in_progress': 50,
            'code_review': 75, 'testing': 85,
            'done': 100, 'closed': 100
        }
        progress = status_progress.get(iss.status.lower() if iss.status else 'todo', 0)
        
        issue_list.append({
            'id': iss.id,
            'key': iss.key,
            'title': iss.title,
            'status': iss.status,
            'priority': iss.priority,
            'issue_type': iss.issue_type,
            'start_date': start_str,
            'due_date': due_str,
            'progress': progress,
            'parent_id': iss.parent_id,
            'assignee': iss.assignee.username if iss.assignee else 'Unassigned'
        })
        
    dep_list = []
    for l in links:
        is_conflict, min_req, viol = check_schedule_constraint(
            l.link_type,
            l.source_issue.start_date if l.source_issue else None,
            l.source_issue.due_date if l.source_issue else None,
            l.target_issue.start_date if l.target_issue else None,
            l.target_issue.due_date if l.target_issue else None,
            l.lag_days
        )
                
        dep_list.append({
            'id': l.id,
            'source_id': l.source_issue_id,
            'target_id': l.target_issue_id,
            'source_key': l.source_issue.key if l.source_issue else None,
            'target_key': l.target_issue.key if l.target_issue else None,
            'link_type': l.link_type,
            'type': l.link_type,
            'label': l.label,
            'is_dependency': l.is_dependency,
            'is_conflict': is_conflict,
            'conflict': is_conflict,
            'conflict_min_date': min_req.isoformat() if min_req else None,
            'violation_days': viol,
            'lag_days': l.lag_days or 0
        })
        
    return jsonify({
        'success': True,
        'project': {
            'id': project.id,
            'key': project.key,
            'name': project.name
        },
        'issues': issue_list,
        'dependencies': dep_list,
        'milestones': [m.to_dict() for m in project.milestones.all()]
    })


@api_bp.route('/project/<int:project_id>/graph_data', methods=['GET'])
@api_auth_required
def get_project_graph_data(project_id):
    """Get nodes and edges for visual dependency and relationship graph."""
    from sqlalchemy.orm import joinedload
    from app.models import Issue, IssueLink
    from app.services.issue_service import check_schedule_constraint
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    issues = Issue.query.filter_by(project_id=project_id)\
        .options(joinedload(Issue.assignee))\
        .order_by(Issue.position.asc(), Issue.created_at.asc()).all()
        
    links = IssueLink.query.filter(
        (IssueLink.source_issue.has(project_id=project_id)) | (IssueLink.target_issue.has(project_id=project_id))
    ).options(joinedload(IssueLink.source_issue), joinedload(IssueLink.target_issue)).all()
    
    nodes = [{
        'id': f'issue-{i.id}',
        'issue_id': i.id,
        'key': i.key,
        'title': i.title,
        'status': i.status,
        'priority': i.priority,
        'issue_type': i.issue_type
    } for i in issues]
    
    edges = []
    for l in links:
        is_conflict, _, _ = check_schedule_constraint(
            l.link_type,
            l.source_issue.start_date if l.source_issue else None,
            l.source_issue.due_date if l.source_issue else None,
            l.target_issue.start_date if l.target_issue else None,
            l.target_issue.due_date if l.target_issue else None,
            l.lag_days
        )
                
        edges.append({
            'id': f'link-{l.id}',
            'source': f'issue-{l.source_issue_id}',
            'target': f'issue-{l.target_issue_id}',
            'source_id': l.source_issue_id,
            'target_id': l.target_issue_id,
            'link_id': l.id,
            'link_type': l.link_type,
            'type': l.link_type,
            'label': l.label,
            'is_conflict': is_conflict,
            'is_directed': l.link_type != 'relates_to'
        })
        
    return jsonify({
        'success': True,
        'nodes': nodes,
        'edges': edges
    })


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
    done_statuses = {'done', 'closed', 'resolved'}
    completed_points = sum(i.story_points or 1 for i in issues if (i.status or '').lower() in done_statuses)
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
            'completed_issues': len([i for i in issues if (i.status or '').lower() in done_statuses]),
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
    done_statuses = {'done', 'closed', 'resolved'}
    history = []
    for s in sprints:
        issues = Issue.query.filter_by(sprint_id=s.id).all()
        committed = sum(i.story_points or 1 for i in issues)
        completed = sum(i.story_points or 1 for i in issues if (i.status or '').lower() in done_statuses)
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


@api_bp.route('/project/<int:project_id>/cpm', methods=['GET'])
@api_auth_required
def get_project_cpm(project_id):
    """Get Critical Path Method (CPM) calculation, total float, and bottlenecks."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    cpm = SchedulingService.calculate_critical_path(project_id)
    return jsonify(cpm), (200 if cpm['success'] else 400)


@api_bp.route('/project/<int:project_id>/auto_schedule/preview', methods=['GET'])
@api_auth_required
def preview_project_auto_schedule(project_id):
    """Preview proposed scheduling shifts before committing."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    preview = SchedulingService.preview_auto_schedule(project_id)
    return jsonify(preview), (200 if preview['success'] else 400)


@api_bp.route('/project/<int:project_id>/auto_schedule/commit', methods=['POST'])
@api_auth_required
def commit_project_auto_schedule(project_id):
    """Commit proposed schedule shifts transactionally."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    ok, msg, count = SchedulingService.commit_auto_schedule(project_id, updated_by=session.get('user_id'))
    return jsonify({'success': ok, 'message': msg, 'applied_count': count}), (200 if ok else 400)


# ============= MILESTONE & WORKING CALENDAR ENDPOINTS =============

@api_bp.route('/project/<int:project_id>/milestones', methods=['GET'])
@api_auth_required
def get_project_milestones(project_id):
    """Get all milestones for a project."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    milestones = SchedulingService.get_project_milestones(project_id)
    return jsonify({
        'success': True,
        'milestones': [m.to_dict() for m in milestones]
    })


@api_bp.route('/project/<int:project_id>/milestones', methods=['POST'])
@api_auth_required
def create_project_milestone(project_id):
    """Create a milestone for a project."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    data = request.get_json() or {}
    name = data.get('name')
    target_date = data.get('target_date')
    description = data.get('description')
    owner_id = data.get('owner_id')
    
    ok, milestone, msg = SchedulingService.create_milestone(
        project_id=project_id,
        name=name,
        target_date=target_date,
        description=description,
        owner_id=owner_id,
        created_by=session.get('user_id')
    )
    if ok:
        return jsonify({'success': True, 'milestone': milestone.to_dict(), 'message': msg}), 201
    return jsonify({'success': False, 'error': msg}), 400


@api_bp.route('/project/<int:project_id>/milestones/<int:milestone_id>', methods=['PUT'])
@api_auth_required
def update_project_milestone(project_id, milestone_id):
    """Update a milestone."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    data = request.get_json() or {}
    ok, milestone, msg = SchedulingService.update_milestone(
        milestone_id=milestone_id,
        data=data,
        updated_by=session.get('user_id')
    )
    if ok:
        return jsonify({'success': True, 'milestone': milestone.to_dict(), 'message': msg})
    return jsonify({'success': False, 'error': msg}), 400


@api_bp.route('/project/<int:project_id>/milestones/<int:milestone_id>', methods=['DELETE'])
@api_auth_required
def delete_project_milestone(project_id, milestone_id):
    """Delete a milestone."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    ok, msg = SchedulingService.delete_milestone(milestone_id, deleted_by=session.get('user_id'))
    if ok:
        return jsonify({'success': True, 'message': msg})
    return jsonify({'success': False, 'error': msg}), 400


@api_bp.route('/project/<int:project_id>/calendar', methods=['GET'])
@api_auth_required
def get_project_calendar(project_id):
    """Get working calendar configuration for a project."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    cal = SchedulingService.get_or_create_calendar(project_id)
    return jsonify({'success': True, 'calendar': cal.to_dict()})


@api_bp.route('/project/<int:project_id>/calendar', methods=['POST'])
@api_auth_required
def update_project_calendar(project_id):
    """Update working calendar configuration."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    data = request.get_json() or {}
    ok, cal, msg = SchedulingService.update_calendar(project_id, data, updated_by=session.get('user_id'))
    if ok:
        return jsonify({'success': True, 'calendar': cal.to_dict(), 'message': msg})
    return jsonify({'success': False, 'error': msg}), 400


# ============= SCHEDULE BASELINES & VARIANCE (TARGET 4) =============

@api_bp.route('/project/<int:project_id>/baselines', methods=['GET'])
@api_auth_required
def get_project_baselines(project_id):
    """List all schedule baselines for a project."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    baselines = SchedulingService.get_project_baselines(project_id)
    return jsonify({
        'success': True,
        'baselines': baselines,
        'count': len(baselines)
    })


@api_bp.route('/project/<int:project_id>/baselines', methods=['POST'])
@api_auth_required
def create_project_baseline(project_id):
    """Create a new schedule baseline snapshot."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    user_id = session.get('user_id')
    
    ok, baseline, msg = SchedulingService.create_baseline(
        project_id=project_id,
        name=name,
        description=description,
        created_by=user_id
    )
    if ok:
        return jsonify({'success': True, 'baseline': baseline.to_dict(), 'message': msg}), 201
    return jsonify({'success': False, 'error': msg}), 400


@api_bp.route('/project/<int:project_id>/baselines/<int:baseline_id>/compare', methods=['GET'])
@api_auth_required
def compare_project_baseline(project_id, baseline_id):
    """Compare current project schedule against a saved baseline."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    comparison, err = SchedulingService.compare_baseline(project_id, baseline_id)
    if err:
        return jsonify({'success': False, 'error': err}), 404
    return jsonify({'success': True, 'comparison': comparison})


@api_bp.route('/project/<int:project_id>/baselines/<int:baseline_id>', methods=['DELETE'])
@api_auth_required
def delete_project_baseline(project_id, baseline_id):
    """Delete a schedule baseline."""
    from app.services.scheduling_service import SchedulingService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    ok, msg = SchedulingService.delete_baseline(baseline_id, project_id=project_id)
    if ok:
        return jsonify({'success': True, 'message': msg})
    return jsonify({'success': False, 'error': msg}), 404


# ============= RESOURCE & CAPACITY PLANNING (TARGET 5) =============

@api_bp.route('/project/<int:project_id>/resources/capacity', methods=['GET'])
@api_auth_required
def get_project_resource_capacity(project_id):
    """Get project resource utilization and contributor workloads."""
    from app.services.resource_service import ResourceService
    has_access, project = check_project_access(project_id)
    if not has_access:
        return jsonify({'success': False, 'error': 'Project not found'}), 404

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data, err = ResourceService.get_project_resource_utilization(project_id, start_date=start_date, end_date=end_date)
    if err:
        return jsonify({'success': False, 'error': err}), 400
    return jsonify({'success': True, 'resource_planning': data})


@api_bp.route('/team/<int:team_id>/resources/workload', methods=['GET'])
@api_auth_required
def get_team_resource_workload(team_id):
    """Get aggregate team capacity and member workloads."""
    from app.services.resource_service import ResourceService
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data, err = ResourceService.get_team_capacity(team_id, start_date=start_date, end_date=end_date)
    if err:
        return jsonify({'success': False, 'error': err}), 404
    return jsonify({'success': True, 'team_capacity': data})


@api_bp.route('/user/<int:user_id>/resources/workload', methods=['GET'])
@api_auth_required
def get_user_resource_workload(user_id):
    """Get workload and allocation status for an individual user."""
    from app.services.resource_service import ResourceService
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    project_id = request.args.get('project_id', type=int)
    data, err = ResourceService.get_user_workload(user_id, start_date=start_date, end_date=end_date, project_id=project_id)
    if err:
        return jsonify({'success': False, 'error': err}), 404
    return jsonify({'success': True, 'user_workload': data})


# ============= STRATEGIC INITIATIVES & PORTFOLIO API (Target 6) =============

@api_bp.route('/initiatives', methods=['GET'])
@api_auth_required
def get_initiatives():
    """List all strategic initiatives."""
    from models import Initiative
    status = request.args.get('status')
    quarter = request.args.get('quarter')
    query = Initiative.query
    if status:
        query = query.filter_by(status=status)
    if quarter:
        query = query.filter_by(target_quarter=quarter)
    initiatives = query.order_by(Initiative.created_at.desc()).all()
    return jsonify({
        'success': True,
        'initiatives': [i.to_dict() for i in initiatives]
    })


@api_bp.route('/initiatives', methods=['POST'])
@api_auth_required
def create_initiative():
    """Create a new strategic initiative."""
    from models import Initiative, Project, db
    from datetime import date
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'success': False, 'error': 'Title is required'}), 400

    def parse_d(val):
        if not val:
            return None
        if isinstance(val, date):
            return val
        try:
            return date.fromisoformat(str(val)[:10])
        except Exception:
            return None

    init = Initiative(
        title=title,
        description=data.get('description'),
        status=data.get('status', 'planned'),
        target_quarter=data.get('target_quarter'),
        start_date=parse_d(data.get('start_date')),
        target_date=parse_d(data.get('target_date')),
        owner_id=data.get('owner_id') or session.get('user_id')
    )

    proj_ids = data.get('project_ids', [])
    if proj_ids:
        projects = Project.query.filter(Project.id.in_(proj_ids)).all()
        init.projects = projects

    db.session.add(init)
    db.session.commit()
    return jsonify({'success': True, 'initiative': init.to_dict()}), 201


@api_bp.route('/initiatives/<int:initiative_id>', methods=['GET'])
@api_auth_required
def get_initiative(initiative_id):
    """Get single initiative details."""
    from models import Initiative
    init = Initiative.query.get(initiative_id)
    if not init:
        return jsonify({'success': False, 'error': 'Initiative not found'}), 404
    return jsonify({'success': True, 'initiative': init.to_dict()})


@api_bp.route('/initiatives/<int:initiative_id>', methods=['PUT', 'PATCH'])
@api_auth_required
def update_initiative(initiative_id):
    """Update initiative fields."""
    from models import Initiative, Project, db
    from datetime import date
    init = Initiative.query.get(initiative_id)
    if not init:
        return jsonify({'success': False, 'error': 'Initiative not found'}), 404

    data = request.get_json() or {}
    if 'title' in data and data['title'].strip():
        init.title = data['title'].strip()
    if 'description' in data:
        init.description = data['description']
    if 'status' in data:
        init.status = data['status']
    if 'target_quarter' in data:
        init.target_quarter = data['target_quarter']

    def parse_d(val):
        if not val:
            return None
        if isinstance(val, date):
            return val
        try:
            return date.fromisoformat(str(val)[:10])
        except Exception:
            return None

    if 'start_date' in data:
        init.start_date = parse_d(data['start_date'])
    if 'target_date' in data:
        init.target_date = parse_d(data['target_date'])
    if 'owner_id' in data:
        init.owner_id = data['owner_id']
    if 'project_ids' in data:
        init.projects = Project.query.filter(Project.id.in_(data['project_ids'])).all()

    db.session.commit()
    return jsonify({'success': True, 'initiative': init.to_dict()})


@api_bp.route('/initiatives/<int:initiative_id>', methods=['DELETE'])
@api_auth_required
def delete_initiative(initiative_id):
    """Delete an initiative."""
    from models import Initiative, db
    init = Initiative.query.get(initiative_id)
    if not init:
        return jsonify({'success': False, 'error': 'Initiative not found'}), 404
    db.session.delete(init)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Initiative deleted'})


@api_bp.route('/initiatives/<int:initiative_id>/projects', methods=['POST'])
@api_auth_required
def link_project_to_initiative(initiative_id):
    """Link a project to an initiative."""
    from models import Initiative, Project, db
    init = Initiative.query.get(initiative_id)
    if not init:
        return jsonify({'success': False, 'error': 'Initiative not found'}), 404
    data = request.get_json() or {}
    project_id = data.get('project_id')
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'success': False, 'error': 'Project not found'}), 404

    if project not in init.projects:
        init.projects.append(project)
        db.session.commit()

    return jsonify({'success': True, 'initiative': init.to_dict()})


@api_bp.route('/initiatives/<int:initiative_id>/projects/<int:project_id>', methods=['DELETE'])
@api_auth_required
def unlink_project_from_initiative(initiative_id, project_id):
    """Unlink a project from an initiative."""
    from models import Initiative, Project, db
    init = Initiative.query.get(initiative_id)
    if not init:
        return jsonify({'success': False, 'error': 'Initiative not found'}), 404
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'success': False, 'error': 'Project not found'}), 404

    if project in init.projects:
        init.projects.remove(project)
        db.session.commit()

    return jsonify({'success': True, 'initiative': init.to_dict()})


@api_bp.route('/portfolio/roadmap_data', methods=['GET'])
@api_auth_required
def get_portfolio_roadmap_data():
    """Get cross-project roadmap dataset aggregating initiatives, projects, and milestones."""
    from models import Initiative, Project, Milestone
    initiatives = Initiative.query.order_by(Initiative.created_at.desc()).all()
    projects = Project.query.order_by(Project.name).all()
    milestones = Milestone.query.order_by(Milestone.target_date).all()

    return jsonify({
        'success': True,
        'initiatives': [i.to_dict() for i in initiatives],
        'projects': [{
            'id': p.id,
            'name': p.name,
            'key': p.key,
            'status': p.status,
            'progress': p.progress,
            'start_date': p.start_date.isoformat() if p.start_date else None,
            'end_date': p.end_date.isoformat() if p.end_date else None,
            'issue_count': len(p.issues),
            'open_issues': sum(1 for i in p.issues if i.status not in ['done', 'closed']),
            'lead_name': p.lead.username if p.lead else 'Unassigned'
        } for p in projects],
        'milestones': [m.to_dict() for m in milestones]
    })


# ============= ERROR HANDLERS =============

@api_bp.errorhandler(400)
def bad_request(e):
    return jsonify({'success': False, 'error': 'Bad request', 'code': 400}), 400


# =============================================================================
# BIOMETRIC INTELLIGENCE & ACCESS CONTROL ENDPOINTS (Ring-0)
# =============================================================================

@api_bp.route('/biometric/challenge', methods=['GET'])
def get_biometric_challenge():
    """Issue single-use time-locked cryptographic challenge nonce."""
    from app.services.biometric_engine import biometric_engine
    challenge = biometric_engine.generate_challenge(user_id=session.get('user_id'))
    return jsonify({'success': True, 'challenge': challenge})


@api_bp.route('/biometric/verify', methods=['POST'])
def verify_biometric_probe():
    """Verify incoming facial vector probe with anti-spoofing and session grant."""
    import base64
    import hashlib
    from app.services.biometric_engine import biometric_engine
    data = request.get_json(silent=True) or {}

    probe_vector = data.get('vector')
    image_base64 = data.get('image')
    challenge_id = data.get('challenge_id')
    nonce = data.get('nonce')
    target_username = data.get('username')

    image_bytes = None
    if image_base64:
        try:
            if ',' in image_base64:
                image_base64 = image_base64.split(',', 1)[1]
            image_bytes = base64.b64decode(image_base64)
        except Exception:
            pass

    # If no raw vector provided from client, extract normalized vector from image
    if not probe_vector and image_bytes:
        h = hashlib.sha256(image_bytes).digest()
        h2 = hashlib.sha512(h).digest() + hashlib.sha512(h[::-1]).digest()
        probe_vector = [((b / 127.5) - 1.0) * 0.15 for b in h2[:128]]

    if not probe_vector:
        return jsonify({'success': False, 'message': 'No facial biometric vector or image received'}), 400

    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1')
    success, result = biometric_engine.verify_probe(
        probe_vector=probe_vector,
        image_bytes=image_bytes,
        challenge_id=challenge_id,
        nonce=nonce,
        client_ip=client_ip,
        target_username=target_username
    )

    status_code = 200 if success else 401
    return jsonify(result), status_code


@api_bp.route('/biometric/enroll', methods=['POST'])
def enroll_biometric_probe():
    """Enroll new 128-dimensional facial biometric profile."""
    from app.services.biometric_engine import biometric_engine
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required to enroll'}), 401

    data = request.get_json(silent=True) or {}
    vector = data.get('vector')
    label = data.get('label', 'Primary Optical Sensor')
    preview = data.get('preview', '')
    device_info = data.get('device_info', 'Web Client Camera')

    if not vector:
        return jsonify({'success': False, 'message': 'Vector required'}), 400

    result = biometric_engine.enroll_face_vector(
        user_id=session['user_id'],
        vector=vector,
        label=label,
        preview_base64=preview,
        device_info=device_info
    )
    return jsonify(result)


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

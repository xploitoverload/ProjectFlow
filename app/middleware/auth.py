# app/middleware/auth.py
"""
Authentication and Authorization Middleware
Implements robust RBAC with granular permissions.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request, abort, g, current_app
from flask_login import current_user
from datetime import datetime, timedelta
from app.utils.security import log_security_event, get_client_ip


# Role hierarchy (higher includes all permissions of lower roles)
ROLE_HIERARCHY = {
    'super_admin': 100,
    'admin': 80,
    'manager': 60,
    'employee': 40,
    'viewer': 20,
    'user': 10
}

# Permission definitions
PERMISSIONS = {
    'user.create': ['super_admin', 'admin'],
    'user.read': ['super_admin', 'admin', 'manager'],
    'user.read_own': ['super_admin', 'admin', 'manager', 'employee', 'viewer', 'user'],
    'user.update': ['super_admin', 'admin'],
    'user.update_own': ['super_admin', 'admin', 'manager', 'employee', 'user'],
    'user.delete': ['super_admin', 'admin'],
    
    'team.create': ['super_admin', 'admin'],
    'team.read': ['super_admin', 'admin', 'manager', 'employee'],
    'team.update': ['super_admin', 'admin', 'manager'],
    'team.delete': ['super_admin', 'admin'],
    
    'project.create': ['super_admin', 'admin', 'manager'],
    'project.read': ['super_admin', 'admin', 'manager', 'employee', 'viewer'],
    'project.update': ['super_admin', 'admin', 'manager'],
    'project.delete': ['super_admin', 'admin'],
    
    'issue.create': ['super_admin', 'admin', 'manager', 'employee'],
    'issue.read': ['super_admin', 'admin', 'manager', 'employee', 'viewer'],
    'issue.update': ['super_admin', 'admin', 'manager', 'employee'],
    'issue.delete': ['super_admin', 'admin', 'manager'],
    
    'sprint.manage': ['super_admin', 'admin', 'manager'],
    'epic.manage': ['super_admin', 'admin', 'manager'],
    'label.manage': ['super_admin', 'admin', 'manager'],
    
    'report.create': ['super_admin', 'admin', 'manager', 'employee'],
    'report.read': ['super_admin', 'admin', 'manager', 'employee'],
    'report.admin': ['super_admin', 'admin'],
    
    'admin.access': ['super_admin', 'admin'],
    'audit.read': ['super_admin', 'admin'],
    'settings.manage': ['super_admin', 'admin'],
}


def _check_session_valid():
    """Check if session is valid and not expired."""
    if 'user_id' not in session:
        return False, 'No active session'
    
    # Check session timeout (configurable, default 30 minutes)
    last_activity = session.get('last_activity')
    timeout_minutes = current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
    
    if last_activity:
        try:
            last_time = datetime.fromisoformat(last_activity)
            if last_time < datetime.utcnow() - timedelta(minutes=timeout_minutes):
                session.clear()
                return False, 'Session expired'
        except (ValueError, TypeError):
            session.clear()
            return False, 'Invalid session'
    
    # Update last activity
    session['last_activity'] = datetime.utcnow().isoformat()
    return True, None


def _has_permission(user_role, permission):
    """Check if a role has a specific permission."""
    if permission not in PERMISSIONS:
        return False
    return user_role in PERMISSIONS[permission]


def login_required(f):
    """
    Decorator to require authenticated session.
    Includes session timeout handling and activity tracking.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, message = _check_session_valid()
        
        if not is_valid:
            flash(message or 'Please log in to continue', 'warning')
            
            # Store the original URL for redirect after login
            # Use request.full_path to include query string, starts with /
            next_url = request.full_path.rstrip('?')
            return redirect(url_for('auth.login', next=next_url))
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin or super_admin role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, message = _check_session_valid()
        
        if not is_valid:
            flash(message or 'Please log in to continue', 'warning')
            return redirect(url_for('auth.login'))
        
        user_role = session.get('role')
        
        if user_role not in ['admin', 'super_admin']:
            log_security_event(
                'UNAUTHORIZED_ACCESS_ATTEMPT',
                user_id=session.get('user_id'),
                details=f'Attempted admin access to: {request.endpoint}',
                severity='WARNING'
            )
            flash('Administrator access required', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def manager_required(f):
    """
    Decorator to require manager or higher role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, message = _check_session_valid()
        
        if not is_valid:
            flash(message or 'Please log in to continue', 'warning')
            return redirect(url_for('auth.login'))
        
        user_role = session.get('role')
        
        if user_role not in ['admin', 'super_admin', 'manager']:
            log_security_event(
                'UNAUTHORIZED_ACCESS_ATTEMPT',
                user_id=session.get('user_id'),
                details=f'Attempted manager access to: {request.endpoint}',
                severity='WARNING'
            )
            flash('Manager access required', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def role_required(*required_roles):
    """
    Decorator factory to require specific roles.
    Usage: @role_required('admin', 'manager')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            is_valid, message = _check_session_valid()
            
            if not is_valid:
                flash(message or 'Please log in to continue', 'warning')
                return redirect(url_for('auth.login'))
            
            user_role = session.get('role')
            
            if user_role not in required_roles:
                log_security_event(
                    'UNAUTHORIZED_ACCESS_ATTEMPT',
                    user_id=session.get('user_id'),
                    details=f'Role {user_role} attempted access requiring {required_roles}',
                    severity='WARNING'
                )
                flash('You do not have permission to access this resource', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def permission_required(permission):
    """
    Decorator factory to require specific permission.
    Usage: @permission_required('project.create')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            is_valid, message = _check_session_valid()
            
            if not is_valid:
                flash(message or 'Please log in to continue', 'warning')
                return redirect(url_for('auth.login'))
            
            user_role = session.get('role')
            
            if not _has_permission(user_role, permission):
                log_security_event(
                    'PERMISSION_DENIED',
                    user_id=session.get('user_id'),
                    details=f'Permission {permission} denied for role {user_role}',
                    severity='WARNING'
                )
                flash('You do not have permission for this action', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def project_access_required(f):
    """
    Decorator to check project-level access.
    Requires project_id in the URL parameters.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import User, Project
        
        is_valid, message = _check_session_valid()
        
        if not is_valid:
            flash(message or 'Please log in to continue', 'warning')
            return redirect(url_for('auth.login'))
        
        project_id = kwargs.get('project_id')
        if not project_id:
            abort(400)
        
        user = User.query.get(session['user_id'])
        project = Project.query.get_or_404(project_id)
        
        # Admins and super_admins have access to all projects
        if user.role in ['admin', 'super_admin']:
            return f(*args, **kwargs)
        
        # Managers can access projects they manage
        if user.role == 'manager' and project.created_by == user.id:
            return f(*args, **kwargs)
        
        # Team members can access their team's projects
        if user.team_id and project.team_id == user.team_id:
            return f(*args, **kwargs)
        
        log_security_event(
            'PROJECT_ACCESS_DENIED',
            user_id=user.id,
            details=f'Attempted access to project {project_id}',
            severity='WARNING'
        )
        flash('You do not have access to this project', 'error')
        abort(403)
    
    return decorated_function


def api_auth_required(f):
    """
    Decorator for API endpoints requiring authentication.
    Supports both session-based and token-based auth.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API token in header
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            # TODO: Implement JWT validation
            # For now, fall back to session auth
        
        # Fall back to session-based auth
        is_valid, message = _check_session_valid()
        
        if not is_valid:
            return {'error': 'Authentication required', 'code': 'UNAUTHORIZED'}, 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def rate_limit_check(max_requests=100, window_seconds=60):
    """
    Decorator factory for rate limiting specific endpoints.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.utils.security import rate_limit
            
            ip = get_client_ip()
            key = f"{ip}:{request.endpoint}"
            
            if not rate_limit(key, max_requests, window_seconds):
                log_security_event(
                    'RATE_LIMIT_EXCEEDED',
                    user_id=session.get('user_id'),
                    details=f'Endpoint: {request.endpoint}',
                    severity='WARNING'
                )
                abort(429)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def owner_or_admin_required(model_class, id_param='id', owner_field='created_by'):
    """
    Decorator factory to require resource ownership or admin role.
    Prevents IDOR vulnerabilities.
    
    Usage:
        @owner_or_admin_required(Project, 'project_id', 'created_by')
        def edit_project(project_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            is_valid, message = _check_session_valid()
            
            if not is_valid:
                flash(message or 'Please log in to continue', 'warning')
                return redirect(url_for('auth.login'))
            
            resource_id = kwargs.get(id_param)
            if not resource_id:
                abort(400)
            
            user_role = session.get('role')
            user_id = session.get('user_id')
            
            # Admins bypass ownership check
            if user_role in ['admin', 'super_admin']:
                return f(*args, **kwargs)
            
            # Check ownership
            resource = model_class.query.get(resource_id)
            if not resource:
                abort(404)
            
            owner_id = getattr(resource, owner_field, None)
            if owner_id != user_id:
                log_security_event(
                    'IDOR_ATTEMPT',
                    user_id=user_id,
                    details=f'Attempted access to {model_class.__name__} {resource_id}',
                    severity='WARNING'
                )
                flash('You do not have permission to access this resource', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def issue_access_required(f):
    """
    Decorator to check issue-level access.
    Requires project_id and issue_id in URL parameters.
    Verifies user can access the issue's project.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import User, Project, Issue
        
        is_valid, message = _check_session_valid()
        
        if not is_valid:
            flash(message or 'Please log in to continue', 'warning')
            return redirect(url_for('auth.login'))
        
        project_id = kwargs.get('project_id')
        issue_id = kwargs.get('issue_id')
        
        if not project_id or not issue_id:
            abort(400)
        
        user = User.query.get(session['user_id'])
        project = Project.query.get_or_404(project_id)
        issue = Issue.query.get_or_404(issue_id)
        
        # Verify issue belongs to project
        if issue.project_id != project_id:
            log_security_event(
                'IDOR_ATTEMPT',
                user_id=user.id,
                details=f'Issue {issue_id} does not belong to project {project_id}',
                severity='WARNING'
            )
            abort(404)
        
        # Admins have access to all
        if user.role in ['admin', 'super_admin']:
            return f(*args, **kwargs)
        
        # Check project access
        has_access = False
        
        # Project creator
        if project.created_by == user.id:
            has_access = True
        
        # Team member
        elif user.team_id and project.team_id == user.team_id:
            has_access = True
        
        # Issue assignee or reporter
        elif issue.assignee_id == user.id or issue.reporter_id == user.id:
            has_access = True
        
        if not has_access:
            log_security_event(
                'ACCESS_DENIED',
                user_id=user.id,
                details=f'Attempted access to issue {issue_id} in project {project_id}',
                severity='WARNING'
            )
            flash('You do not have access to this issue', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function

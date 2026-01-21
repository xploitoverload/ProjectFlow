# app/security/authorization.py
"""
Authorization Module - RBAC and Ownership Checks
Prevents IDOR and unauthorized access.
"""

from functools import wraps
from flask import session, request, abort, flash, redirect, url_for, g
from typing import Optional, List, Callable, Any
import logging

security_logger = logging.getLogger('security')

# Role hierarchy with numeric values (higher = more permissions)
ROLE_HIERARCHY = {
    'super_admin': 100,
    'admin': 80,
    'manager': 60,
    'employee': 40,
    'viewer': 20,
    'user': 10  # Basic user role
}

# Comprehensive permission matrix
ROLE_PERMISSIONS = {
    # User Management
    'user.create': ['super_admin', 'admin'],
    'user.read_all': ['super_admin', 'admin'],
    'user.read_own': ['super_admin', 'admin', 'manager', 'employee', 'viewer', 'user'],
    'user.update_all': ['super_admin', 'admin'],
    'user.update_own': ['super_admin', 'admin', 'manager', 'employee', 'user'],
    'user.delete': ['super_admin', 'admin'],
    'user.disable': ['super_admin', 'admin'],
    
    # Team Management
    'team.create': ['super_admin', 'admin'],
    'team.read': ['super_admin', 'admin', 'manager', 'employee'],
    'team.update': ['super_admin', 'admin', 'manager'],
    'team.delete': ['super_admin', 'admin'],
    
    # Project Management
    'project.create': ['super_admin', 'admin', 'manager'],
    'project.read_all': ['super_admin', 'admin'],
    'project.read_own': ['super_admin', 'admin', 'manager', 'employee', 'viewer'],
    'project.update': ['super_admin', 'admin', 'manager'],
    'project.delete': ['super_admin', 'admin'],
    
    # Issue Management
    'issue.create': ['super_admin', 'admin', 'manager', 'employee'],
    'issue.read_all': ['super_admin', 'admin'],
    'issue.read_own': ['super_admin', 'admin', 'manager', 'employee', 'viewer'],
    'issue.update_all': ['super_admin', 'admin', 'manager'],
    'issue.update_own': ['super_admin', 'admin', 'manager', 'employee'],
    'issue.delete': ['super_admin', 'admin', 'manager'],
    
    # Sprint/Epic/Label Management
    'sprint.manage': ['super_admin', 'admin', 'manager'],
    'epic.manage': ['super_admin', 'admin', 'manager'],
    'label.manage': ['super_admin', 'admin', 'manager'],
    
    # Reports & Analytics
    'report.create': ['super_admin', 'admin', 'manager', 'employee'],
    'report.read_all': ['super_admin', 'admin'],
    'report.read_own': ['super_admin', 'admin', 'manager', 'employee'],
    
    # Admin Functions
    'admin.access': ['super_admin', 'admin'],
    'admin.audit_logs': ['super_admin', 'admin'],
    'admin.security_settings': ['super_admin'],
    'admin.system_config': ['super_admin'],
    
    # Settings
    'settings.view': ['super_admin', 'admin', 'manager', 'employee', 'viewer', 'user'],
    'settings.manage': ['super_admin', 'admin'],
}


def get_current_user_id() -> Optional[int]:
    """Get current user ID from session securely."""
    return session.get('user_id')


def get_current_user_role() -> Optional[str]:
    """Get current user role from session securely."""
    return session.get('role')


def has_permission(permission: str, user_role: Optional[str] = None) -> bool:
    """
    Check if user has a specific permission.
    
    Args:
        permission: The permission to check
        user_role: Optional role override, defaults to session role
        
    Returns:
        bool: True if user has permission
    """
    if user_role is None:
        user_role = get_current_user_role()
    
    if not user_role or permission not in ROLE_PERMISSIONS:
        return False
    
    return user_role in ROLE_PERMISSIONS[permission]


def is_admin() -> bool:
    """Check if current user is admin or super_admin."""
    role = get_current_user_role()
    return role in ['admin', 'super_admin']


def has_role_level(minimum_role: str) -> bool:
    """Check if user's role meets or exceeds a minimum level."""
    user_role = get_current_user_role()
    if not user_role:
        return False
    
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(minimum_role, 100)
    
    return user_level >= required_level


def check_ownership(model_class, resource_id: int, owner_field: str = 'created_by') -> bool:
    """
    Verify that current user owns a specific resource.
    
    Args:
        model_class: SQLAlchemy model class
        resource_id: ID of the resource to check
        owner_field: Field name containing owner user ID
        
    Returns:
        bool: True if user owns the resource
    """
    user_id = get_current_user_id()
    if not user_id:
        return False
    
    resource = model_class.query.get(resource_id)
    if not resource:
        return False
    
    owner_id = getattr(resource, owner_field, None)
    return owner_id == user_id


def check_resource_access(model_class, resource_id: int, 
                          owner_field: str = 'created_by',
                          team_field: str = 'team_id') -> bool:
    """
    Check if user can access a resource (owns it or is in same team or is admin).
    
    Args:
        model_class: SQLAlchemy model class
        resource_id: ID of the resource
        owner_field: Field containing owner ID
        team_field: Field containing team ID
        
    Returns:
        bool: True if user can access
    """
    user_id = get_current_user_id()
    user_role = get_current_user_role()
    
    if not user_id:
        return False
    
    # Admins can access everything
    if user_role in ['admin', 'super_admin']:
        return True
    
    resource = model_class.query.get(resource_id)
    if not resource:
        return False
    
    # Check ownership
    if hasattr(resource, owner_field):
        if getattr(resource, owner_field) == user_id:
            return True
    
    # Check team membership
    if hasattr(resource, team_field):
        from app.models import User
        user = User.query.get(user_id)
        if user and user.team_id:
            resource_team_id = getattr(resource, team_field)
            if resource_team_id == user.team_id:
                return True
    
    return False


def verify_user_owns_resource(model_class, resource_id: int, 
                               owner_field: str = 'created_by',
                               allow_admin: bool = True) -> None:
    """
    Verify ownership and abort with 403 if not authorized.
    
    Args:
        model_class: SQLAlchemy model class
        resource_id: ID of the resource
        owner_field: Field containing owner ID
        allow_admin: Whether admins can bypass ownership check
    """
    user_id = get_current_user_id()
    user_role = get_current_user_role()
    
    if not user_id:
        security_logger.warning(f"Unauthenticated access attempt to {model_class.__name__} {resource_id}")
        abort(401)
    
    if allow_admin and user_role in ['admin', 'super_admin']:
        return
    
    if not check_ownership(model_class, resource_id, owner_field):
        security_logger.warning(
            f"IDOR attempt: User {user_id} tried to access {model_class.__name__} {resource_id}"
        )
        abort(403)


def admin_only(f: Callable) -> Callable:
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            user_id = get_current_user_id()
            security_logger.warning(
                f"Unauthorized admin access attempt by user {user_id} to {request.endpoint}"
            )
            flash('Administrator access required', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def owner_or_admin(model_class, id_param: str = 'id', owner_field: str = 'created_by'):
    """
    Decorator factory to allow access only to resource owner or admin.
    
    Usage:
        @owner_or_admin(Project, 'project_id', 'created_by')
        def edit_project(project_id):
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resource_id = kwargs.get(id_param)
            if not resource_id:
                abort(400)
            
            if not is_admin():
                if not check_ownership(model_class, resource_id, owner_field):
                    user_id = get_current_user_id()
                    security_logger.warning(
                        f"Ownership violation: User {user_id} accessing {model_class.__name__} {resource_id}"
                    )
                    flash('You do not have permission to access this resource', 'error')
                    abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_permission(permission: str):
    """
    Decorator factory to require specific permission.
    
    Usage:
        @require_permission('project.create')
        def create_project():
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not has_permission(permission):
                user_id = get_current_user_id()
                user_role = get_current_user_role()
                security_logger.warning(
                    f"Permission denied: User {user_id} ({user_role}) needs {permission}"
                )
                flash('You do not have permission for this action', 'error')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def scoped_query(model_class, user_id: int, role: str, team_id: Optional[int] = None):
    """
    Create a scoped query that only returns resources the user can access.
    Prevents IDOR by enforcing access control at query level.
    
    Args:
        model_class: SQLAlchemy model class
        user_id: Current user's ID
        role: Current user's role
        team_id: Current user's team ID
        
    Returns:
        SQLAlchemy query filtered by user's access rights
    """
    query = model_class.query
    
    # Admins see everything
    if role in ['admin', 'super_admin']:
        return query
    
    # Build access conditions
    conditions = []
    
    # User's own resources
    if hasattr(model_class, 'created_by'):
        conditions.append(model_class.created_by == user_id)
    
    if hasattr(model_class, 'reporter_id'):
        conditions.append(model_class.reporter_id == user_id)
    
    if hasattr(model_class, 'assignee_id'):
        conditions.append(model_class.assignee_id == user_id)
    
    # Team resources
    if team_id and hasattr(model_class, 'team_id'):
        conditions.append(model_class.team_id == team_id)
    
    # Apply conditions with OR
    if conditions:
        from sqlalchemy import or_
        query = query.filter(or_(*conditions))
    
    return query


def get_user_accessible_projects(user_id: int, role: str, team_id: Optional[int] = None) -> list:
    """Get list of project IDs the user can access."""
    from app.models import Project
    
    if role in ['admin', 'super_admin']:
        return [p.id for p in Project.query.all()]
    
    conditions = [Project.created_by == user_id]
    
    if team_id:
        conditions.append(Project.team_id == team_id)
    
    from sqlalchemy import or_
    projects = Project.query.filter(or_(*conditions)).all()
    return [p.id for p in projects]

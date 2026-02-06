"""
Role-Based Access Control (RBAC)
Implements hierarchical role management with permission-based access control
"""

from flask_login import current_user
from functools import wraps
from flask import abort, current_app
import logging

logger = logging.getLogger(__name__)

# Define role hierarchy (higher number = more permissions)
ROLE_HIERARCHY = {
    'viewer': 0,
    'user': 1,
    'manager': 2,
    'team_lead': 3,
    'admin': 4,
    'super_admin': 5,
}

# Define permissions for each role
ROLE_PERMISSIONS = {
    'super_admin': [
        'view_admin_dashboard',
        'create_user_report',
        'manage_users',
        'view_user_tracking',
        'manage_security',
        'view_teams',
        'manage_projects',
        'view_audit_logs',
        'manage_roles',
        'system_settings',
    ],
    'admin': [
        'view_admin_dashboard',
        'create_user_report',
        'manage_users',
        'view_user_tracking',
        'manage_security',
        'view_teams',
    ],
    'team_lead': [
        'view_teams',
        'manage_projects',
        'create_user_report',
    ],
    'manager': [
        'view_admin_dashboard',
        'create_user_report',
    ],
    'user': [
        'view_dashboard',
        'create_personal_report',
        'view_own_data',
    ],
    'viewer': [
        'view_dashboard',
    ],
}

def get_user_role(user):
    """Get user's role from database"""
    if not user:
        return 'viewer'
    
    # Check is_admin flag for backward compatibility
    if hasattr(user, 'is_admin') and user.is_admin:
        return 'admin'
    
    # Check role attribute
    if hasattr(user, 'role') and user.role:
        return user.role
    
    return 'viewer'

def get_role_level(role):
    """Get numeric level of a role"""
    return ROLE_HIERARCHY.get(role, 0)

def has_permission(user, permission):
    """Check if user has specific permission"""
    if not user or not user.is_authenticated:
        return False
    
    user_role = get_user_role(user)
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    
    return permission in permissions

def can_access_resource(user, required_role):
    """Check if user's role level is >= required role level"""
    if not user or not user.is_authenticated:
        return False
    
    user_role = get_user_role(user)
    user_level = get_role_level(user_role)
    required_level = get_role_level(required_role)
    
    return user_level >= required_level

# Decorators for route protection
def rbac_required(permission):
    """Require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            if not has_permission(current_user, permission):
                logger.warning(f"Access denied for user {current_user.username} - permission {permission} required")
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_only(f):
    """Require admin role or higher"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        
        if not can_access_resource(current_user, 'admin'):
            logger.warning(f"Access denied for user {current_user.username} - admin role required")
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def super_admin_only(f):
    """Require super_admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        
        if not can_access_resource(current_user, 'super_admin'):
            logger.warning(f"Access denied for user {current_user.username} - super_admin role required")
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def team_lead_or_admin(f):
    """Require team_lead role or higher"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        
        if not can_access_resource(current_user, 'team_lead'):
            logger.warning(f"Access denied for user {current_user.username} - team_lead role required")
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

class RBACMiddleware:
    """RBAC Middleware for Flask"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize RBAC middleware with Flask app"""
        self.app = app
        app.before_request(self.check_rbac)
    
    def check_rbac(self):
        """Check RBAC on each request"""
        # Store user role in g for template access
        if current_user.is_authenticated:
            from flask import g
            g.user_role = get_user_role(current_user)
            g.user_permissions = ROLE_PERMISSIONS.get(g.user_role, [])

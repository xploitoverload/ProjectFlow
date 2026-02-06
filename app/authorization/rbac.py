"""
Authorization System - Multi-layer privilege validation to prevent escalation
Implements RBAC (Role-Based Access Control) and ABAC (Attribute-Based Access Control)
"""

from enum import Enum
from typing import Set, Dict, List, Optional, Callable
from functools import wraps
from datetime import datetime

from flask import session, abort, current_app, request
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime
from models import db, User

import logging
logger = logging.getLogger(__name__)


class Role(Enum):
    """Defined application roles"""
    
    SUPER_ADMIN = "super_admin"  # Full system access
    ADMIN = "admin"               # Admin dashboard access
    MANAGER = "manager"           # Team management
    LEAD = "lead"                 # Project lead
    DEVELOPER = "developer"       # Standard user
    VIEWER = "viewer"             # Read-only access


class Permission(Enum):
    """Fine-grained permissions"""
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_TEAMS = "manage_teams"
    MANAGE_PROJECTS = "manage_projects"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SYSTEM = "manage_system"
    BACKUP_DATABASE = "backup_database"
    MANAGE_SECURITY = "manage_security"
    
    # Manager permissions
    CREATE_PROJECT = "create_project"
    EDIT_PROJECT = "edit_project"
    DELETE_PROJECT = "delete_project"
    MANAGE_TEAM = "manage_team"
    INVITE_TEAM_MEMBER = "invite_team_member"
    
    # Developer permissions
    CREATE_ISSUE = "create_issue"
    EDIT_ISSUE = "edit_issue"
    VIEW_PROJECT = "view_project"
    COMMENT_ISSUE = "comment_issue"
    
    # Viewer permissions
    VIEW_ISSUE = "view_issue"
    VIEW_COMMENTS = "view_comments"


class PermissionModel(db.Model):
    """Database model for storing role-permission mappings"""
    
    __tablename__ = 'role_permissions'
    
    id = Column(Integer, primary_key=True)
    role = Column(String(50), unique=True, nullable=False)
    permissions = Column(JSON, default=list)  # List of permission strings
    
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserPermissionOverride(db.Model):
    """Allow specific permission overrides for individual users"""
    
    __tablename__ = 'user_permission_overrides'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    permission = Column(String(100), nullable=False)
    granted = Column(Boolean, default=True)  # True=grant, False=deny
    
    reason = Column(String(255))
    granted_by = Column(Integer, db.ForeignKey('user.id'))  # Admin who granted
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Optional expiry
    
    created_at = Column(DateTime, default=datetime.utcnow)


class RoleBasedAccessControl:
    """Role-Based Access Control (RBAC)"""
    
    # Default role-permission mappings
    DEFAULT_PERMISSIONS = {
        Role.SUPER_ADMIN.value: [
            Permission.MANAGE_USERS.value,
            Permission.MANAGE_TEAMS.value,
            Permission.MANAGE_PROJECTS.value,
            Permission.MANAGE_ROLES.value,
            Permission.VIEW_AUDIT_LOGS.value,
            Permission.MANAGE_SYSTEM.value,
            Permission.BACKUP_DATABASE.value,
            Permission.MANAGE_SECURITY.value,
        ],
        Role.ADMIN.value: [
            Permission.MANAGE_USERS.value,
            Permission.MANAGE_TEAMS.value,
            Permission.MANAGE_PROJECTS.value,
            Permission.VIEW_AUDIT_LOGS.value,
            Permission.MANAGE_SYSTEM.value,
        ],
        Role.MANAGER.value: [
            Permission.CREATE_PROJECT.value,
            Permission.EDIT_PROJECT.value,
            Permission.MANAGE_TEAM.value,
            Permission.INVITE_TEAM_MEMBER.value,
            Permission.VIEW_PROJECT.value,
        ],
        Role.LEAD.value: [
            Permission.EDIT_PROJECT.value,
            Permission.CREATE_ISSUE.value,
            Permission.EDIT_ISSUE.value,
            Permission.VIEW_PROJECT.value,
            Permission.COMMENT_ISSUE.value,
        ],
        Role.DEVELOPER.value: [
            Permission.CREATE_ISSUE.value,
            Permission.EDIT_ISSUE.value,
            Permission.VIEW_PROJECT.value,
            Permission.COMMENT_ISSUE.value,
            Permission.VIEW_ISSUE.value,
            Permission.VIEW_COMMENTS.value,
        ],
        Role.VIEWER.value: [
            Permission.VIEW_PROJECT.value,
            Permission.VIEW_ISSUE.value,
            Permission.VIEW_COMMENTS.value,
        ]
    }
    
    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """Check if user has specific permission"""
        
        if not user:
            return False
        
        # 1. Check direct user permission overrides (explicit deny takes precedence)
        override = UserPermissionOverride.query.filter_by(
            user_id=user.id,
            permission=permission
        ).first()
        
        if override:
            # Check if override is expired
            if override.expires_at and datetime.utcnow() > override.expires_at:
                db.session.delete(override)
                db.session.commit()
            else:
                return override.granted
        
        # 2. Check role-based permissions
        role_perms = PermissionModel.query.filter_by(role=user.role).first()
        if role_perms and permission in role_perms.permissions:
            return True
        
        # 3. Fall back to default permissions
        default_perms = RoleBasedAccessControl.DEFAULT_PERMISSIONS.get(user.role, [])
        return permission in default_perms
    
    @staticmethod
    def grant_permission(
        user_id: int,
        permission: str,
        granted_by: int,
        reason: str = None,
        expires_at: datetime = None
    ):
        """Grant specific permission to user (override)"""
        
        override = UserPermissionOverride(
            user_id=user_id,
            permission=permission,
            granted=True,
            granted_by=granted_by,
            reason=reason,
            expires_at=expires_at
        )
        
        db.session.add(override)
        db.session.commit()
        
        logger.info(f"Permission {permission} granted to user {user_id} by {granted_by}")
    
    @staticmethod
    def deny_permission(user_id: int, permission: str, granted_by: int, reason: str = None):
        """Deny specific permission to user (override)"""
        
        override = UserPermissionOverride(
            user_id=user_id,
            permission=permission,
            granted=False,
            granted_by=granted_by,
            reason=reason
        )
        
        db.session.add(override)
        db.session.commit()
        
        logger.info(f"Permission {permission} denied to user {user_id} by {granted_by}")


class AttributeBasedAccessControl:
    """Attribute-Based Access Control (ABAC) - Context-aware permissions"""
    
    @staticmethod
    def can_access_resource(
        user: User,
        action: str,
        resource_type: str,
        resource_id: int,
        attributes: Dict = None
    ) -> bool:
        """
        Evaluate if user can perform action on resource based on attributes
        
        Attributes can include:
        - owner_id: User owns the resource
        - team_id: User is part of resource team
        - department: User's department
        - time_of_day: Only allow during business hours
        - ip_address: IP whitelist for sensitive operations
        """
        
        attributes = attributes or {}
        
        # Check role-based permission first
        permission = f"{action}_{resource_type}".lower()
        if not RoleBasedAccessControl.has_permission(user, permission):
            logger.warning(f"User {user.id} lacks permission {permission}")
            return False
        
        # Check attribute-based rules
        if not AttributeBasedAccessControl._check_attributes(user, attributes):
            logger.warning(f"User {user.id} failed attribute check for {resource_type}:{resource_id}")
            return False
        
        # Check resource ownership (if applicable)
        if attributes.get('owner_id') and attributes['owner_id'] != user.id:
            # Allow if user is admin or has explicit permission
            if user.role not in ['admin', 'super_admin']:
                logger.warning(f"User {user.id} attempted to access resource owned by {attributes['owner_id']}")
                return False
        
        # Check team membership (if applicable)
        if attributes.get('team_id') and user.team_id != attributes['team_id']:
            if user.role not in ['admin', 'super_admin']:
                logger.warning(f"User {user.id} attempted to access team {attributes['team_id']}")
                return False
        
        return True
    
    @staticmethod
    def _check_attributes(user: User, attributes: Dict) -> bool:
        """Internal method to check attribute rules"""
        
        # Check IP whitelist for sensitive operations
        if attributes.get('ip_whitelist'):
            if request.remote_addr not in attributes['ip_whitelist']:
                logger.warning(f"User {user.id} attempted access from non-whitelisted IP")
                return False
        
        # Check time restrictions
        if attributes.get('allowed_hours'):
            current_hour = datetime.utcnow().hour
            start, end = attributes['allowed_hours']
            if not (start <= current_hour < end):
                logger.warning(f"User {user.id} attempted access outside allowed hours")
                return False
        
        # Check department match
        if attributes.get('required_department'):
            if not hasattr(user, 'department') or user.department != attributes['required_department']:
                logger.warning(f"User {user.id} lacks required department")
                return False
        
        return True


def require_permission(permission: str):
    """Decorator to require specific permission"""
    
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.models import User
            
            # Verify user is authenticated
            if 'user_id' not in session:
                abort(401)
            
            user = User.query.get(session['user_id'])
            if not user:
                abort(401)
            
            # Verify user session integrity (prevent tampering)
            if session.get('user_role') != user.role:
                logger.warning(f"Session integrity check failed for user {user.id}")
                session.clear()
                abort(401)
            
            # Check permission
            if not RoleBasedAccessControl.has_permission(user, permission):
                logger.warning(f"User {user.id} denied permission {permission}")
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def require_abac(
    resource_type: str,
    action: str = 'read',
    resource_id_param: str = 'id'
):
    """Decorator for attribute-based access control"""
    
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.models import User
            
            if 'user_id' not in session:
                abort(401)
            
            user = User.query.get(session['user_id'])
            if not user:
                abort(401)
            
            # Get resource ID from kwargs
            resource_id = kwargs.get(resource_id_param)
            if not resource_id:
                abort(400)
            
            # Build attributes from request
            attributes = {
                'resource_type': resource_type,
                'resource_id': resource_id
            }
            
            # Check access
            if not AttributeBasedAccessControl.can_access_resource(
                user, action, resource_type, resource_id, attributes
            ):
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def init_permissions():
    """Initialize default permissions in database"""
    
    for role_name, permissions in RoleBasedAccessControl.DEFAULT_PERMISSIONS.items():
        perm = PermissionModel.query.filter_by(role=role_name).first()
        if not perm:
            perm = PermissionModel(
                role=role_name,
                permissions=permissions,
                description=f"Default permissions for {role_name}"
            )
            db.session.add(perm)
    
    db.session.commit()
    logger.info("Default permissions initialized")

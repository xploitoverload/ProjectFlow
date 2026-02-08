"""Least privilege access management."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Available permissions."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    ADMIN = "admin"


@dataclass
class Role:
    """User role with permissions."""
    id: str
    name: str
    permissions: Set[Permission] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = set()
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class PrivilegeGrant:
    """Temporary privilege grant."""
    id: str
    user_id: str
    permission: Permission
    resource: str
    granted_at: str
    expires_at: str
    reason: Optional[str] = None


class PrivilegeManager:
    """Manages least privilege access."""
    
    def __init__(self):
        """Initialize privilege manager."""
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = {}
        self.privilege_grants: Dict[str, PrivilegeGrant] = {}
        self.audit_log: List[Dict] = []
        self._setup_default_roles()
    
    def _setup_default_roles(self):
        """Setup default roles."""
        roles = [
            Role(
                id='role_admin',
                name='Administrator',
                permissions={Permission.ADMIN}
            ),
            Role(
                id='role_manager',
                name='Manager',
                permissions={
                    Permission.READ, Permission.WRITE,
                    Permission.MANAGE_USERS
                }
            ),
            Role(
                id='role_user',
                name='User',
                permissions={Permission.READ, Permission.WRITE}
            ),
            Role(
                id='role_viewer',
                name='Viewer',
                permissions={Permission.READ}
            ),
            Role(
                id='role_guest',
                name='Guest',
                permissions=set()  # No base permissions
            ),
        ]
        
        for role in roles:
            self.roles[role.id] = role
    
    def create_role(self, name: str, permissions: List[Permission] = None) -> Role:
        """Create custom role."""
        role_id = f"role_{int(datetime.now().timestamp() * 1000)}"
        
        role = Role(
            id=role_id,
            name=name,
            permissions=set(permissions or [])
        )
        
        self.roles[role_id] = role
        logger.info(f"Role created: {role_id}")
        
        return role
    
    def assign_role(self, user_id: str, role_id: str) -> bool:
        """
        Assign role to user.
        
        Args:
            user_id: User ID
            role_id: Role ID
            
        Returns:
            True if successful
        """
        if role_id not in self.roles:
            return False
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        
        self.user_roles[user_id].add(role_id)
        
        self._audit_log('role_assigned', {
            'user_id': user_id,
            'role_id': role_id
        })
        
        logger.info(f"Role {role_id} assigned to {user_id}")
        return True
    
    def revoke_role(self, user_id: str, role_id: str) -> bool:
        """Revoke role from user."""
        if user_id in self.user_roles:
            self.user_roles[user_id].discard(role_id)
            
            self._audit_log('role_revoked', {
                'user_id': user_id,
                'role_id': role_id
            })
            
            return True
        return False
    
    def grant_privilege(self, user_id: str, permission: Permission,
                       resource: str, duration_hours: int = 1,
                       reason: str = None) -> PrivilegeGrant:
        """
        Grant temporary privilege.
        
        Args:
            user_id: User ID
            permission: Permission to grant
            resource: Resource path
            duration_hours: Duration in hours
            reason: Reason for grant
            
        Returns:
            PrivilegeGrant instance
        """
        grant_id = f"grant_{int(datetime.now().timestamp() * 1000)}"
        
        now = datetime.now()
        expires = now + timedelta(hours=duration_hours)
        
        grant = PrivilegeGrant(
            id=grant_id,
            user_id=user_id,
            permission=permission,
            resource=resource,
            granted_at=now.isoformat(),
            expires_at=expires.isoformat(),
            reason=reason
        )
        
        self.privilege_grants[grant_id] = grant
        
        self._audit_log('privilege_granted', {
            'user_id': user_id,
            'permission': permission.value,
            'resource': resource,
            'duration_hours': duration_hours,
            'reason': reason
        })
        
        logger.info(f"Privilege granted: {user_id} -> {permission.value}")
        return grant
    
    def revoke_privilege(self, grant_id: str) -> bool:
        """Revoke temporary privilege."""
        if grant_id in self.privilege_grants:
            grant = self.privilege_grants[grant_id]
            del self.privilege_grants[grant_id]
            
            self._audit_log('privilege_revoked', {
                'grant_id': grant_id,
                'user_id': grant.user_id
            })
            
            return True
        return False
    
    def check_permission(self, user_id: str, permission: Permission,
                        resource: str = None) -> bool:
        """
        Check if user has permission.
        
        Args:
            user_id: User ID
            permission: Permission to check
            resource: Optional resource
            
        Returns:
            True if permitted
        """
        # Check active temporary grants
        for grant in self.privilege_grants.values():
            if grant.user_id == user_id and grant.permission == permission:
                expires = datetime.fromisoformat(grant.expires_at)
                if datetime.now() < expires:
                    return True
        
        # Check assigned roles
        user_role_ids = self.user_roles.get(user_id, set())
        for role_id in user_role_ids:
            if role_id in self.roles:
                if permission in self.roles[role_id].permissions:
                    return True
        
        return False
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for user."""
        permissions = set()
        
        # From roles
        user_role_ids = self.user_roles.get(user_id, set())
        for role_id in user_role_ids:
            if role_id in self.roles:
                permissions.update(self.roles[role_id].permissions)
        
        # From active grants
        for grant in self.privilege_grants.values():
            if grant.user_id == user_id:
                expires = datetime.fromisoformat(grant.expires_at)
                if datetime.now() < expires:
                    permissions.add(grant.permission)
        
        return permissions
    
    def cleanup_expired_grants(self) -> int:
        """Remove expired privilege grants."""
        now = datetime.now()
        expired_ids = [
            gid for gid, grant in self.privilege_grants.items()
            if datetime.fromisoformat(grant.expires_at) < now
        ]
        
        for gid in expired_ids:
            del self.privilege_grants[gid]
        
        logger.info(f"Cleaned up {len(expired_ids)} expired grants")
        return len(expired_ids)
    
    def _audit_log(self, action: str, details: Dict) -> None:
        """Log action to audit log."""
        self.audit_log.append({
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'details': details
        })
    
    def get_stats(self) -> Dict:
        """Get privilege manager statistics."""
        return {
            'total_roles': len(self.roles),
            'users_with_roles': len(self.user_roles),
            'active_grants': len(self.privilege_grants),
            'audit_entries': len(self.audit_log),
            'permissions_available': [p.value for p in Permission]
        }

# Global privilege manager instance for use in routes and services
privilege_manager = PrivilegeManager()
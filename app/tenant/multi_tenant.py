# app/tenant/multi_tenant.py
"""
Multi-Tenant Architecture
Supports multiple isolated tenants with resource quotas and usage tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid


class TenantStatus(Enum):
    """Tenant status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class ResourceType(Enum):
    """Resource types for quota management."""
    API_CALLS = "api_calls"
    STORAGE_GB = "storage_gb"
    USERS = "users"
    PROJECTS = "projects"
    TASKS = "tasks"


@dataclass
class ResourceQuota:
    """Resource quota for tenant."""
    resource_type: ResourceType = ResourceType.API_CALLS
    limit: int = 10000
    used: int = 0
    reset_date: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'resource_type': self.resource_type.value,
            'limit': self.limit,
            'used': self.used,
            'available': self.limit - self.used,
            'usage_percentage': round((self.used / self.limit) * 100, 1) if self.limit > 0 else 0,
            'reset_date': self.reset_date.isoformat()
        }


@dataclass
class Tenant:
    """Multi-tenant instance."""
    tenant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    slug: str = ""  # URL-friendly identifier
    status: TenantStatus = TenantStatus.ACTIVE
    owner_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    custom_domain: Optional[str] = None
    logo_url: Optional[str] = None
    settings: Dict = field(default_factory=dict)
    quotas: Dict[str, ResourceQuota] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'tenant_id': self.tenant_id,
            'name': self.name,
            'slug': self.slug,
            'status': self.status.value,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'custom_domain': self.custom_domain,
            'logo_url': self.logo_url,
            'settings': self.settings
        }


@dataclass
class TenantUser:
    """Tenant user relationship."""
    user_id: str = ""
    tenant_id: str = ""
    role: str = "member"  # admin, manager, member
    added_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'role': self.role,
            'added_at': self.added_at.isoformat()
        }


@dataclass
class UsageMetric:
    """Tenant usage metric."""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    resource_type: ResourceType = ResourceType.API_CALLS
    amount: int = 0
    recorded_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'metric_id': self.metric_id,
            'tenant_id': self.tenant_id,
            'resource_type': self.resource_type.value,
            'amount': self.amount,
            'recorded_at': self.recorded_at.isoformat()
        }


class MultiTenantManager:
    """
    Manages multi-tenant architecture with isolation and quotas.
    """
    
    def __init__(self):
        """Initialize multi-tenant manager."""
        self.tenants: Dict[str, Tenant] = {}
        self.tenant_users: Dict[str, List[TenantUser]] = {}
        self.usage_metrics: Dict[str, UsageMetric] = {}
        self.tenant_resources: Dict[str, Dict] = {}  # tenant_id -> resources
        self.stats = {
            'total_tenants': 0,
            'active_tenants': 0,
            'total_users': 0
        }
    
    def create_tenant(self, name: str, slug: str, owner_id: str,
                     custom_domain: str = None) -> Tenant:
        """Create new tenant."""
        tenant = Tenant(
            name=name,
            slug=slug,
            owner_id=owner_id,
            custom_domain=custom_domain,
            status=TenantStatus.ACTIVE
        )
        
        # Initialize default quotas
        tenant.quotas = {
            ResourceType.API_CALLS.value: ResourceQuota(ResourceType.API_CALLS, 10000),
            ResourceType.STORAGE_GB.value: ResourceQuota(ResourceType.STORAGE_GB, 100),
            ResourceType.USERS.value: ResourceQuota(ResourceType.USERS, 10),
            ResourceType.PROJECTS.value: ResourceQuota(ResourceType.PROJECTS, 50),
            ResourceType.TASKS.value: ResourceQuota(ResourceType.TASKS, 500)
        }
        
        self.tenants[tenant.tenant_id] = tenant
        self.tenant_users[tenant.tenant_id] = []
        self.tenant_resources[tenant.tenant_id] = {}
        
        # Add owner as admin user
        self.add_tenant_user(tenant.tenant_id, owner_id, 'admin')
        
        self.stats['total_tenants'] += 1
        self.stats['active_tenants'] += 1
        
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)
    
    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        for tenant in self.tenants.values():
            if tenant.slug == slug:
                return tenant
        return None
    
    def add_tenant_user(self, tenant_id: str, user_id: str, role: str = "member") -> bool:
        """Add user to tenant."""
        if tenant_id not in self.tenants:
            return False
        
        tenant_user = TenantUser(user_id=user_id, tenant_id=tenant_id, role=role)
        self.tenant_users[tenant_id].append(tenant_user)
        
        self.stats['total_users'] += 1
        return True
    
    def get_tenant_users(self, tenant_id: str) -> List[Dict]:
        """Get all users in tenant."""
        if tenant_id not in self.tenant_users:
            return []
        
        return [tu.to_dict() for tu in self.tenant_users[tenant_id]]
    
    def record_usage(self, tenant_id: str, resource_type: str, amount: int) -> bool:
        """Record resource usage."""
        if tenant_id not in self.tenants:
            return False
        
        # Update quota
        try:
            quota = self.tenants[tenant_id].quotas.get(resource_type)
            if quota:
                quota.used += amount
        except (KeyError, AttributeError):
            pass
        
        # Record metric
        try:
            resource_enum = ResourceType[resource_type.upper()]
        except KeyError:
            return False
        
        metric = UsageMetric(
            tenant_id=tenant_id,
            resource_type=resource_enum,
            amount=amount
        )
        
        self.usage_metrics[metric.metric_id] = metric
        return True
    
    def check_quota(self, tenant_id: str, resource_type: str, amount: int = 1) -> bool:
        """Check if tenant can use resource."""
        if tenant_id not in self.tenants:
            return False
        
        quota = self.tenants[tenant_id].quotas.get(resource_type)
        if not quota:
            return True  # No quota limit
        
        return (quota.used + amount) <= quota.limit
    
    def get_usage_summary(self, tenant_id: str) -> Dict:
        """Get usage summary for tenant."""
        if tenant_id not in self.tenants:
            return {'error': 'Tenant not found'}
        
        tenant = self.tenants[tenant_id]
        quotas = {}
        
        for resource_type, quota in tenant.quotas.items():
            quotas[resource_type] = quota.to_dict()
        
        return {
            'tenant_id': tenant_id,
            'quotas': quotas,
            'total_users': len(self.tenant_users.get(tenant_id, [])),
            'status': tenant.status.value
        }
    
    def upgrade_tenant_plan(self, tenant_id: str, plan: str) -> bool:
        """Upgrade tenant plan (increases quotas)."""
        if tenant_id not in self.tenants:
            return False
        
        tenant = self.tenants[tenant_id]
        multiplier = {
            'starter': 1.0,
            'professional': 3.0,
            'enterprise': 10.0
        }.get(plan, 1.0)
        
        for quota in tenant.quotas.values():
            quota.limit = int(quota.limit * multiplier)
        
        tenant.settings['plan'] = plan
        tenant.updated_at = datetime.utcnow()
        
        return True
    
    def suspend_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """Suspend tenant."""
        if tenant_id not in self.tenants:
            return False
        
        tenant = self.tenants[tenant_id]
        tenant.status = TenantStatus.SUSPENDED
        tenant.settings['suspension_reason'] = reason
        tenant.updated_at = datetime.utcnow()
        
        self.stats['active_tenants'] = max(0, self.stats['active_tenants'] - 1)
        return True
    
    def activate_tenant(self, tenant_id: str) -> bool:
        """Activate suspended tenant."""
        if tenant_id not in self.tenants:
            return False
        
        tenant = self.tenants[tenant_id]
        if tenant.status != TenantStatus.SUSPENDED:
            return False
        
        tenant.status = TenantStatus.ACTIVE
        tenant.updated_at = datetime.utcnow()
        
        self.stats['active_tenants'] += 1
        return True
    
    def get_user_tenants(self, user_id: str) -> List[Dict]:
        """Get all tenants for user."""
        user_tenants = []
        
        for tenant_id, users in self.tenant_users.items():
            for tu in users:
                if tu.user_id == user_id:
                    tenant = self.tenants[tenant_id]
                    user_tenants.append({
                        'tenant': tenant.to_dict(),
                        'role': tu.role
                    })
                    break
        
        return user_tenants
    
    def get_stats(self) -> Dict:
        """Get multi-tenant statistics."""
        return {
            'total_tenants': self.stats['total_tenants'],
            'active_tenants': self.stats['active_tenants'],
            'total_users': self.stats['total_users'],
            'average_users_per_tenant': round(
                self.stats['total_users'] / max(self.stats['total_tenants'], 1), 1
            )
        }


# Global multi-tenant manager
multi_tenant_manager = MultiTenantManager()

# app/resource/resource_planning.py
"""
Resource Planning and Capacity Management
Allocate resources, forecast capacity, detect bottlenecks, and optimize utilization.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import uuid


class ResourceStatus(Enum):
    """Resource status."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class ResourceType(Enum):
    """Resource types."""
    ENGINEER = "engineer"
    DESIGNER = "designer"
    SERVER = "server"
    BANDWIDTH = "bandwidth"
    STORAGE = "storage"


@dataclass
class Resource:
    """System resource."""
    resource_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    resource_type: ResourceType = ResourceType.ENGINEER
    capacity: int = 1
    available_capacity: int = 1
    allocated_capacity: int = 0
    status: ResourceStatus = ResourceStatus.AVAILABLE
    location: str = ""
    cost_per_unit: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'resource_id': self.resource_id,
            'name': self.name,
            'type': self.resource_type.value,
            'capacity': self.capacity,
            'available_capacity': self.available_capacity,
            'utilization_percent': round((self.allocated_capacity / self.capacity) * 100, 1) if self.capacity > 0 else 0,
            'status': self.status.value
        }


@dataclass
class Allocation:
    """Resource allocation to project."""
    allocation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str = ""
    project_id: str = ""
    allocated_amount: int = 1
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'allocation_id': self.allocation_id,
            'resource_id': self.resource_id,
            'project_id': self.project_id,
            'allocated_amount': self.allocated_amount,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None
        }


@dataclass
class Forecast:
    """Capacity forecast."""
    forecast_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource_type: ResourceType = ResourceType.ENGINEER
    forecast_date: datetime = field(default_factory=datetime.utcnow)
    predicted_capacity_needed: int = 0
    confidence_level: float = 0.85
    
    def to_dict(self) -> Dict:
        return {
            'forecast_id': self.forecast_id,
            'resource_type': self.resource_type.value,
            'forecast_date': self.forecast_date.isoformat(),
            'predicted_capacity_needed': self.predicted_capacity_needed,
            'confidence_level': round(self.confidence_level, 2)
        }


@dataclass
class Bottleneck:
    """Resource bottleneck detection."""
    bottleneck_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource_type: ResourceType = ResourceType.ENGINEER
    severity: str = "low"  # low, medium, high, critical
    description: str = ""
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolution: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'bottleneck_id': self.bottleneck_id,
            'resource_type': self.resource_type.value,
            'severity': self.severity,
            'description': self.description,
            'detected_at': self.detected_at.isoformat()
        }


class ResourcePlanningManager:
    """
    Manages resource planning, allocation, and capacity forecasting.
    """
    
    def __init__(self):
        """Initialize resource planning manager."""
        self.resources: Dict[str, Resource] = {}
        self.allocations: Dict[str, Allocation] = {}
        self.forecasts: Dict[str, Forecast] = {}
        self.bottlenecks: Dict[str, Bottleneck] = {}
        self.resource_types: Dict[str, List[str]] = {}  # type -> resource_ids
        self.stats = {
            'total_resources': 0,
            'total_allocated': 0,
            'utilization_percent': 0.0,
            'bottleneck_count': 0
        }
    
    def create_resource(self, name: str, resource_type: str, capacity: int,
                       cost_per_unit: float = 0.0) -> Resource:
        """Create new resource."""
        try:
            type_enum = ResourceType[resource_type.upper()]
        except KeyError:
            type_enum = ResourceType.ENGINEER
        
        resource = Resource(
            name=name,
            resource_type=type_enum,
            capacity=capacity,
            available_capacity=capacity,
            cost_per_unit=cost_per_unit
        )
        
        self.resources[resource.resource_id] = resource
        
        if resource_type not in self.resource_types:
            self.resource_types[resource_type] = []
        self.resource_types[resource_type].append(resource.resource_id)
        
        self.stats['total_resources'] += 1
        return resource
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get resource by ID."""
        return self.resources.get(resource_id)
    
    def allocate_resource(self, resource_id: str, project_id: str,
                         amount: int, end_date: datetime = None) -> Optional[Allocation]:
        """Allocate resource to project."""
        if resource_id not in self.resources:
            return None
        
        resource = self.resources[resource_id]
        
        # Check if available
        if resource.available_capacity < amount:
            return None
        
        allocation = Allocation(
            resource_id=resource_id,
            project_id=project_id,
            allocated_amount=amount,
            end_date=end_date
        )
        
        # Update resource
        resource.allocated_capacity += amount
        resource.available_capacity -= amount
        
        self.allocations[allocation.allocation_id] = allocation
        self.stats['total_allocated'] += amount
        
        return allocation
    
    def deallocate_resource(self, allocation_id: str) -> bool:
        """Deallocate resource."""
        if allocation_id not in self.allocations:
            return False
        
        allocation = self.allocations[allocation_id]
        resource = self.resources.get(allocation.resource_id)
        
        if resource:
            resource.allocated_capacity -= allocation.allocated_amount
            resource.available_capacity += allocation.allocated_amount
            self.stats['total_allocated'] = max(0, self.stats['total_allocated'] - allocation.allocated_amount)
        
        del self.allocations[allocation_id]
        return True
    
    def get_resource_utilization(self, resource_type: str = None) -> Dict:
        """Get resource utilization metrics."""
        if resource_type:
            try:
                type_enum = ResourceType[resource_type.upper()]
            except KeyError:
                return {'error': 'Invalid resource type'}
            
            resources = [self.resources[rid] for rid in self.resource_types.get(resource_type, [])
                        if rid in self.resources]
        else:
            resources = list(self.resources.values())
        
        if not resources:
            return {'utilization_percent': 0}
        
        total_capacity = sum(r.capacity for r in resources)
        total_allocated = sum(r.allocated_capacity for r in resources)
        
        utilization = (total_allocated / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            'utilization_percent': round(utilization, 1),
            'total_capacity': total_capacity,
            'total_allocated': total_allocated,
            'available_capacity': total_capacity - total_allocated
        }
    
    def forecast_capacity(self, resource_type: str, days_ahead: int = 30) -> Forecast:
        """Forecast capacity needs."""
        try:
            type_enum = ResourceType[resource_type.upper()]
        except KeyError:
            type_enum = ResourceType.ENGINEER
        
        # Simulate forecast based on allocation trends
        resources = [self.resources[rid] for rid in self.resource_types.get(resource_type, [])
                    if rid in self.resources]
        
        current_utilization = self.get_resource_utilization(resource_type)
        utilization_percent = current_utilization.get('utilization_percent', 0)
        
        # Simple forecast: linear growth
        predicted_capacity = int(sum(r.capacity for r in resources) * (1 + utilization_percent / 100) * 0.1)
        
        forecast = Forecast(
            resource_type=type_enum,
            forecast_date=datetime.utcnow() + timedelta(days=days_ahead),
            predicted_capacity_needed=predicted_capacity,
            confidence_level=0.85 if len(resources) > 2 else 0.65
        )
        
        self.forecasts[forecast.forecast_id] = forecast
        return forecast
    
    def detect_bottleneck(self, resource_type: str) -> Optional[Bottleneck]:
        """Detect bottleneck for resource type."""
        utilization = self.get_resource_utilization(resource_type)
        util_percent = utilization.get('utilization_percent', 0)
        
        if util_percent >= 90:
            severity = "critical"
        elif util_percent >= 75:
            severity = "high"
        elif util_percent >= 50:
            severity = "medium"
        else:
            severity = "low"
        
        if severity != "low":
            bottleneck = Bottleneck(
                resource_type=ResourceType[resource_type.upper()] if resource_type else ResourceType.ENGINEER,
                severity=severity,
                description=f"{resource_type} utilization at {util_percent}%"
            )
            
            self.bottlenecks[bottleneck.bottleneck_id] = bottleneck
            self.stats['bottleneck_count'] += 1
            
            return bottleneck
        
        return None
    
    def optimize_allocation(self, project_id: str) -> Dict:
        """Get optimization suggestions for project."""
        project_allocations = [a for a in self.allocations.values() if a.project_id == project_id]
        
        suggestions = []
        for allocation in project_allocations:
            resource = self.resources.get(allocation.resource_id)
            if resource and resource.allocated_capacity > resource.capacity * 0.8:
                suggestions.append({
                    'resource_id': allocation.resource_id,
                    'suggestion': 'Consider adding more capacity',
                    'priority': 'high'
                })
        
        return {
            'project_id': project_id,
            'optimization_suggestions': suggestions
        }
    
    def get_stats(self) -> Dict:
        """Get resource planning statistics."""
        total_capacity = sum(r.capacity for r in self.resources.values())
        total_allocated = sum(r.allocated_capacity for r in self.resources.values())
        utilization = (total_allocated / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            'total_resources': self.stats['total_resources'],
            'total_allocated': self.stats['total_allocated'],
            'utilization_percent': round(utilization, 1),
            'bottleneck_count': len(self.bottlenecks)
        }


# Global resource planning manager
resource_planning_manager = ResourcePlanningManager()

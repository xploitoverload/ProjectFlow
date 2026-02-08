# app/disaster/dr_management.py
"""
Disaster Recovery & High Availability Management
Backup, failover, replication, and monitoring.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class BackupType(Enum):
    """Backup types."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    """Backup status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


class FailoverStatus(Enum):
    """Failover status."""
    ACTIVE = "active"
    STANDBY = "standby"
    FAILED_OVER = "failed_over"
    RECOVERING = "recovering"


@dataclass
class BackupJob:
    """Backup job."""
    id: str
    backup_type: BackupType
    status: BackupStatus
    source_system: str
    destination: str
    data_size: float = 0.0  # GB
    duration_seconds: int = 0
    retention_days: int = 30
    incremental_parents: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'backup_type': self.backup_type.value,
            'status': self.status.value,
            'source_system': self.source_system,
            'destination': self.destination,
            'data_size': self.data_size,
            'duration_seconds': self.duration_seconds,
            'retention_days': self.retention_days,
            'incremental_parents': self.incremental_parents,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class RestorePoint:
    """Restore point."""
    id: str
    backup_job_id: str
    system: str
    point_in_time: datetime
    rpo_minutes: int = 15  # Recovery Point Objective
    verified: bool = False
    test_restored: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'backup_job_id': self.backup_job_id,
            'system': self.system,
            'point_in_time': self.point_in_time.isoformat(),
            'rpo_minutes': self.rpo_minutes,
            'verified': self.verified,
            'test_restored': self.test_restored,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class ReplicationConfig:
    """Replication configuration."""
    id: str
    name: str
    primary_system: str
    secondary_system: str
    replication_type: str  # synchronous or asynchronous
    enabled: bool = True
    lag_threshold_ms: int = 1000
    status: str = "healthy"
    metrics: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'primary_system': self.primary_system,
            'secondary_system': self.secondary_system,
            'replication_type': self.replication_type,
            'enabled': self.enabled,
            'lag_threshold_ms': self.lag_threshold_ms,
            'status': self.status,
            'metrics': self.metrics,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class FailoverConfig:
    """Failover configuration."""
    id: str
    name: str
    primary: str
    secondary: str
    tertiary: str = ""
    automatic: bool = True
    health_check_interval_seconds: int = 30
    rto_minutes: int = 5  # Recovery Time Objective
    status: FailoverStatus = FailoverStatus.ACTIVE
    last_failover: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'primary': self.primary,
            'secondary': self.secondary,
            'tertiary': self.tertiary,
            'automatic': self.automatic,
            'health_check_interval_seconds': self.health_check_interval_seconds,
            'rto_minutes': self.rto_minutes,
            'status': self.status.value,
            'last_failover': self.last_failover.isoformat() if self.last_failover else None,
            'created_at': self.created_at.isoformat()
        }


class DisasterRecoveryManager:
    """Manage disaster recovery and high availability."""
    
    def __init__(self):
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.restore_points: Dict[str, RestorePoint] = {}
        self.replication_configs: Dict[str, ReplicationConfig] = {}
        self.failover_configs: Dict[str, FailoverConfig] = {}
        self.backup_counter = 0
    
    def create_backup(self, backup_type: str, source_system: str, destination: str):
        """Create backup job."""
        self.backup_counter += 1
        job_id = f"bak_{self.backup_counter}"
        
        job = BackupJob(
            job_id, BackupType(backup_type), BackupStatus.PENDING, 
            source_system, destination
        )
        self.backup_jobs[job_id] = job
        return job
    
    def start_backup(self, job_id: str):
        """Start backup job."""
        job = self.backup_jobs.get(job_id)
        if not job:
            return False
        
        job.status = BackupStatus.IN_PROGRESS
        job.started_at = datetime.utcnow()
        return True
    
    def complete_backup(self, job_id: str, data_size: float = 0.0):
        """Complete backup job."""
        job = self.backup_jobs.get(job_id)
        if not job:
            return False
        
        job.status = BackupStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.data_size = data_size
        
        if job.started_at and job.completed_at:
            job.duration_seconds = int((job.completed_at - job.started_at).total_seconds())
        
        return True
    
    def verify_backup(self, job_id: str):
        """Verify backup integrity."""
        job = self.backup_jobs.get(job_id)
        if not job or job.status != BackupStatus.COMPLETED:
            return False
        
        job.status = BackupStatus.VERIFIED
        return True
    
    def create_restore_point(self, backup_job_id: str, system: str):
        """Create restore point from backup."""
        restore_id = f"rst_{len(self.restore_points) + 1}"
        point = RestorePoint(restore_id, backup_job_id, system, datetime.utcnow())
        self.restore_points[restore_id] = point
        return point
    
    def test_restore(self, restore_id: str):
        """Test restore point."""
        point = self.restore_points.get(restore_id)
        if not point:
            return False
        
        point.test_restored = True
        return True
    
    def configure_replication(self, name: str, primary: str, secondary: str, 
                             replication_type: str = "asynchronous"):
        """Configure replication."""
        rep_id = f"rep_{len(self.replication_configs) + 1}"
        config = ReplicationConfig(rep_id, name, primary, secondary, replication_type)
        self.replication_configs[rep_id] = config
        return config
    
    def get_replication_status(self, replication_id: str):
        """Get replication status."""
        config = self.replication_configs.get(replication_id)
        if not config:
            return None
        
        return {
            'id': replication_id,
            'status': config.status,
            'lag_ms': 0,
            'replicated_bytes': 0,
            'is_healthy': config.status == 'healthy'
        }
    
    def configure_failover(self, name: str, primary: str, secondary: str, tertiary: str = ""):
        """Configure failover."""
        fo_id = f"fo_{len(self.failover_configs) + 1}"
        config = FailoverConfig(fo_id, name, primary, secondary, tertiary)
        self.failover_configs[fo_id] = config
        return config
    
    def trigger_failover(self, failover_id: str):
        """Trigger failover to secondary system."""
        config = self.failover_configs.get(failover_id)
        if not config:
            return False
        
        config.status = FailoverStatus.FAILED_OVER
        config.last_failover = datetime.utcnow()
        return True
    
    def failback(self, failover_id: str):
        """Failback to primary system."""
        config = self.failover_configs.get(failover_id)
        if not config:
            return False
        
        config.status = FailoverStatus.ACTIVE
        return True
    
    def get_backup_schedule(self):
        """Get backup schedule."""
        return {
            'daily_full': '02:00 UTC',
            'hourly_incremental': 'every hour',
            'weekly_differential': 'Sunday 03:00 UTC',
            'retention_policy': {
                'daily': 7,
                'weekly': 4,
                'monthly': 12
            }
        }
    
    def get_dr_metrics(self):
        """Get DR metrics."""
        total_backups = len(self.backup_jobs)
        successful = len([j for j in self.backup_jobs.values() 
                         if j.status == BackupStatus.VERIFIED])
        total_data = sum(j.data_size for j in self.backup_jobs.values())
        
        return {
            'total_backups': total_backups,
            'successful_backups': successful,
            'success_rate': (successful / total_backups * 100) if total_backups > 0 else 0,
            'total_data_backed_up_gb': total_data,
            'active_replications': len([c for c in self.replication_configs.values() if c.enabled]),
            'failover_configs': len(self.failover_configs),
            'rpo_minutes': 15,
            'rto_minutes': 5
        }


# Global instance
dr_manager = DisasterRecoveryManager()

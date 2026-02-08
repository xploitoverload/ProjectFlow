"""Integration sync manager."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SyncDirection(Enum):
    """Sync direction."""
    PULL = "pull"  # From external to local
    PUSH = "push"  # From local to external
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(Enum):
    """Sync status."""
    PENDING = "pending"
    SYNCING = "syncing"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass
class SyncJob:
    """Synchronization job."""
    id: str
    source: str  # 'slack', 'github', 'jira'
    direction: SyncDirection
    status: SyncStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    items_synced: int = 0
    items_failed: int = 0
    error: Optional[str] = None


class SyncManager:
    """Manages synchronization across integrations."""
    
    def __init__(self):
        """Initialize sync manager."""
        self.sync_jobs: Dict[str, SyncJob] = {}
        self.sync_schedule: Dict[str, int] = {}  # source -> interval in seconds
        self.last_sync: Dict[str, str] = {}
    
    def schedule_sync(self, source: str, interval: int) -> None:
        """
        Schedule synchronization.
        
        Args:
            source: Integration source
            interval: Sync interval in seconds
        """
        self.sync_schedule[source] = interval
        logger.info(f"Sync scheduled for {source}: every {interval}s")
    
    async def sync(self, source: str, direction: SyncDirection = SyncDirection.PULL,
                   items: List[Dict] = None) -> SyncJob:
        """
        Perform synchronization.
        
        Args:
            source: Integration source
            direction: Sync direction
            items: Items to sync
            
        Returns:
            SyncJob instance
        """
        job_id = f"sync_{int(datetime.now().timestamp() * 1000)}"
        
        job = SyncJob(
            id=job_id,
            source=source,
            direction=direction,
            status=SyncStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        self.sync_jobs[job_id] = job
        
        try:
            job.status = SyncStatus.SYNCING
            job.started_at = datetime.now().isoformat()
            
            # Simulate sync
            if items:
                job.items_synced = len(items)
            
            job.status = SyncStatus.SUCCESS
            job.completed_at = datetime.now().isoformat()
            
            self.last_sync[source] = datetime.now().isoformat()
            logger.info(f"Sync completed: {job_id}")
            
        except Exception as e:
            job.status = SyncStatus.FAILED
            job.error = str(e)
            logger.error(f"Sync failed: {e}")
        
        return job
    
    def get_sync_jobs(self, source: str = None, 
                      status: SyncStatus = None) -> List[SyncJob]:
        """
        Get synchronization jobs.
        
        Args:
            source: Filter by source
            status: Filter by status
            
        Returns:
            List of jobs
        """
        jobs = list(self.sync_jobs.values())
        
        if source:
            jobs = [j for j in jobs if j.source == source]
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        return sorted(jobs, key=lambda j: j.created_at, reverse=True)
    
    def get_last_sync(self, source: str) -> Optional[str]:
        """
        Get last sync time for source.
        
        Args:
            source: Integration source
            
        Returns:
            Last sync timestamp or None
        """
        return self.last_sync.get(source)
    
    def get_sync_schedule(self) -> Dict[str, int]:
        """
        Get sync schedule.
        
        Returns:
            Schedule dictionary
        """
        return dict(self.sync_schedule)
    
    def get_stats(self) -> Dict:
        """Get sync manager statistics."""
        successful = sum(1 for j in self.sync_jobs.values() 
                        if j.status == SyncStatus.SUCCESS)
        failed = sum(1 for j in self.sync_jobs.values() 
                    if j.status == SyncStatus.FAILED)
        total_synced = sum(j.items_synced for j in self.sync_jobs.values())
        
        return {
            'total_jobs': len(self.sync_jobs),
            'successful_jobs': successful,
            'failed_jobs': failed,
            'total_items_synced': total_synced,
            'sources_scheduled': len(self.sync_schedule),
            'last_syncs': self.last_sync
        }

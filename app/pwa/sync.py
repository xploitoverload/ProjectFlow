"""Background synchronization management."""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class SyncEventType(Enum):
    """Types of sync events."""
    BEFORE_SYNC = "before_sync"
    SYNC_SUCCESS = "sync_success"
    SYNC_FAILURE = "sync_failure"
    SYNC_COMPLETE = "sync_complete"
    DATA_CHANGED = "data_changed"


@dataclass
class SyncEvent:
    """Represents a sync event."""
    type: SyncEventType
    timestamp: str
    data: Dict = None
    error: Optional[str] = None


@dataclass
class SyncSchedule:
    """Background sync schedule."""
    id: str
    name: str
    tag: str
    interval: int  # seconds
    max_sync_attempts: int = 3
    last_sync: Optional[str] = None
    next_sync: Optional[str] = None
    enabled: bool = True


class BackgroundSyncManager:
    """Manages background synchronization."""
    
    def __init__(self):
        """Initialize background sync manager."""
        self.schedules: Dict[str, SyncSchedule] = {}
        self.sync_events: List[SyncEvent] = []
        self.sync_handlers: Dict[str, List[Callable]] = {}
        self.last_sync_time: Optional[datetime] = None
        self.is_syncing = False
        self._setup_default_schedules()
    
    def _setup_default_schedules(self):
        """Setup default sync schedules."""
        schedules = [
            SyncSchedule(
                id='data-sync',
                name='Data Synchronization',
                tag='sync-data',
                interval=300  # 5 minutes
            ),
            SyncSchedule(
                id='notification-sync',
                name='Notification Sync',
                tag='sync-notifications',
                interval=60  # 1 minute
            ),
            SyncSchedule(
                id='presence-sync',
                name='Presence Update',
                tag='sync-presence',
                interval=30  # 30 seconds
            ),
            SyncSchedule(
                id='cache-cleanup',
                name='Cache Cleanup',
                tag='cleanup-cache',
                interval=3600  # 1 hour
            )
        ]
        
        for schedule in schedules:
            self.register_schedule(schedule)
    
    def register_schedule(self, schedule: SyncSchedule) -> None:
        """
        Register a sync schedule.
        
        Args:
            schedule: SyncSchedule instance
        """
        self.schedules[schedule.id] = schedule
        schedule.next_sync = (
            datetime.now() + timedelta(seconds=schedule.interval)
        ).isoformat()
        logger.info(f"Registered sync schedule: {schedule.name}")
    
    def register_sync_handler(self, tag: str, handler: Callable) -> None:
        """
        Register handler for sync events.
        
        Args:
            tag: Sync tag
            handler: Callable handler
        """
        if tag not in self.sync_handlers:
            self.sync_handlers[tag] = []
        
        self.sync_handlers[tag].append(handler)
        logger.info(f"Registered sync handler for tag: {tag}")
    
    def trigger_sync(self, tag: str, data: Dict = None) -> Dict:
        """
        Trigger synchronization.
        
        Args:
            tag: Sync tag
            data: Sync data
            
        Returns:
            Sync result
        """
        if self.is_syncing:
            logger.warning("Sync already in progress")
            return {'status': 'already_syncing'}
        
        self.is_syncing = True
        self._record_event(SyncEventType.BEFORE_SYNC, data or {})
        
        try:
            # Execute handlers
            results = []
            if tag in self.sync_handlers:
                for handler in self.sync_handlers[tag]:
                    try:
                        result = handler(data or {})
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Sync handler error: {e}")
                        self._record_event(
                            SyncEventType.SYNC_FAILURE,
                            {'tag': tag},
                            str(e)
                        )
            
            # Update schedule
            if tag in self.schedules:
                schedule = self.schedules[tag]
                schedule.last_sync = datetime.now().isoformat()
                schedule.next_sync = (
                    datetime.now() + timedelta(seconds=schedule.interval)
                ).isoformat()
            
            self.last_sync_time = datetime.now()
            self._record_event(SyncEventType.SYNC_SUCCESS, {'tag': tag})
            
            return {
                'status': 'success',
                'tag': tag,
                'timestamp': datetime.now().isoformat(),
                'handlers_executed': len(results)
            }
        
        except Exception as e:
            logger.error(f"Sync error: {e}")
            self._record_event(SyncEventType.SYNC_FAILURE, {'tag': tag}, str(e))
            return {
                'status': 'failed',
                'error': str(e)
            }
        
        finally:
            self.is_syncing = False
            self._record_event(SyncEventType.SYNC_COMPLETE, {'tag': tag})
    
    def get_javascript_code(self) -> str:
        """
        Get JavaScript code for background sync.
        
        Returns:
            JavaScript code
        """
        return """
// Background Sync API
async function registerBackgroundSync(tag) {
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        try {
            const registration = await navigator.serviceWorker.ready;
            await registration.sync.register(tag);
            console.log('[Sync] Registered background sync:', tag);
        } catch (error) {
            console.error('[Sync] Failed to register:', error);
        }
    }
}

// Periodic background sync
async function registerPeriodicSync(tag, minInterval) {
    if ('serviceWorker' in navigator && 'PeriodicSyncManager' in window) {
        try {
            const registration = await navigator.serviceWorker.ready;
            await registration.periodicSync.register(tag, {
                minInterval: minInterval
            });
            console.log('[Sync] Registered periodic sync:', tag);
        } catch (error) {
            console.error('[Sync] Failed to register periodic sync:', error);
        }
    }
}

// Sync data with server
async function syncWithServer(endpoint, data) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            console.log('[Sync] Data synced successfully');
            return { status: 'success' };
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('[Sync] Sync failed:', error);
        return { status: 'failed', error: error.message };
    }
}

// Listen for sync events
window.addEventListener('online', () => {
    console.log('[Sync] Online - triggering sync');
    registerBackgroundSync('sync-data');
});

// Request periodic sync
function setupPeriodicSync() {
    registerPeriodicSync('sync-data', 5 * 60 * 1000); // 5 minutes
}

// Periodic heartbeat
function setupHeartbeat(interval = 30000) {
    setInterval(async () => {
        if (navigator.onLine) {
            await syncWithServer('/api/v1/pwa/heartbeat', {
                timestamp: new Date().toISOString()
            });
        }
    }, interval);
}

// Initialize sync
document.addEventListener('DOMContentLoaded', () => {
    setupPeriodicSync();
    setupHeartbeat();
});
"""
    
    def _record_event(self, event_type: SyncEventType, data: Dict = None,
                      error: str = None) -> None:
        """
        Record a sync event.
        
        Args:
            event_type: Type of event
            data: Event data
            error: Error message
        """
        event = SyncEvent(
            type=event_type,
            timestamp=datetime.now().isoformat(),
            data=data,
            error=error
        )
        self.sync_events.append(event)
        
        # Keep only last 1000 events
        if len(self.sync_events) > 1000:
            self.sync_events = self.sync_events[-1000:]
    
    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        """
        Get recent sync events.
        
        Args:
            limit: Maximum events to return
            
        Returns:
            List of events
        """
        return [
            {
                'type': e.type.value,
                'timestamp': e.timestamp,
                'data': e.data,
                'error': e.error
            }
            for e in self.sync_events[-limit:]
        ]
    
    def get_sync_status(self) -> Dict:
        """
        Get current sync status.
        
        Returns:
            Dictionary with status
        """
        return {
            'is_syncing': self.is_syncing,
            'last_sync': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'schedules': [
                {
                    'id': s.id,
                    'name': s.name,
                    'enabled': s.enabled,
                    'interval': s.interval,
                    'last_sync': s.last_sync,
                    'next_sync': s.next_sync
                }
                for s in self.schedules.values()
            ],
            'recent_events': self.get_recent_events(10)
        }
    
    def get_stats(self) -> Dict:
        """
        Get background sync statistics.
        
        Returns:
            Dictionary with stats
        """
        event_counts = {}
        for event in self.sync_events:
            event_type = event.type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            'is_syncing': self.is_syncing,
            'schedules_count': len(self.schedules),
            'handlers_registered': sum(len(h) for h in self.sync_handlers.values()),
            'total_events': len(self.sync_events),
            'event_breakdown': event_counts,
            'last_sync': self.last_sync_time.isoformat() if self.last_sync_time else None
        }

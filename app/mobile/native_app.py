# app/mobile/native_app.py
"""
Mobile Native App APIs
Support for iOS/Android clients with offline sync, push notifications, and device management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid


class DevicePlatform(Enum):
    """Mobile device platforms."""
    IOS = "ios"
    ANDROID = "android"
    WINDOWS = "windows"


class SyncStatus(Enum):
    """Data sync status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SYNCED = "synced"
    FAILED = "failed"


@dataclass
class MobileDevice:
    """Registered mobile device."""
    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    platform: DevicePlatform = DevicePlatform.ANDROID
    app_version: str = ""
    os_version: str = ""
    device_name: str = ""
    push_token: str = ""
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_sync: Optional[datetime] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict:
        return {
            'device_id': self.device_id,
            'platform': self.platform.value,
            'app_version': self.app_version,
            'os_version': self.os_version,
            'device_name': self.device_name,
            'registered_at': self.registered_at.isoformat(),
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'is_active': self.is_active
        }


@dataclass
class SyncJob:
    """Data synchronization job."""
    sync_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str = ""
    sync_type: str = ""  # pull, push, bidirectional
    status: SyncStatus = SyncStatus.PENDING
    records_count: int = 0
    synced_count: int = 0
    failed_count: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'sync_id': self.sync_id,
            'device_id': self.device_id,
            'sync_type': self.sync_type,
            'status': self.status.value,
            'progress': round((self.synced_count / max(self.records_count, 1)) * 100, 1),
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class OfflineData:
    """Offline data cached on device."""
    data_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str = ""
    entity_type: str = ""  # projects, tasks, etc
    entity_id: str = ""
    data: Dict = field(default_factory=dict)
    cached_at: datetime = field(default_factory=datetime.utcnow)
    synced: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'data_id': self.data_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'cached_at': self.cached_at.isoformat(),
            'synced': self.synced
        }


class MobileNativeAppManager:
    """
    Manages mobile native app functionality for iOS and Android.
    """
    
    def __init__(self):
        """Initialize mobile app manager."""
        self.devices: Dict[str, MobileDevice] = {}
        self.sync_jobs: Dict[str, SyncJob] = {}
        self.offline_data: Dict[str, OfflineData] = {}
        self.device_users: Dict[str, List[str]] = {}  # user_id -> device_ids
        self.stats = {
            'total_devices': 0,
            'active_devices': 0,
            'total_syncs': 0,
            'successful_syncs': 0
        }
    
    def register_device(self, user_id: str, platform: str, app_version: str,
                       os_version: str, device_name: str,
                       push_token: str = "") -> MobileDevice:
        """Register mobile device."""
        try:
            platform_enum = DevicePlatform[platform.upper()]
        except KeyError:
            platform_enum = DevicePlatform.ANDROID
        
        device = MobileDevice(
            user_id=user_id,
            platform=platform_enum,
            app_version=app_version,
            os_version=os_version,
            device_name=device_name,
            push_token=push_token
        )
        
        self.devices[device.device_id] = device
        
        if user_id not in self.device_users:
            self.device_users[user_id] = []
        self.device_users[user_id].append(device.device_id)
        
        self.stats['total_devices'] += 1
        self.stats['active_devices'] += 1
        
        return device
    
    def get_user_devices(self, user_id: str) -> List[Dict]:
        """Get all devices for user."""
        if user_id not in self.device_users:
            return []
        
        return [self.devices[did].to_dict() for did in self.device_users[user_id]
               if did in self.devices]
    
    def create_sync_job(self, device_id: str, sync_type: str,
                       records_count: int = 0) -> SyncJob:
        """Create synchronization job."""
        sync_job = SyncJob(
            device_id=device_id,
            sync_type=sync_type,
            records_count=records_count,
            status=SyncStatus.IN_PROGRESS
        )
        
        self.sync_jobs[sync_job.sync_id] = sync_job
        self.stats['total_syncs'] += 1
        
        return sync_job
    
    def update_sync_progress(self, sync_id: str, synced_count: int,
                            failed_count: int = 0) -> bool:
        """Update sync progress."""
        if sync_id not in self.sync_jobs:
            return False
        
        sync_job = self.sync_jobs[sync_id]
        sync_job.synced_count = synced_count
        sync_job.failed_count = failed_count
        
        # Mark complete if all synced
        if synced_count + failed_count >= sync_job.records_count:
            sync_job.status = SyncStatus.SYNCED if failed_count == 0 else SyncStatus.FAILED
            sync_job.completed_at = datetime.utcnow()
            
            if failed_count == 0:
                self.stats['successful_syncs'] += 1
                
                # Update device last sync
                if sync_job.device_id in self.devices:
                    self.devices[sync_job.device_id].last_sync = datetime.utcnow()
        
        return True
    
    def cache_offline_data(self, device_id: str, entity_type: str,
                          entity_id: str, data: Dict) -> OfflineData:
        """Cache data for offline access."""
        offline_data = OfflineData(
            device_id=device_id,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data
        )
        
        self.offline_data[offline_data.data_id] = offline_data
        return offline_data
    
    def get_offline_data(self, device_id: str, entity_type: str = None) -> List[Dict]:
        """Get offline cached data."""
        results = []
        
        for data in self.offline_data.values():
            if data.device_id == device_id:
                if entity_type is None or data.entity_type == entity_type:
                    results.append(data.to_dict())
        
        return results
    
    def mark_offline_data_synced(self, data_ids: List[str]) -> int:
        """Mark offline data as synced."""
        count = 0
        for data_id in data_ids:
            if data_id in self.offline_data:
                self.offline_data[data_id].synced = True
                count += 1
        
        return count
    
    def check_app_update(self, platform: str, current_version: str) -> Dict:
        """Check if app update is available."""
        # Simulate version checking
        latest_versions = {
            'ios': '2.5.0',
            'android': '2.5.0'
        }
        
        latest = latest_versions.get(platform.lower(), current_version)
        needs_update = latest > current_version
        
        return {
            'current_version': current_version,
            'latest_version': latest,
            'update_available': needs_update,
            'force_update': False,
            'update_url': f'https://app.store/{platform}/v{latest}' if needs_update else None
        }
    
    def get_device_analytics(self, device_id: str) -> Dict:
        """Get analytics for device."""
        if device_id not in self.devices:
            return {'error': 'Device not found'}
        
        device = self.devices[device_id]
        device_syncs = [s for s in self.sync_jobs.values() if s.device_id == device_id]
        
        return {
            'device_id': device_id,
            'platform': device.platform.value,
            'total_syncs': len(device_syncs),
            'successful_syncs': sum(1 for s in device_syncs if s.status == SyncStatus.SYNCED),
            'failed_syncs': sum(1 for s in device_syncs if s.status == SyncStatus.FAILED),
            'cached_items': len([d for d in self.offline_data.values() if d.device_id == device_id]),
            'last_sync': device.last_sync.isoformat() if device.last_sync else None
        }
    
    def get_stats(self) -> Dict:
        """Get mobile app statistics."""
        active = sum(1 for d in self.devices.values() if d.is_active)
        
        return {
            'total_devices': self.stats['total_devices'],
            'active_devices': active,
            'ios_devices': sum(1 for d in self.devices.values() if d.platform == DevicePlatform.IOS),
            'android_devices': sum(1 for d in self.devices.values() if d.platform == DevicePlatform.ANDROID),
            'total_syncs': self.stats['total_syncs'],
            'successful_syncs': self.stats['successful_syncs'],
            'sync_success_rate': round(
                self.stats['successful_syncs'] / max(self.stats['total_syncs'], 1) * 100, 1
            ),
            'cached_items': len(self.offline_data)
        }


# Global mobile app manager
mobile_manager = MobileNativeAppManager()

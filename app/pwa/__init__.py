"""
Progressive Web App (PWA) module.

Provides PWA capabilities including service workers, offline support,
web manifest, and installability features.
"""

from .service_worker import ServiceWorkerManager
from .manifest import ManifestGenerator
from .offline import OfflineManager
from .sync import BackgroundSyncManager

# Global instances
service_worker_manager = ServiceWorkerManager()
manifest_generator = ManifestGenerator()
offline_manager = OfflineManager()
background_sync_manager = BackgroundSyncManager()

__all__ = [
    'ServiceWorkerManager',
    'ManifestGenerator',
    'OfflineManager',
    'BackgroundSyncManager',
    'service_worker_manager',
    'manifest_generator',
    'offline_manager',
    'background_sync_manager',
]

"""Offline support and data synchronization."""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Synchronization status."""
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"


@dataclass
class OfflineRequest:
    """Represents an offline request to be synced."""
    id: str
    method: str  # GET, POST, PUT, DELETE
    endpoint: str
    data: Optional[Dict] = None
    headers: Optional[Dict] = None
    timestamp: str = None
    status: SyncStatus = SyncStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class OfflineManager:
    """Manages offline data and synchronization."""
    
    def __init__(self):
        """Initialize offline manager."""
        self.offline_requests: Dict[str, OfflineRequest] = {}
        self.cached_data: Dict[str, Any] = {}
        self.sync_enabled = True
        self.sync_interval = 30  # seconds
        self.offline_threshold = 3600  # 1 hour
    
    def add_offline_request(self, method: str, endpoint: str, 
                           data: Optional[Dict] = None,
                           headers: Optional[Dict] = None) -> str:
        """
        Add a request to be synced when online.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            headers: Request headers
            
        Returns:
            Request ID
        """
        request_id = f"req_{int(datetime.now().timestamp() * 1000)}"
        
        request = OfflineRequest(
            id=request_id,
            method=method,
            endpoint=endpoint,
            data=data,
            headers=headers
        )
        
        self.offline_requests[request_id] = request
        logger.info(f"Added offline request: {request_id}")
        
        return request_id
    
    def get_pending_requests(self) -> List[OfflineRequest]:
        """
        Get all pending offline requests.
        
        Returns:
            List of pending requests
        """
        return [
            req for req in self.offline_requests.values()
            if req.status == SyncStatus.PENDING
        ]
    
    def mark_as_syncing(self, request_id: str) -> None:
        """
        Mark request as syncing.
        
        Args:
            request_id: Request ID
        """
        if request_id in self.offline_requests:
            self.offline_requests[request_id].status = SyncStatus.SYNCING
    
    def mark_as_synced(self, request_id: str) -> None:
        """
        Mark request as successfully synced.
        
        Args:
            request_id: Request ID
        """
        if request_id in self.offline_requests:
            req = self.offline_requests[request_id]
            req.status = SyncStatus.SYNCED
            logger.info(f"Request synced: {request_id}")
    
    def mark_as_failed(self, request_id: str, error: str = None) -> None:
        """
        Mark request as failed.
        
        Args:
            request_id: Request ID
            error: Error message
        """
        if request_id in self.offline_requests:
            req = self.offline_requests[request_id]
            req.status = SyncStatus.FAILED
            req.error = error
            req.retry_count += 1
            logger.warning(f"Request failed: {request_id} - {error}")
    
    def should_retry(self, request_id: str) -> bool:
        """
        Check if request should be retried.
        
        Args:
            request_id: Request ID
            
        Returns:
            True if should retry
        """
        if request_id not in self.offline_requests:
            return False
        
        req = self.offline_requests[request_id]
        return req.retry_count < req.max_retries and req.status in [
            SyncStatus.FAILED,
            SyncStatus.PENDING
        ]
    
    def cache_data(self, key: str, data: Any, ttl: int = 3600) -> None:
        """
        Cache data for offline use.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
        """
        self.cached_data[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'ttl': ttl,
            'expires': (datetime.now() + timedelta(seconds=ttl)).isoformat()
        }
        logger.info(f"Cached data: {key}")
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """
        Get cached data.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if expired
        """
        if key not in self.cached_data:
            return None
        
        cached = self.cached_data[key]
        
        # Check if expired
        expires = datetime.fromisoformat(cached['expires'])
        if datetime.now() > expires:
            del self.cached_data[key]
            logger.info(f"Cache expired: {key}")
            return None
        
        return cached['data']
    
    def clear_expired_cache(self) -> int:
        """
        Remove all expired cached data.
        
        Returns:
            Number of items cleared
        """
        now = datetime.now()
        expired_keys = [
            key for key, cached in self.cached_data.items()
            if datetime.fromisoformat(cached['expires']) < now
        ]
        
        for key in expired_keys:
            del self.cached_data[key]
        
        logger.info(f"Cleared {len(expired_keys)} expired cache items")
        return len(expired_keys)
    
    def get_offline_fallback_page(self) -> str:
        """
        Get fallback HTML page for offline mode.
        
        Returns:
            HTML string
        """
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline - Project Management</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .offline-container {
            background: white;
            border-radius: 12px;
            padding: 48px 32px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            text-align: center;
        }
        
        .offline-icon {
            font-size: 64px;
            margin-bottom: 24px;
        }
        
        h1 {
            font-size: 28px;
            color: #1f2937;
            margin-bottom: 12px;
        }
        
        .offline-message {
            font-size: 16px;
            color: #6b7280;
            margin-bottom: 32px;
            line-height: 1.6;
        }
        
        .offline-suggestions {
            background: #f3f4f6;
            border-left: 4px solid #667eea;
            padding: 16px;
            margin-bottom: 32px;
            text-align: left;
            border-radius: 4px;
        }
        
        .offline-suggestions h3 {
            font-size: 14px;
            color: #1f2937;
            margin-bottom: 8px;
        }
        
        .offline-suggestions ul {
            font-size: 14px;
            color: #6b7280;
            list-style: none;
            padding-left: 0;
        }
        
        .offline-suggestions li {
            padding: 4px 0;
        }
        
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 32px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #5568d3;
        }
        
        .sync-status {
            margin-top: 24px;
            padding-top: 24px;
            border-top: 1px solid #e5e7eb;
            font-size: 12px;
            color: #9ca3af;
        }
    </style>
</head>
<body>
    <div class="offline-container">
        <div class="offline-icon">📡</div>
        <h1>You're Offline</h1>
        <p class="offline-message">
            It looks like you've lost your internet connection. 
            Don't worry, you can still view cached data.
        </p>
        
        <div class="offline-suggestions">
            <h3>What you can do:</h3>
            <ul>
                <li>✓ View previously loaded projects</li>
                <li>✓ Read cached documents</li>
                <li>✓ Take notes (synced when online)</li>
                <li>✗ Create new issues (will sync when online)</li>
                <li>✗ Update team members</li>
            </ul>
        </div>
        
        <button onclick="location.reload()">Try Again</button>
        
        <div class="sync-status">
            Pending changes will sync automatically when you're back online
        </div>
    </div>
</body>
</html>
"""
    
    def get_stats(self) -> Dict:
        """
        Get offline manager statistics.
        
        Returns:
            Dictionary with stats
        """
        pending = sum(1 for r in self.offline_requests.values() if r.status == SyncStatus.PENDING)
        synced = sum(1 for r in self.offline_requests.values() if r.status == SyncStatus.SYNCED)
        failed = sum(1 for r in self.offline_requests.values() if r.status == SyncStatus.FAILED)
        
        return {
            'sync_enabled': self.sync_enabled,
            'pending_requests': pending,
            'synced_requests': synced,
            'failed_requests': failed,
            'total_requests': len(self.offline_requests),
            'cached_items': len(self.cached_data),
            'sync_interval': self.sync_interval
        }

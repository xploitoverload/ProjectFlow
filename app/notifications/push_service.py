"""Web Push Service implementation."""

import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PushConfig:
    """Push notification configuration."""
    vapid_public_key: str
    vapid_private_key: str
    api_key: str = None  # For Firebase Cloud Messaging
    project_id: str = None  # For FCM
    sender_id: str = None  # For FCM


class PushService:
    """Web Push Service implementation."""
    
    def __init__(self):
        """Initialize push service."""
        self.config: Optional[PushConfig] = None
        self.is_configured = False
        self.delivery_attempts: Dict[str, int] = {}
        self.failed_deliveries: List[Dict] = []
        self.successful_deliveries: List[Dict] = []
    
    def configure(self, vapid_public: str, vapid_private: str, 
                  api_key: str = None, project_id: str = None,
                  sender_id: str = None) -> None:
        """
        Configure push service with VAPID credentials.
        
        Args:
            vapid_public: VAPID public key
            vapid_private: VAPID private key
            api_key: Firebase API key (optional)
            project_id: Firebase project ID (optional)
            sender_id: Firebase sender ID (optional)
        """
        self.config = PushConfig(
            vapid_public_key=vapid_public,
            vapid_private_key=vapid_private,
            api_key=api_key,
            project_id=project_id,
            sender_id=sender_id
        )
        self.is_configured = True
        logger.info("Push service configured")
    
    def get_vapid_keys(self) -> Dict[str, str]:
        """
        Get VAPID public key for client registration.
        
        Returns:
            Dictionary with public key
        """
        if not self.is_configured or not self.config:
            raise RuntimeError("Push service not configured")
        
        return {
            'public_key': self.config.vapid_public_key
        }
    
    async def send_push(self, subscription: Dict, payload: Dict,
                       notification_id: str = None) -> Dict:
        """
        Send push notification to subscription.
        
        Args:
            subscription: Push subscription object
            payload: Notification payload
            notification_id: Optional notification ID
            
        Returns:
            Send result
        """
        if not self.is_configured:
            logger.error("Push service not configured")
            return {'status': 'error', 'message': 'Service not configured'}
        
        if notification_id is None:
            notification_id = f"notif_{int(datetime.now().timestamp() * 1000)}"
        
        try:
            # In production, use pywebpush or firebase-admin
            # For now, simulate the send
            result = {
                'status': 'success',
                'notification_id': notification_id,
                'endpoint': subscription.get('endpoint'),
                'timestamp': datetime.now().isoformat()
            }
            
            self.successful_deliveries.append(result)
            logger.info(f"Push sent: {notification_id}")
            
            return result
        
        except Exception as e:
            error_result = {
                'status': 'failed',
                'notification_id': notification_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            self.failed_deliveries.append(error_result)
            self.delivery_attempts[notification_id] = \
                self.delivery_attempts.get(notification_id, 0) + 1
            
            logger.error(f"Push failed: {e}")
            return error_result
    
    async def send_to_topic(self, topic: str, payload: Dict) -> Dict:
        """
        Send push notification to all subscribers of a topic.
        
        Args:
            topic: Topic name
            payload: Notification payload
            
        Returns:
            Send result with delivery stats
        """
        # In production, this would query subscriptions and send to each
        return {
            'status': 'success',
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'message': 'Topic broadcast initiated'
        }
    
    def get_javascript_registration_code(self) -> str:
        """
        Get JavaScript code for push subscription registration.
        
        Returns:
            JavaScript code
        """
        return """
// Push Notification Registration
async function registerPushNotifications() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.log('[Push] Push notifications not supported');
        return;
    }
    
    try {
        const registration = await navigator.serviceWorker.ready;
        
        // Get VAPID public key from server
        const response = await fetch('/api/v1/notifications/vapid-key');
        const data = await response.json();
        const vapidPublicKey = data.public_key;
        
        // Subscribe to push notifications
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
        });
        
        // Send subscription to server
        await fetch('/api/v1/notifications/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(subscription)
        });
        
        console.log('[Push] Push notifications subscribed');
    } catch (error) {
        console.error('[Push] Subscription error:', error);
    }
}

// Unsubscribe from push notifications
async function unsubscribePushNotifications() {
    if (!('serviceWorker' in navigator)) return;
    
    try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        
        if (subscription) {
            await subscription.unsubscribe();
            
            // Notify server
            await fetch('/api/v1/notifications/unsubscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(subscription)
            });
            
            console.log('[Push] Unsubscribed from push');
        }
    } catch (error) {
        console.error('[Push] Unsubscribe error:', error);
    }
}

// Get current push subscription
async function getPushSubscription() {
    if (!('serviceWorker' in navigator)) return null;
    
    try {
        const registration = await navigator.serviceWorker.ready;
        return await registration.pushManager.getSubscription();
    } catch (error) {
        console.error('[Push] Error getting subscription:', error);
        return null;
    }
}

// Request notification permission
async function requestNotificationPermission() {
    if (!('Notification' in window)) {
        console.log('[Push] Notification API not supported');
        return false;
    }
    
    if (Notification.permission === 'granted') {
        return true;
    }
    
    if (Notification.permission !== 'denied') {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            registerPushNotifications();
            return true;
        }
    }
    
    return false;
}

// Helper function for VAPID key conversion
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\\-/g, '+')
        .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    
    return outputArray;
}

// Initialize push on page load
document.addEventListener('DOMContentLoaded', async () => {
    if (Notification.permission === 'granted') {
        await registerPushNotifications();
    } else if (Notification.permission !== 'denied') {
        const enablePushBtn = document.getElementById('enable-push-btn');
        if (enablePushBtn) {
            enablePushBtn.onclick = requestNotificationPermission;
        }
    }
});
"""
    
    def get_stats(self) -> Dict:
        """
        Get push service statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            'is_configured': self.is_configured,
            'successful_deliveries': len(self.successful_deliveries),
            'failed_deliveries': len(self.failed_deliveries),
            'delivery_attempts': len(self.delivery_attempts),
            'vapid_configured': bool(self.config and self.config.vapid_public_key)
        }

"""Notification engine and management."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications."""
    ISSUE_CREATED = "issue_created"
    ISSUE_ASSIGNED = "issue_assigned"
    ISSUE_UPDATED = "issue_updated"
    COMMENT_ADDED = "comment_added"
    MENTION = "mention"
    DEADLINE_REMINDER = "deadline_reminder"
    SYSTEM_ALERT = "system_alert"
    TEAM_UPDATE = "team_update"
    PROJECT_UPDATE = "project_update"


@dataclass
class NotificationPreferences:
    """User notification preferences."""
    user_id: str
    enabled: bool = True
    email_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    notification_types: Dict[str, bool] = field(default_factory=dict)
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    mute_until: Optional[str] = None
    
    def __post_init__(self):
        if not self.notification_types:
            # Set defaults
            self.notification_types = {
                NotificationType.ISSUE_CREATED.value: True,
                NotificationType.ISSUE_ASSIGNED.value: True,
                NotificationType.ISSUE_UPDATED.value: True,
                NotificationType.COMMENT_ADDED.value: True,
                NotificationType.MENTION.value: True,
                NotificationType.DEADLINE_REMINDER.value: True,
            }


@dataclass
class Notification:
    """Notification object."""
    id: str
    user_id: str
    notification_type: NotificationType
    title: str
    body: str
    icon: str
    badge: str = None
    tag: str = None
    data: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    is_read: bool = False
    is_clicked: bool = False
    action_url: Optional[str] = None


class NotificationEngine:
    """Central notification engine."""
    
    def __init__(self):
        """Initialize notification engine."""
        self.notifications: Dict[str, Notification] = {}
        self.user_preferences: Dict[str, NotificationPreferences] = {}
        self.notification_queue: List[Notification] = []
        self.sent_count = 0
        self.failed_count = 0
    
    def set_user_preferences(self, user_id: str, 
                            preferences: NotificationPreferences) -> None:
        """
        Set user notification preferences.
        
        Args:
            user_id: User ID
            preferences: NotificationPreferences instance
        """
        self.user_preferences[user_id] = preferences
        logger.info(f"Preferences updated for user: {user_id}")
    
    def get_user_preferences(self, user_id: str) -> NotificationPreferences:
        """
        Get user notification preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            NotificationPreferences
        """
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = NotificationPreferences(user_id=user_id)
        
        return self.user_preferences[user_id]
    
    def create_notification(self, user_id: str, notification_type: NotificationType,
                           title: str, body: str, icon: str, 
                           data: Dict = None, action_url: str = None) -> Notification:
        """
        Create a new notification.
        
        Args:
            user_id: User ID
            notification_type: Type of notification
            title: Notification title
            body: Notification body
            icon: Icon URL
            data: Additional data
            action_url: Action URL when clicked
            
        Returns:
            Notification object
        """
        notification_id = f"notif_{int(datetime.now().timestamp() * 1000)}"
        
        notification = Notification(
            id=notification_id,
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            body=body,
            icon=icon,
            data=data or {},
            action_url=action_url,
            tag=notification_type.value
        )
        
        self.notifications[notification_id] = notification
        self.notification_queue.append(notification)
        
        logger.info(f"Notification created: {notification_id}")
        return notification
    
    def send_notification(self, notification: Notification) -> Dict:
        """
        Send a notification.
        
        Args:
            notification: Notification to send
            
        Returns:
            Send result
        """
        preferences = self.get_user_preferences(notification.user_id)
        
        # Check if notifications are enabled
        if not preferences.enabled:
            logger.warning(f"Notifications disabled for user {notification.user_id}")
            return {'status': 'disabled'}
        
        # Check notification type preference
        notif_type_key = notification.notification_type.value
        if not preferences.notification_types.get(notif_type_key, True):
            logger.warning(f"Notification type disabled for user: {notif_type_key}")
            return {'status': 'type_disabled'}
        
        # Check quiet hours
        if preferences.quiet_hours_enabled:
            # Implement quiet hours logic
            pass
        
        # Check muted
        if preferences.mute_until:
            mute_until = datetime.fromisoformat(preferences.mute_until)
            if datetime.now() < mute_until:
                return {'status': 'muted'}
        
        try:
            # Send through available channels
            results = {}
            
            if preferences.push_enabled:
                results['push'] = self._send_push(notification)
            
            if preferences.email_enabled:
                results['email'] = self._send_email(notification)
            
            if preferences.in_app_enabled:
                results['in_app'] = self._send_in_app(notification)
            
            self.sent_count += 1
            logger.info(f"Notification sent: {notification.id}")
            
            return {
                'status': 'success',
                'notification_id': notification.id,
                'channels': results
            }
        
        except Exception as e:
            self.failed_count += 1
            logger.error(f"Failed to send notification: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _send_push(self, notification: Notification) -> Dict:
        """Send push notification."""
        return {'status': 'queued', 'method': 'push'}
    
    def _send_email(self, notification: Notification) -> Dict:
        """Send email notification."""
        return {'status': 'queued', 'method': 'email'}
    
    def _send_in_app(self, notification: Notification) -> Dict:
        """Store in-app notification."""
        return {'status': 'stored', 'method': 'in_app'}
    
    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark notification as read.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            True if successful
        """
        if notification_id in self.notifications:
            self.notifications[notification_id].is_read = True
            return True
        return False
    
    def mark_as_clicked(self, notification_id: str) -> bool:
        """
        Mark notification as clicked.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            True if successful
        """
        if notification_id in self.notifications:
            self.notifications[notification_id].is_clicked = True
            return True
        return False
    
    def get_user_notifications(self, user_id: str, 
                               unread_only: bool = False) -> List[Notification]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID
            unread_only: Only return unread
            
        Returns:
            List of notifications
        """
        notifications = [
            n for n in self.notifications.values()
            if n.user_id == user_id
        ]
        
        if unread_only:
            notifications = [n for n in notifications if not n.is_read]
        
        # Sort by timestamp, newest first
        return sorted(notifications, key=lambda n: n.timestamp, reverse=True)
    
    def get_notification_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get notification history for user.
        
        Args:
            user_id: User ID
            limit: Maximum to return
            
        Returns:
            List of notification dicts
        """
        notifications = self.get_user_notifications(user_id)
        return [
            {
                'id': n.id,
                'type': n.notification_type.value,
                'title': n.title,
                'body': n.body,
                'timestamp': n.timestamp,
                'is_read': n.is_read,
                'action_url': n.action_url
            }
            for n in notifications[:limit]
        ]
    
    def mute_notifications(self, user_id: str, minutes: int = 60) -> None:
        """
        Mute notifications for a user.
        
        Args:
            user_id: User ID
            minutes: Duration in minutes
        """
        from datetime import timedelta
        mute_until = datetime.now() + timedelta(minutes=minutes)
        
        prefs = self.get_user_preferences(user_id)
        prefs.mute_until = mute_until.isoformat()
        
        logger.info(f"Notifications muted for {user_id} for {minutes} minutes")
    
    def unmute_notifications(self, user_id: str) -> None:
        """
        Unmute notifications for a user.
        
        Args:
            user_id: User ID
        """
        prefs = self.get_user_preferences(user_id)
        prefs.mute_until = None
        logger.info(f"Notifications unmuted for {user_id}")
    
    def get_stats(self) -> Dict:
        """
        Get notification engine statistics.
        
        Returns:
            Dictionary with stats
        """
        unread_count = sum(1 for n in self.notifications.values() if not n.is_read)
        
        return {
            'total_notifications': len(self.notifications),
            'unread_notifications': unread_count,
            'sent_count': self.sent_count,
            'failed_count': self.failed_count,
            'users_with_preferences': len(self.user_preferences),
            'queue_size': len(self.notification_queue)
        }

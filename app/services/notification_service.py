"""
Notification Service
Handles creating, retrieving, and managing user notifications
"""

from datetime import datetime, timedelta
from flask_login import current_user
from models import db, Notification


class NotificationService:
    """Service for managing user notifications"""
    
    @staticmethod
    def create_notification(user_id, notification_type, title, message=None, link=None, 
                          icon='bell', related_type=None, related_id=None):
        """
        Create a new notification for a user
        
        Args:
            user_id: Target user ID
            notification_type: Type of notification (issue_assigned, comment, mention, etc.)
            title: Notification title
            message: Optional detailed message
            link: Optional URL to navigate to
            icon: Lucide icon name (default: bell)
            related_type: Optional related item type
            related_id: Optional related item ID
        
        Returns:
            Notification object
        """
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            link=link,
            icon=icon,
            related_type=related_type,
            related_id=related_id
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    @staticmethod
    def get_notifications(user_id, limit=50, unread_only=False):
        """
        Get notifications for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of notifications to return
            unread_only: If True, only return unread notifications
        
        Returns:
            List of Notification objects
        """
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        
        return notifications
    
    @staticmethod
    def get_unread_count(user_id):
        """
        Get count of unread notifications for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Integer count of unread notifications
        """
        count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        return count
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """
        Mark a notification as read
        
        Args:
            notification_id: Notification ID
            user_id: User ID (for security)
        
        Returns:
            Boolean success
        """
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def mark_all_as_read(user_id):
        """
        Mark all notifications as read for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Integer count of notifications marked as read
        """
        notifications = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).all()
        
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            count += 1
        
        if count > 0:
            db.session.commit()
        
        return count
    
    @staticmethod
    def delete_notification(notification_id, user_id):
        """
        Delete a notification
        
        Args:
            notification_id: Notification ID
            user_id: User ID (for security)
        
        Returns:
            Boolean success
        """
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if notification:
            db.session.delete(notification)
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def cleanup_old_notifications(user_id, days=30):
        """
        Delete old read notifications
        
        Args:
            user_id: User ID
            days: Delete read notifications older than this many days
        
        Returns:
            Integer count of deleted notifications
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_notifications = Notification.query.filter(
            Notification.user_id == user_id,
            Notification.is_read == True,
            Notification.created_at < cutoff_date
        ).all()
        
        count = len(old_notifications)
        
        for notification in old_notifications:
            db.session.delete(notification)
        
        if count > 0:
            db.session.commit()
        
        return count
    
    @staticmethod
    def create_sample_notifications(user_id):
        """
        Create sample notifications for testing
        
        Args:
            user_id: User ID to create notifications for
        """
        samples = [
            {
                'type': 'issue_assigned',
                'title': 'Issue assigned to you',
                'message': 'PROJ-123: Fix login bug has been assigned to you',
                'link': '/issues/123',
                'icon': 'user-check',
                'related_type': 'issue',
                'related_id': 123
            },
            {
                'type': 'comment',
                'title': 'New comment on your issue',
                'message': 'John Doe commented on PROJ-124',
                'link': '/issues/124',
                'icon': 'message-square',
                'related_type': 'issue',
                'related_id': 124
            },
            {
                'type': 'mention',
                'title': 'You were mentioned',
                'message': '@admin mentioned you in a comment',
                'link': '/issues/125',
                'icon': 'at-sign',
                'related_type': 'comment',
                'related_id': 456
            },
            {
                'type': 'status_change',
                'title': 'Issue status changed',
                'message': 'PROJ-126 moved to In Progress',
                'link': '/issues/126',
                'icon': 'git-branch',
                'related_type': 'issue',
                'related_id': 126
            },
            {
                'type': 'project_update',
                'title': 'Project updated',
                'message': 'New sprint started for Test Project',
                'link': '/projects/1',
                'icon': 'calendar',
                'related_type': 'project',
                'related_id': 1
            }
        ]
        
        for sample in samples:
            NotificationService.create_notification(
                user_id=user_id,
                notification_type=sample['type'],
                title=sample['title'],
                message=sample['message'],
                link=sample['link'],
                icon=sample['icon'],
                related_type=sample.get('related_type'),
                related_id=sample.get('related_id')
            )

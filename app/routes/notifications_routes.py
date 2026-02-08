"""Push Notifications API routes."""

from flask import Blueprint, request, jsonify, current_app
from app.notifications import (
    push_service, subscription_manager,
    notification_engine, NotificationType
)
import logging

logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/v1/notifications')


@notifications_bp.route('/vapid-key', methods=['GET'])
def get_vapid_key():
    """Get VAPID public key for client registration."""
    try:
        keys = push_service.get_vapid_keys()
        return jsonify(keys)
    except Exception as e:
        logger.error(f"Error getting VAPID key: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/subscribe', methods=['POST'])
def subscribe_push():
    """Subscribe to push notifications."""
    try:
        data = request.json
        user_id = data.get('user_id')
        endpoint = data.get('endpoint')
        auth = data.get('auth')
        p256dh = data.get('p256dh')
        
        if not all([user_id, endpoint, auth, p256dh]):
            return jsonify({'error': 'Missing subscription data'}), 400
        
        subscription = subscription_manager.subscribe(user_id, endpoint, auth, p256dh)
        
        return jsonify({
            'status': 'subscribed',
            'subscription_id': subscription.id
        })
    except Exception as e:
        logger.error(f"Subscription error: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/unsubscribe', methods=['POST'])
def unsubscribe_push():
    """Unsubscribe from push notifications."""
    try:
        data = request.json
        endpoint = data.get('endpoint')
        
        if not endpoint:
            return jsonify({'error': 'Endpoint required'}), 400
        
        # Find subscription by endpoint
        subscription_id = f"sub_{hash(endpoint) % 10**8}"
        success = subscription_manager.unsubscribe(subscription_id)
        
        return jsonify({
            'status': 'unsubscribed' if success else 'not_found'
        })
    except Exception as e:
        logger.error(f"Unsubscribe error: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/subscribe-topic', methods=['POST'])
def subscribe_to_topic():
    """Subscribe to a topic."""
    try:
        data = request.json
        subscription_id = data.get('subscription_id')
        topic = data.get('topic')
        
        if not all([subscription_id, topic]):
            return jsonify({'error': 'Missing data'}), 400
        
        subscription_manager.subscribe_to_topic(subscription_id, topic)
        
        return jsonify({
            'status': 'subscribed_to_topic',
            'topic': topic
        })
    except Exception as e:
        logger.error(f"Topic subscription error: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/send', methods=['POST'])
def send_notification():
    """Send a notification."""
    try:
        data = request.json
        user_id = data.get('user_id')
        title = data.get('title')
        body = data.get('body')
        icon = data.get('icon')
        
        if not all([user_id, title, body, icon]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        notif_type = data.get('type', 'system_alert')
        try:
            notif_type = NotificationType[notif_type.upper()]
        except KeyError:
            notif_type = NotificationType.SYSTEM_ALERT
        
        notification = notification_engine.create_notification(
            user_id=user_id,
            notification_type=notif_type,
            title=title,
            body=body,
            icon=icon,
            data=data.get('data'),
            action_url=data.get('action_url')
        )
        
        result = notification_engine.send_notification(notification)
        
        return jsonify({
            'status': 'sent',
            'notification_id': notification.id,
            'delivery': result
        })
    except Exception as e:
        logger.error(f"Send notification error: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/user/<user_id>/notifications', methods=['GET'])
def get_user_notifications(user_id):
    """Get user notifications."""
    try:
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        notifications = notification_engine.get_user_notifications(user_id, unread_only)
        
        return jsonify({
            'user_id': user_id,
            'total': len(notifications),
            'notifications': [
                {
                    'id': n.id,
                    'type': n.notification_type.value,
                    'title': n.title,
                    'body': n.body,
                    'timestamp': n.timestamp,
                    'is_read': n.is_read,
                    'action_url': n.action_url
                }
                for n in notifications
            ]
        })
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/notification/<notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark notification as read."""
    try:
        success = notification_engine.mark_as_read(notification_id)
        
        return jsonify({
            'status': 'updated' if success else 'not_found',
            'notification_id': notification_id
        })
    except Exception as e:
        logger.error(f"Error marking notification: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/user/<user_id>/preferences', methods=['GET'])
def get_preferences(user_id):
    """Get user notification preferences."""
    try:
        prefs = notification_engine.get_user_preferences(user_id)
        
        return jsonify({
            'user_id': user_id,
            'enabled': prefs.enabled,
            'email_enabled': prefs.email_enabled,
            'push_enabled': prefs.push_enabled,
            'in_app_enabled': prefs.in_app_enabled,
            'notification_types': prefs.notification_types
        })
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/user/<user_id>/preferences', methods=['PUT'])
def update_preferences(user_id):
    """Update user notification preferences."""
    try:
        data = request.json
        prefs = notification_engine.get_user_preferences(user_id)
        
        if 'enabled' in data:
            prefs.enabled = data['enabled']
        if 'email_enabled' in data:
            prefs.email_enabled = data['email_enabled']
        if 'push_enabled' in data:
            prefs.push_enabled = data['push_enabled']
        if 'in_app_enabled' in data:
            prefs.in_app_enabled = data['in_app_enabled']
        
        return jsonify({
            'status': 'updated',
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/user/<user_id>/mute', methods=['POST'])
def mute_notifications(user_id):
    """Mute notifications for a user."""
    try:
        data = request.json
        minutes = data.get('minutes', 60)
        
        notification_engine.mute_notifications(user_id, minutes)
        
        return jsonify({
            'status': 'muted',
            'user_id': user_id,
            'duration_minutes': minutes
        })
    except Exception as e:
        logger.error(f"Error muting notifications: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/user/<user_id>/unmute', methods=['POST'])
def unmute_notifications(user_id):
    """Unmute notifications for a user."""
    try:
        notification_engine.unmute_notifications(user_id)
        
        return jsonify({
            'status': 'unmuted',
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error unmuting notifications: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get notification statistics."""
    try:
        stats = notification_engine.get_stats()
        push_stats = push_service.get_stats()
        sub_stats = subscription_manager.get_stats()
        
        return jsonify({
            'notification_engine': stats,
            'push_service': push_stats,
            'subscriptions': sub_stats
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/health', methods=['GET'])
def health():
    """Health check."""
    try:
        return jsonify({
            'status': 'healthy',
            'push_configured': push_service.is_configured,
            'subscriptions_active': subscription_manager.get_stats()['active_subscriptions']
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'error': str(e)}), 500

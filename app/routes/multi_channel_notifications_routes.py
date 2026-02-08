# app/routes/multi_channel_notifications_routes.py
"""
Multi-Channel Notifications API Routes
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from app.notifications.multi_channel import multi_channel_manager


def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


multi_notif_bp = Blueprint('multi_notifications', __name__, url_prefix='/api/v1/notifications')


@multi_notif_bp.route('/templates/create', methods=['POST'])
@require_auth
def create_template():
    """Create notification template."""
    try:
        data = request.get_json()
        
        template = multi_channel_manager.create_template(
            name=data.get('name', ''),
            subject=data.get('subject', ''),
            body=data.get('body', ''),
            html_body=data.get('html_body', ''),
            channels=data.get('channels', [])
        )
        
        return jsonify({
            'status': 'success',
            'template': template.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@multi_notif_bp.route('/templates/<template_id>', methods=['GET'])
@require_auth
def get_template(template_id):
    """Get template."""
    try:
        template = multi_channel_manager.get_template(template_id)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify({
            'status': 'success',
            'template': template.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@multi_notif_bp.route('/workflows/create', methods=['POST'])
@require_auth
def create_workflow():
    """Create notification workflow."""
    try:
        data = request.get_json()
        
        workflow = multi_channel_manager.create_workflow(
            name=data.get('name', ''),
            trigger=data.get('trigger', ''),
            template_id=data.get('template_id', ''),
            channels=data.get('channels', [])
        )
        
        return jsonify({
            'status': 'success',
            'workflow': workflow.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@multi_notif_bp.route('/workflows/<workflow_id>', methods=['GET'])
@require_auth
def get_workflow(workflow_id):
    """Get workflow."""
    try:
        workflow = multi_channel_manager.get_workflow(workflow_id)
        
        if not workflow:
            return jsonify({'error': 'Workflow not found'}), 404
        
        return jsonify({
            'status': 'success',
            'workflow': workflow.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@multi_notif_bp.route('/send', methods=['POST'])
@require_auth
def send_notification():
    """Send notification."""
    try:
        data = request.get_json()
        
        record = multi_channel_manager.queue_notification(
            user_id=data.get('user_id', ''),
            channel=data.get('channel', 'email'),
            recipient=data.get('recipient', ''),
            subject=data.get('subject', ''),
            body=data.get('body', ''),
            template_id=data.get('template_id', '')
        )
        
        multi_channel_manager.send_notification(record.id)
        
        return jsonify({
            'status': 'success',
            'notification': record.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@multi_notif_bp.route('/history', methods=['GET'])
@require_auth
def get_history():
    """Get notification history."""
    try:
        user_id = request.headers.get('X-User-ID', 'guest')
        history = multi_channel_manager.get_notification_history(user_id)
        
        return jsonify({
            'status': 'success',
            'history': history,
            'total': len(history)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@multi_notif_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    """Get delivery statistics."""
    try:
        stats = multi_channel_manager.get_delivery_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@multi_notif_bp.route('/channels/<channel>/test', methods=['POST'])
@require_auth
def test_channel(channel):
    """Test notification channel."""
    try:
        data = request.get_json()
        result = multi_channel_manager.test_channel(channel, data.get('recipient', ''))
        
        return jsonify({
            'status': 'success',
            'result': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# app/routes/mobile_routes.py
"""
Mobile Native App API Routes
iOS and Android device management and offline sync endpoints.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from app.mobile.native_app import mobile_manager


def require_auth(f):
    """Require authentication for mobile endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in request.headers.get('Authorization', ''):
            if 'user_id' not in getattr(request, 'user', {}):
                # For development, allow any request with user_id header
                request.user_id = request.headers.get('X-User-ID', 'guest')
            else:
                request.user_id = request.user.get('id', 'guest')
        else:
            request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


mobile_bp = Blueprint('mobile', __name__, url_prefix='/api/v1/mobile')


@mobile_bp.route('/devices/register', methods=['POST'])
@require_auth
def register_mobile_device():
    """Register a mobile device for push notifications and offline sync."""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        device = mobile_manager.register_device(
            user_id=user_id,
            platform=data.get('platform', 'android'),
            app_version=data.get('app_version', '1.0.0'),
            os_version=data.get('os_version', ''),
            device_name=data.get('device_name', ''),
            push_token=data.get('push_token', '')
        )
        
        return jsonify({
            'status': 'success',
            'device': device.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/devices', methods=['GET'])
@require_auth
def get_user_devices():
    """Get all registered devices for current user."""
    try:
        user_id = request.user_id
        devices = mobile_manager.get_user_devices(user_id)
        
        return jsonify({
            'status': 'success',
            'devices': devices,
            'total': len(devices)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/devices/<device_id>', methods=['GET'])
@require_auth
def get_device(device_id):
    """Get device details."""
    try:
        if device_id not in mobile_manager.devices:
            return jsonify({'error': 'Device not found'}), 404
        
        device = mobile_manager.devices[device_id]
        return jsonify({
            'status': 'success',
            'device': device.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/devices/<device_id>/unregister', methods=['POST'])
@require_auth
def unregister_device(device_id):
    """Unregister a mobile device."""
    try:
        if device_id not in mobile_manager.devices:
            return jsonify({'error': 'Device not found'}), 404
        
        device = mobile_manager.devices[device_id]
        device.is_active = False
        mobile_manager.stats['active_devices'] = max(0, mobile_manager.stats['active_devices'] - 1)
        
        return jsonify({
            'status': 'success',
            'message': 'Device unregistered'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/sync/create', methods=['POST'])
@require_auth
def create_sync_job():
    """Create a new sync job for device."""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        sync_type = data.get('sync_type', 'bidirectional')
        records_count = data.get('records_count', 0)
        
        if device_id not in mobile_manager.devices:
            return jsonify({'error': 'Device not found'}), 404
        
        sync_job = mobile_manager.create_sync_job(
            device_id=device_id,
            sync_type=sync_type,
            records_count=records_count
        )
        
        return jsonify({
            'status': 'success',
            'sync_job': sync_job.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/sync/<sync_id>/progress', methods=['PUT'])
@require_auth
def update_sync_progress(sync_id):
    """Update synchronization progress."""
    try:
        if sync_id not in mobile_manager.sync_jobs:
            return jsonify({'error': 'Sync job not found'}), 404
        
        data = request.get_json()
        synced_count = data.get('synced_count', 0)
        failed_count = data.get('failed_count', 0)
        
        mobile_manager.update_sync_progress(sync_id, synced_count, failed_count)
        sync_job = mobile_manager.sync_jobs[sync_id]
        
        return jsonify({
            'status': 'success',
            'sync_job': sync_job.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/sync/<sync_id>', methods=['GET'])
@require_auth
def get_sync_job(sync_id):
    """Get synchronization job status."""
    try:
        if sync_id not in mobile_manager.sync_jobs:
            return jsonify({'error': 'Sync job not found'}), 404
        
        sync_job = mobile_manager.sync_jobs[sync_id]
        return jsonify({
            'status': 'success',
            'sync_job': sync_job.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/offline-data/cache', methods=['POST'])
@require_auth
def cache_offline_data():
    """Cache data for offline access."""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        entity_type = data.get('entity_type')
        entity_id = data.get('entity_id')
        entity_data = data.get('data', {})
        
        if device_id not in mobile_manager.devices:
            return jsonify({'error': 'Device not found'}), 404
        
        cached = mobile_manager.cache_offline_data(
            device_id=device_id,
            entity_type=entity_type,
            entity_id=entity_id,
            data=entity_data
        )
        
        return jsonify({
            'status': 'success',
            'cached_data': cached.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/offline-data', methods=['GET'])
@require_auth
def get_offline_data():
    """Get offline cached data."""
    try:
        device_id = request.args.get('device_id')
        entity_type = request.args.get('entity_type')
        
        if device_id not in mobile_manager.devices:
            return jsonify({'error': 'Device not found'}), 404
        
        data = mobile_manager.get_offline_data(device_id, entity_type)
        
        return jsonify({
            'status': 'success',
            'offline_data': data,
            'total': len(data)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/offline-data/mark-synced', methods=['POST'])
@require_auth
def mark_offline_data_synced():
    """Mark offline data as synced."""
    try:
        data = request.get_json()
        data_ids = data.get('data_ids', [])
        
        count = mobile_manager.mark_offline_data_synced(data_ids)
        
        return jsonify({
            'status': 'success',
            'synced_count': count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/app-update/check', methods=['POST'])
@require_auth
def check_app_update():
    """Check if app update is available."""
    try:
        data = request.get_json()
        platform = data.get('platform', 'android')
        current_version = data.get('current_version', '1.0.0')
        
        update_info = mobile_manager.check_app_update(platform, current_version)
        
        return jsonify({
            'status': 'success',
            'update_info': update_info
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/devices/<device_id>/analytics', methods=['GET'])
@require_auth
def get_device_analytics(device_id):
    """Get analytics for mobile device."""
    try:
        analytics = mobile_manager.get_device_analytics(device_id)
        
        return jsonify({
            'status': 'success',
            'analytics': analytics
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mobile_bp.route('/stats', methods=['GET'])
def get_mobile_stats():
    """Get mobile app statistics."""
    try:
        stats = mobile_manager.get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

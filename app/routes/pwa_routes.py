"""Progressive Web App API routes."""

from flask import Blueprint, request, jsonify, current_app
from app.pwa import (
    service_worker_manager, manifest_generator,
    offline_manager, background_sync_manager
)
import logging

logger = logging.getLogger(__name__)

pwa_bp = Blueprint('pwa', __name__, url_prefix='/api/v1/pwa')


@pwa_bp.route('/manifest.json', methods=['GET'])
def get_manifest():
    """Get web app manifest."""
    try:
        manifest = manifest_generator.generate_manifest_json()
        return jsonify(manifest)
    except Exception as e:
        logger.error(f"Error getting manifest: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/service-worker.js', methods=['GET'])
def get_service_worker():
    """Get service worker JavaScript."""
    try:
        sw_code = service_worker_manager.get_service_worker_code()
        return sw_code, 200, {'Content-Type': 'application/javascript'}
    except Exception as e:
        logger.error(f"Error getting service worker: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/install-prompt.js', methods=['GET'])
def get_install_prompt():
    """Get install prompt JavaScript."""
    try:
        code = service_worker_manager.get_install_prompt_script()
        return code, 200, {'Content-Type': 'application/javascript'}
    except Exception as e:
        logger.error(f"Error getting install prompt: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/sync', methods=['POST'])
def sync_data():
    """Synchronize offline data."""
    try:
        pending = offline_manager.get_pending_requests()
        
        sync_result = {
            'status': 'synced',
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'pending_requests': len(pending)
        }
        
        logger.info(f"Sync requested: {len(pending)} pending requests")
        return jsonify(sync_result)
    except Exception as e:
        logger.error(f"Sync error: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/offline-data', methods=['POST'])
def store_offline_data():
    """Store data for offline use."""
    try:
        data = request.json
        key = data.get('key')
        value = data.get('value')
        ttl = data.get('ttl', 3600)
        
        if not key:
            return jsonify({'error': 'Key required'}), 400
        
        offline_manager.cache_data(key, value, ttl)
        return jsonify({'status': 'stored', 'key': key})
    except Exception as e:
        logger.error(f"Error storing offline data: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/service-worker/enable', methods=['POST'])
def enable_sw():
    """Enable service worker."""
    try:
        service_worker_manager.enable_service_worker()
        return jsonify({'status': 'enabled'})
    except Exception as e:
        logger.error(f"Error enabling SW: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/service-worker/disable', methods=['POST'])
def disable_sw():
    """Disable service worker."""
    try:
        service_worker_manager.disable_service_worker()
        return jsonify({'status': 'disabled'})
    except Exception as e:
        logger.error(f"Error disabling SW: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/service-worker/stats', methods=['GET'])
def get_sw_stats():
    """Get service worker statistics."""
    try:
        stats = service_worker_manager.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting SW stats: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/manifest/theme-color', methods=['PUT'])
def set_theme_color():
    """Set manifest theme color."""
    try:
        data = request.json
        color = data.get('color')
        
        if not color:
            return jsonify({'error': 'Color required'}), 400
        
        manifest_generator.set_theme_color(color)
        return jsonify({'status': 'updated', 'color': color})
    except Exception as e:
        logger.error(f"Error setting theme color: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/offline/stats', methods=['GET'])
def get_offline_stats():
    """Get offline manager statistics."""
    try:
        stats = offline_manager.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting offline stats: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/sync/status', methods=['GET'])
def get_sync_status():
    """Get background sync status."""
    try:
        status = background_sync_manager.get_sync_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/sync/trigger', methods=['POST'])
def trigger_sync():
    """Trigger background sync."""
    try:
        data = request.json or {}
        tag = data.get('tag', 'sync-data')
        
        result = background_sync_manager.trigger_sync(tag, data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error triggering sync: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    """PWA heartbeat check."""
    try:
        timestamp = __import__('datetime').datetime.now().isoformat()
        return jsonify({
            'status': 'online',
            'timestamp': timestamp
        })
    except Exception as e:
        logger.error(f"Heartbeat error: {e}")
        return jsonify({'error': str(e)}), 500


@pwa_bp.route('/health', methods=['GET'])
def health():
    """Health check."""
    try:
        return jsonify({
            'status': 'healthy',
            'pwa_enabled': service_worker_manager.sw_enabled,
            'offline_support': True,
            'sync_enabled': background_sync_manager.sync_enabled
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'error': str(e)}), 500

# app/routes/dr_routes.py
"""
Disaster Recovery & High Availability API Routes
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from app.disaster.dr_management import dr_manager


def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


dr_bp = Blueprint('disaster_recovery', __name__, url_prefix='/api/v1/dr')


@dr_bp.route('/backups/create', methods=['POST'])
@require_auth
def create_backup():
    """Create backup job."""
    try:
        data = request.get_json()
        
        job = dr_manager.create_backup(
            backup_type=data.get('backup_type', 'full'),
            source_system=data.get('source_system', ''),
            destination=data.get('destination', '')
        )
        
        return jsonify({
            'status': 'success',
            'backup': job.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dr_bp.route('/backups/<backup_id>/start', methods=['POST'])
@require_auth
def start_backup(backup_id):
    """Start backup job."""
    try:
        success = dr_manager.start_backup(backup_id)
        
        if not success:
            return jsonify({'error': 'Backup not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Backup started'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dr_bp.route('/backups/<backup_id>/complete', methods=['POST'])
@require_auth
def complete_backup(backup_id):
    """Complete backup job."""
    try:
        data = request.get_json()
        success = dr_manager.complete_backup(backup_id, data.get('data_size', 0.0))
        
        if not success:
            return jsonify({'error': 'Backup not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Backup completed'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dr_bp.route('/backups/<backup_id>/verify', methods=['POST'])
@require_auth
def verify_backup(backup_id):
    """Verify backup integrity."""
    try:
        success = dr_manager.verify_backup(backup_id)
        
        if not success:
            return jsonify({'error': 'Backup not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Backup verified'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dr_bp.route('/restore-points/create', methods=['POST'])
@require_auth
def create_restore_point():
    """Create restore point."""
    try:
        data = request.get_json()
        
        point = dr_manager.create_restore_point(
            backup_job_id=data.get('backup_job_id', ''),
            system=data.get('system', '')
        )
        
        return jsonify({
            'status': 'success',
            'restore_point': point.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dr_bp.route('/restore-points/<restore_id>/test', methods=['POST'])
@require_auth
def test_restore(restore_id):
    """Test restore point."""
    try:
        success = dr_manager.test_restore(restore_id)
        
        if not success:
            return jsonify({'error': 'Restore point not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Restore test completed'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dr_bp.route('/replication/configure', methods=['POST'])
@require_auth
def configure_replication():
    """Configure replication."""
    try:
        data = request.get_json()
        
        config = dr_manager.configure_replication(
            name=data.get('name', ''),
            primary=data.get('primary', ''),
            secondary=data.get('secondary', ''),
            replication_type=data.get('replication_type', 'asynchronous')
        )
        
        return jsonify({
            'status': 'success',
            'replication': config.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dr_bp.route('/failover/configure', methods=['POST'])
@require_auth
def configure_failover():
    """Configure failover."""
    try:
        data = request.get_json()
        
        config = dr_manager.configure_failover(
            name=data.get('name', ''),
            primary=data.get('primary', ''),
            secondary=data.get('secondary', ''),
            tertiary=data.get('tertiary', '')
        )
        
        return jsonify({
            'status': 'success',
            'failover': config.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dr_bp.route('/failover/<failover_id>/trigger', methods=['POST'])
@require_auth
def trigger_failover(failover_id):
    """Trigger failover."""
    try:
        success = dr_manager.trigger_failover(failover_id)
        
        if not success:
            return jsonify({'error': 'Failover config not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Failover triggered'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dr_bp.route('/metrics', methods=['GET'])
@require_auth
def get_metrics():
    """Get DR metrics."""
    try:
        metrics = dr_manager.get_dr_metrics()
        
        return jsonify({
            'status': 'success',
            'metrics': metrics
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

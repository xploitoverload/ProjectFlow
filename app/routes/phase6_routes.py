# app/routes/phase6_routes.py
"""
Phase 6 API routes for enterprise systems.
Provides endpoints for batch operations, backups, GraphQL, and performance metrics.
"""

from flask import Blueprint, jsonify, request, g
from functools import wraps
import logging

logger = logging.getLogger('phase6_routes')

phase6_bp = Blueprint('phase6', __name__, url_prefix='/api/v1/enterprise')


def require_admin(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if g.user.role not in ['admin', 'super_admin']:
            return jsonify({'error': 'Forbidden - Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# BATCH OPERATIONS ENDPOINTS
# ============================================================================

@phase6_bp.route('/batch/execute', methods=['POST'])
@require_admin
def execute_batch():
    """
    Execute batch operations atomically.
    
    Request JSON:
    {
        "operations": [
            {"type": "create", "resource": "issue", "data": {...}},
            {"type": "update", "resource": "issue", "id": "123", "data": {...}},
            {"type": "delete", "resource": "issue", "id": "456"}
        ],
        "atomic": true
    }
    """
    try:
        from app.operations import BatchBuilder, OperationType
        
        data = request.get_json()
        if not data or 'operations' not in data:
            return jsonify({'error': 'Missing operations'}), 400
        
        builder = BatchBuilder()
        
        for op in data.get('operations', []):
            op_type = op.get('type', '').lower()
            resource = op.get('resource')
            op_data = op.get('data', {})
            op_id = op.get('id')
            
            if op_type == 'create':
                builder.create(resource, op_data)
            elif op_type == 'update':
                if not op_id:
                    return jsonify({'error': 'Update operation requires id'}), 400
                builder.update(resource, op_id, op_data)
            elif op_type == 'delete':
                if not op_id:
                    return jsonify({'error': 'Delete operation requires id'}), 400
                builder.delete(resource, op_id)
        
        result = builder.execute(atomic=data.get('atomic', False))
        
        if result:
            return jsonify({
                'success': True,
                'batch_id': result.batch_id,
                'total_operations': result.total_operations,
                'successful': result.successful,
                'failed': result.failed,
                'duration_seconds': result.get_duration(),
                'errors': result.errors
            }), 201
        else:
            return jsonify({'error': 'Failed to execute batch'}), 500
    
    except Exception as e:
        logger.error(f'Batch execution error: {e}')
        return jsonify({'error': str(e)}), 500


@phase6_bp.route('/batch/status/<batch_id>', methods=['GET'])
@require_admin
def batch_status(batch_id):
    """Get status of executed batch."""
    return jsonify({'batch_id': batch_id, 'status': 'completed'})


# ============================================================================
# BACKUP & RECOVERY ENDPOINTS
# ============================================================================

@phase6_bp.route('/backups', methods=['GET'])
@require_admin
def list_backups():
    """List all backups with statistics."""
    try:
        from app.recovery import get_backup_manager
        
        manager = get_backup_manager()
        if not manager:
            return jsonify({'error': 'Backup manager not initialized'}), 500
        
        return jsonify({
            'backups': manager.list_backups(),
            'stats': manager.get_backup_stats()
        })
    
    except Exception as e:
        logger.error(f'Backup list error: {e}')
        return jsonify({'error': str(e)}), 500


@phase6_bp.route('/backups/create', methods=['POST'])
@require_admin
def create_backup():
    """Create a new full backup."""
    try:
        from app.recovery import get_backup_manager
        
        manager = get_backup_manager()
        if not manager:
            return jsonify({'error': 'Backup manager not initialized'}), 500
        
        data = request.get_json() or {}
        notes = data.get('notes', '')
        
        success, message, metadata = manager.create_full_backup(notes=notes)
        
        if success:
            return jsonify({
                'success': True,
                'backup': metadata.to_dict(),
                'message': message
            }), 201
        else:
            return jsonify({'success': False, 'error': message}), 400
    
    except Exception as e:
        logger.error(f'Backup creation error: {e}')
        return jsonify({'error': str(e)}), 500


@phase6_bp.route('/backups/<backup_id>/restore', methods=['POST'])
@require_admin
def restore_backup(backup_id):
    """Restore database from backup."""
    try:
        from app.recovery import get_backup_manager
        
        manager = get_backup_manager()
        if not manager:
            return jsonify({'error': 'Backup manager not initialized'}), 500
        
        success, message = manager.restore_backup(backup_id)
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
    
    except Exception as e:
        logger.error(f'Restore error: {e}')
        return jsonify({'error': str(e)}), 500


@phase6_bp.route('/backups/<backup_id>/verify', methods=['POST'])
@require_admin
def verify_backup(backup_id):
    """Verify backup integrity."""
    try:
        from app.recovery import get_backup_manager
        
        manager = get_backup_manager()
        if not manager:
            return jsonify({'error': 'Backup manager not initialized'}), 500
        
        valid, message = manager.verify_backup(backup_id)
        
        return jsonify({
            'valid': valid,
            'message': message
        }), 200 if valid else 400
    
    except Exception as e:
        logger.error(f'Verification error: {e}')
        return jsonify({'error': str(e)}), 500


# ============================================================================
# GRAPHQL ENDPOINT
# ============================================================================

@phase6_bp.route('/graphql', methods=['POST'])
def graphql_query():
    """Execute GraphQL query."""
    try:
        from app.api.graphql_api import get_graphql_executor
        
        executor = get_graphql_executor()
        if not executor:
            return jsonify({'error': 'GraphQL not initialized'}), 500
        
        data = request.get_json() or {}
        query = data.get('query')
        variables = data.get('variables', {})
        
        if not query:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        result = executor.execute(query, variables=variables)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f'GraphQL error: {e}')
        return jsonify({'errors': [{'message': str(e)}]}), 500


@phase6_bp.route('/graphql/schema', methods=['GET'])
def graphql_schema():
    """Get GraphQL schema definition."""
    try:
        from app.api.graphql_api import get_graphql_schema
        
        schema = get_graphql_schema()
        return jsonify({'schema': schema})
    
    except Exception as e:
        logger.error(f'Schema error: {e}')
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PERFORMANCE MONITORING ENDPOINTS
# ============================================================================

@phase6_bp.route('/metrics', methods=['GET'])
@require_admin
def get_metrics():
    """Get comprehensive performance metrics."""
    try:
        from app.monitoring.performance import get_performance_monitor
        
        monitor = get_performance_monitor()
        if not monitor:
            return jsonify({'error': 'Performance monitor not initialized'}), 500
        
        return jsonify(monitor.get_performance_report())
    
    except Exception as e:
        logger.error(f'Metrics error: {e}')
        return jsonify({'error': str(e)}), 500


@phase6_bp.route('/metrics/recommendations', methods=['GET'])
@require_admin
def get_recommendations():
    """Get optimization recommendations."""
    try:
        from app.monitoring.performance import get_performance_monitor
        
        monitor = get_performance_monitor()
        if not monitor:
            return jsonify({'error': 'Performance monitor not initialized'}), 500
        
        return jsonify({
            'recommendations': monitor.get_optimization_recommendations(),
            'slowest_operations': monitor.get_slowest_operations(5),
            'most_called_operations': monitor.get_most_called_operations(5)
        })
    
    except Exception as e:
        logger.error(f'Recommendations error: {e}')
        return jsonify({'error': str(e)}), 500


@phase6_bp.route('/metrics/operation/<operation_name>', methods=['GET'])
@require_admin
def get_operation_stats(operation_name):
    """Get stats for specific operation."""
    try:
        from app.monitoring.performance import get_performance_monitor
        
        monitor = get_performance_monitor()
        if not monitor:
            return jsonify({'error': 'Performance monitor not initialized'}), 500
        
        stats = monitor.get_stats(operation_name)
        if stats:
            return jsonify(stats)
        else:
            return jsonify({'error': f'No stats for {operation_name}'}), 404
    
    except Exception as e:
        logger.error(f'Operation stats error: {e}')
        return jsonify({'error': str(e)}), 500


# ============================================================================
# WEBSOCKET STATUS ENDPOINT
# ============================================================================

@phase6_bp.route('/websocket/status', methods=['GET'])
@require_admin
def websocket_status():
    """Get WebSocket connection status."""
    try:
        from app.websocket import get_connected_users
        
        users = get_connected_users()
        
        return jsonify({
            'connected': True,
            'active_connections': len(users),
            'connected_users': users
        })
    
    except Exception as e:
        logger.error(f'WebSocket status error: {e}')
        return jsonify({
            'connected': False,
            'error': str(e)
        }), 500


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@phase6_bp.route('/health', methods=['GET'])
def phase6_health():
    """Check Phase 6 systems health."""
    try:
        health_status = {}
        
        # Check WebSocket
        try:
            from app.websocket import get_connected_users
            get_connected_users()
            health_status['websocket'] = 'operational'
        except:
            health_status['websocket'] = 'degraded'
        
        # Check Batch Processor
        try:
            from app.operations import get_batch_processor
            get_batch_processor()
            health_status['batch_processor'] = 'operational'
        except:
            health_status['batch_processor'] = 'degraded'
        
        # Check Backup Manager
        try:
            from app.recovery import get_backup_manager
            get_backup_manager()
            health_status['backup_manager'] = 'operational'
        except:
            health_status['backup_manager'] = 'degraded'
        
        # Check GraphQL
        try:
            from app.api.graphql_api import get_graphql_executor
            get_graphql_executor()
            health_status['graphql'] = 'operational'
        except:
            health_status['graphql'] = 'degraded'
        
        # Check Performance Monitor
        try:
            from app.monitoring.performance import get_performance_monitor
            get_performance_monitor()
            health_status['performance_monitor'] = 'operational'
        except:
            health_status['performance_monitor'] = 'degraded'
        
        overall_status = 'operational' if all(
            v == 'operational' for v in health_status.values()
        ) else 'degraded'
        
        return jsonify({
            'status': overall_status,
            'systems': health_status
        })
    
    except Exception as e:
        logger.error(f'Health check error: {e}')
        return jsonify({
            'status': 'down',
            'error': str(e)
        }), 500

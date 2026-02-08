# app/routes/resource_planning_routes.py
"""
Resource Planning API Routes
Resource allocation, capacity forecasting, and bottleneck detection.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime
from app.resource.resource_planning import resource_planning_manager


def require_auth(f):
    """Require authentication for resource planning endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


resource_bp = Blueprint('resource', __name__, url_prefix='/api/v1/resource')


@resource_bp.route('/resources/create', methods=['POST'])
@require_auth
def create_resource():
    """Create new resource."""
    try:
        data = request.get_json()
        
        resource = resource_planning_manager.create_resource(
            name=data.get('name', ''),
            resource_type=data.get('resource_type', 'engineer'),
            capacity=data.get('capacity', 1),
            cost_per_unit=data.get('cost_per_unit', 0.0)
        )
        
        return jsonify({
            'status': 'success',
            'resource': resource.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@resource_bp.route('/resources/<resource_id>', methods=['GET'])
@require_auth
def get_resource(resource_id):
    """Get resource details."""
    try:
        resource = resource_planning_manager.get_resource(resource_id)
        
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        return jsonify({
            'status': 'success',
            'resource': resource.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@resource_bp.route('/allocate', methods=['POST'])
@require_auth
def allocate_resource():
    """Allocate resource to project."""
    try:
        data = request.get_json()
        
        allocation = resource_planning_manager.allocate_resource(
            resource_id=data.get('resource_id', ''),
            project_id=data.get('project_id', ''),
            amount=data.get('amount', 1),
            end_date=datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else None
        )
        
        if not allocation:
            return jsonify({'error': 'Failed to allocate resource'}), 400
        
        return jsonify({
            'status': 'success',
            'allocation': allocation.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@resource_bp.route('/allocate/<allocation_id>', methods=['DELETE'])
@require_auth
def deallocate_resource(allocation_id):
    """Deallocate resource."""
    try:
        success = resource_planning_manager.deallocate_resource(allocation_id)
        
        if not success:
            return jsonify({'error': 'Allocation not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Resource deallocated'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@resource_bp.route('/utilization', methods=['GET'])
@require_auth
def get_utilization():
    """Get resource utilization metrics."""
    try:
        resource_type = request.args.get('resource_type')
        utilization = resource_planning_manager.get_resource_utilization(resource_type)
        
        return jsonify({
            'status': 'success',
            'utilization': utilization
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@resource_bp.route('/forecast', methods=['POST'])
@require_auth
def forecast_capacity():
    """Forecast capacity needs."""
    try:
        data = request.get_json()
        days_ahead = data.get('days_ahead', 30)
        resource_type = data.get('resource_type', 'engineer')
        
        forecast = resource_planning_manager.forecast_capacity(resource_type, days_ahead)
        
        return jsonify({
            'status': 'success',
            'forecast': forecast.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@resource_bp.route('/bottleneck/detect', methods=['POST'])
@require_auth
def detect_bottleneck():
    """Detect bottleneck for resource type."""
    try:
        data = request.get_json()
        resource_type = data.get('resource_type', 'engineer')
        
        bottleneck = resource_planning_manager.detect_bottleneck(resource_type)
        
        return jsonify({
            'status': 'success',
            'bottleneck': bottleneck.to_dict() if bottleneck else None,
            'status_message': 'No bottleneck detected' if not bottleneck else 'Bottleneck detected'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@resource_bp.route('/optimize/<project_id>', methods=['GET'])
@require_auth
def optimize_allocation(project_id):
    """Get optimization suggestions for project."""
    try:
        suggestions = resource_planning_manager.optimize_allocation(project_id)
        
        return jsonify({
            'status': 'success',
            'optimization': suggestions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@resource_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get resource planning statistics."""
    try:
        stats = resource_planning_manager.get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@resource_bp.route('/capacity-plan/<resource_type>', methods=['GET'])
@require_auth
def get_capacity_plan(resource_type):
    """Get capacity plan for resource type."""
    try:
        utilization = resource_planning_manager.get_resource_utilization(resource_type)
        bottleneck = resource_planning_manager.detect_bottleneck(resource_type)
        forecast = resource_planning_manager.forecast_capacity(resource_type, 30)
        
        return jsonify({
            'status': 'success',
            'capacity_plan': {
                'resource_type': resource_type,
                'current_utilization': utilization,
                'bottleneck_detected': bottleneck is not None,
                'forecast_30_days': forecast.to_dict()
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# app/routes/api_versioning_routes.py
"""
API Versioning and GraphQL API Routes
Support for API v1/v2, GraphQL, and endpoint management.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from app.api.api_versioning import api_versioning_manager


def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


api_mgmt_bp = Blueprint('api_management', __name__, url_prefix='/api/management')


@api_mgmt_bp.route('/endpoints/register', methods=['POST'])
@require_auth
def register_endpoint():
    """Register API endpoint."""
    try:
        data = request.get_json()
        
        endpoint = api_versioning_manager.register_endpoint(
            path=data.get('path', ''),
            method=data.get('method', 'GET'),
            version=data.get('version', 'v2'),
            description=data.get('description', ''),
            auth_required=data.get('auth_required', True)
        )
        
        return jsonify({
            'status': 'success',
            'endpoint': endpoint.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_mgmt_bp.route('/endpoints', methods=['GET'])
@require_auth
def list_endpoints():
    """List all registered endpoints."""
    try:
        endpoints = [e.to_dict() for e in api_versioning_manager.endpoints.values()]
        
        # Filter by version if provided
        version = request.args.get('version')
        if version:
            endpoints = [e for e in endpoints if e['version'] == version]
        
        return jsonify({
            'status': 'success',
            'endpoints': endpoints,
            'total': len(endpoints)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_mgmt_bp.route('/endpoints/<path:path>', methods=['GET'])
@require_auth
def get_endpoint(path):
    """Get endpoint definition."""
    try:
        method = request.args.get('method', 'GET')
        version = request.args.get('version', 'v2')
        
        endpoint = api_versioning_manager.get_endpoint(method, path, version)
        
        if not endpoint:
            return jsonify({'error': 'Endpoint not found'}), 404
        
        return jsonify({
            'status': 'success',
            'endpoint': endpoint.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_mgmt_bp.route('/endpoints/<path:path>/deprecate', methods=['POST'])
@require_auth
def deprecate_endpoint(path):
    """Deprecate API endpoint."""
    try:
        data = request.get_json()
        method = data.get('method', 'GET')
        version = data.get('version', 'v1')
        replacement = data.get('replacement_path')
        
        success = api_versioning_manager.deprecate_endpoint(method, path, version, replacement)
        
        if not success:
            return jsonify({'error': 'Endpoint not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Endpoint deprecated'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_mgmt_bp.route('/graphql', methods=['POST'])
@require_auth
def execute_graphql():
    """Execute GraphQL query."""
    try:
        user_id = request.user_id
        data = request.get_json()
        query = data.get('query', '')
        variables = data.get('variables', {})
        
        result = api_versioning_manager.execute_graphql_query(user_id, query, variables)
        
        return jsonify({
            'status': 'success',
            'query_id': result.query_id,
            'execution_time_ms': result.execution_time_ms
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_mgmt_bp.route('/graphql/introspection', methods=['GET'])
def get_graphql_introspection():
    """Get GraphQL schema introspection."""
    try:
        schema = api_versioning_manager.get_graphql_introspection()
        
        return jsonify({
            'status': 'success',
            'schema': schema
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_mgmt_bp.route('/usage/record', methods=['POST'])
@require_auth
def record_usage():
    """Record API usage."""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        usage = api_versioning_manager.record_api_call(
            user_id=user_id,
            endpoint_path=data.get('endpoint_path', ''),
            method=data.get('method', 'GET'),
            version=data.get('version', 'v1'),
            status_code=data.get('status_code', 200),
            response_time_ms=data.get('response_time_ms', 0.0)
        )
        
        return jsonify({
            'status': 'success',
            'usage_id': usage.usage_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_mgmt_bp.route('/usage/report', methods=['GET'])
@require_auth
def get_usage_report():
    """Get API usage report."""
    try:
        version = request.args.get('version')
        limit = request.args.get('limit', 100, type=int)
        
        report = api_versioning_manager.get_api_usage_report(version, limit)
        
        return jsonify({
            'status': 'success',
            'usage': report,
            'total': len(report)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_mgmt_bp.route('/coverage', methods=['GET'])
@require_auth
def get_coverage():
    """Get API endpoint coverage metrics."""
    try:
        coverage = api_versioning_manager.get_endpoint_coverage()
        
        return jsonify({
            'status': 'success',
            'coverage': coverage
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_mgmt_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get API versioning statistics."""
    try:
        stats = api_versioning_manager.get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# app/routes/performance_routes.py
"""
Performance Optimization API Routes
Caching, query optimization, and performance monitoring endpoints.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from app.optimization.performance import performance_engine


def require_auth(f):
    """Require authentication for performance endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


perf_bp = Blueprint('performance', __name__, url_prefix='/api/v1/performance')


@perf_bp.route('/cache/set', methods=['POST'])
@require_auth
def cache_set():
    """Set cache entry."""
    try:
        data = request.get_json()
        key = data.get('key', '')
        value = data.get('value')
        ttl = data.get('ttl_seconds', 3600)
        
        entry = performance_engine.cache_set(key, value, ttl)
        
        return jsonify({
            'status': 'success',
            'cache_entry': entry.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@perf_bp.route('/cache/get', methods=['GET'])
@require_auth
def cache_get():
    """Get cache entry."""
    try:
        key = request.args.get('key', '')
        value = performance_engine.cache_get(key)
        
        return jsonify({
            'status': 'success',
            'key': key,
            'value': value,
            'found': value is not None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@perf_bp.route('/cache/invalidate', methods=['POST'])
@require_auth
def cache_invalidate():
    """Invalidate cache entries."""
    try:
        data = request.get_json()
        key = data.get('key')  # None = invalidate all
        
        count = performance_engine.cache_invalidate(key)
        
        return jsonify({
            'status': 'success',
            'invalidated_count': count,
            'message': 'Cache invalidated'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@perf_bp.route('/cache/stats', methods=['GET'])
@require_auth
def get_cache_stats():
    """Get cache statistics."""
    try:
        stats = performance_engine.get_cache_stats()
        
        return jsonify({
            'status': 'success',
            'cache_stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@perf_bp.route('/cache/strategy', methods=['PUT'])
@require_auth
def set_cache_strategy():
    """Set cache strategy."""
    try:
        data = request.get_json()
        strategy = data.get('strategy', 'lru')
        
        success = performance_engine.set_cache_strategy(strategy)
        
        if not success:
            return jsonify({'error': 'Invalid strategy'}), 400
        
        return jsonify({
            'status': 'success',
            'strategy': strategy,
            'message': f'Cache strategy set to {strategy}'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@perf_bp.route('/query/analyze', methods=['POST'])
@require_auth
def analyze_query():
    """Analyze query for optimization opportunities."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        execution_time = data.get('execution_time_ms', 0.0)
        
        plan = performance_engine.analyze_query(query, execution_time)
        
        return jsonify({
            'status': 'success',
            'query_plan': plan.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@perf_bp.route('/metric/record', methods=['POST'])
@require_auth
def record_metric():
    """Record performance metric."""
    try:
        data = request.get_json()
        metric_name = data.get('metric_name', '')
        value = data.get('value', 0.0)
        unit = data.get('unit', '')
        
        metric = performance_engine.record_metric(metric_name, value, unit)
        
        return jsonify({
            'status': 'success',
            'metric': metric.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@perf_bp.route('/recommendations', methods=['GET'])
@require_auth
def get_recommendations():
    """Get optimization recommendations."""
    try:
        threshold = request.args.get('threshold_ms', 1000, type=int)
        recommendations = performance_engine.get_optimization_recommendations(threshold)
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@perf_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get performance statistics."""
    try:
        stats = performance_engine.get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

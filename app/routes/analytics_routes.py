"""Advanced Analytics Routes - Dashboard and analytics endpoints"""

from flask import Blueprint, request, jsonify, render_template, current_app
from functools import wraps
from datetime import datetime, timedelta
import logging

from app.analytics.dashboard import analytics_dashboard

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/v1/analytics')


def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# Dashboard Endpoints
# ============================================================================

@analytics_bp.route('/dashboard/<project_id>', methods=['GET'])
@require_auth
def get_project_dashboard(project_id):
    """Get analytics dashboard for a project"""
    try:
        # In real implementation, fetch from database
        project = {
            'id': project_id,
            'name': f'Project {project_id}',
            'issues': [],  # Would come from database
            'estimated_completion': (datetime.now() + timedelta(days=30)).isoformat(),
        }
        
        team_members = []  # Would come from database
        
        dashboard = analytics_dashboard.generate_dashboard(project, team_members)
        
        return jsonify({
            'status': 'success',
            'dashboard': dashboard,
        }), 200
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/summary/<project_id>', methods=['GET'])
@require_auth
def get_executive_summary(project_id):
    """Get executive summary"""
    try:
        # In real implementation, fetch from database
        project = {
            'id': project_id,
            'name': f'Project {project_id}',
            'issues': [],
        }
        
        summary = analytics_dashboard.generate_executive_summary(project)
        
        return jsonify({
            'status': 'success',
            'summary': summary,
        }), 200
    except Exception as e:
        logger.error(f"Summary error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Project Metrics Endpoints
# ============================================================================

@analytics_bp.route('/metrics/project/<project_id>', methods=['GET'])
@require_auth
def get_project_metrics(project_id):
    """Get all project metrics"""
    try:
        # In real implementation, fetch from database
        project = {
            'id': project_id,
            'name': f'Project {project_id}',
            'issues': [],
        }
        
        health_metrics = analytics_dashboard.project_analytics.calculate_project_health(project)
        
        metrics = {}
        for name, metric in health_metrics.items():
            metrics[name] = metric.to_dict()
        
        return jsonify({
            'status': 'success',
            'metrics': metrics,
        }), 200
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/metrics/team/<project_id>', methods=['GET'])
@require_auth
def get_team_metrics(project_id):
    """Get team productivity metrics"""
    try:
        # In real implementation, fetch from database
        team_members = []
        issues = []
        
        metrics = analytics_dashboard.project_analytics.calculate_team_productivity(
            team_members, issues
        )
        
        result = {}
        for name, metric in metrics.items():
            result[name] = metric.to_dict()
        
        return jsonify({
            'status': 'success',
            'metrics': result,
        }), 200
    except Exception as e:
        logger.error(f"Team metrics error: {e}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/metrics/issues/<project_id>', methods=['GET'])
@require_auth
def get_issue_metrics(project_id):
    """Get issue resolution metrics"""
    try:
        # In real implementation, fetch from database
        issues = []
        
        metrics = analytics_dashboard.project_analytics.calculate_issue_resolution_metrics(issues)
        
        result = {}
        for name, metric in metrics.items():
            result[name] = metric.to_dict()
        
        return jsonify({
            'status': 'success',
            'metrics': result,
        }), 200
    except Exception as e:
        logger.error(f"Issue metrics error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Trend Analysis Endpoints
# ============================================================================

@analytics_bp.route('/trends/bottlenecks/<project_id>', methods=['GET'])
@require_auth
def get_bottlenecks(project_id):
    """Get bottleneck analysis"""
    try:
        # In real implementation, fetch from database
        issues = []
        
        bottlenecks = analytics_dashboard.trend_analysis.identify_bottlenecks(issues)
        
        return jsonify({
            'status': 'success',
            'bottlenecks': bottlenecks,
        }), 200
    except Exception as e:
        logger.error(f"Bottleneck error: {e}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/trends/forecast/<project_id>', methods=['GET'])
@require_auth
def get_forecast(project_id):
    """Get project forecast"""
    try:
        metric_type = request.args.get('metric', 'completion')
        
        forecast = {
            'metric_type': metric_type,
            'forecast': [],  # Would calculate from ML models
            'confidence': 'high',
            'timestamp': datetime.now().isoformat(),
        }
        
        return jsonify({
            'status': 'success',
            'forecast': forecast,
        }), 200
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Benchmark Endpoints
# ============================================================================

@analytics_bp.route('/benchmark/compare', methods=['POST'])
@require_auth
def compare_benchmark():
    """Compare metrics to industry benchmark"""
    try:
        data = request.get_json()
        metric_name = data.get('metric')
        value = data.get('value')
        
        if not metric_name or value is None:
            return jsonify({'error': 'Missing metric or value'}), 400
        
        comparison = analytics_dashboard.benchmark_analysis.compare_to_benchmark(
            metric_name, value
        )
        
        return jsonify({
            'status': 'success',
            'comparison': comparison,
        }), 200
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/benchmark/list', methods=['GET'])
@require_auth
def list_benchmarks():
    """List all available benchmarks"""
    try:
        benchmarks = analytics_dashboard.benchmark_analysis.INDUSTRY_BENCHMARKS
        
        return jsonify({
            'status': 'success',
            'benchmarks': benchmarks,
        }), 200
    except Exception as e:
        logger.error(f"Benchmark list error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Health Check
# ============================================================================

@analytics_bp.route('/health', methods=['GET'])
def analytics_health():
    """Analytics system health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'components': {
                'project_analytics': 'ready',
                'trend_analysis': 'ready',
                'benchmark_analysis': 'ready',
                'dashboard': 'ready',
            },
            'timestamp': datetime.now().isoformat(),
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# app/routes/health.py
"""
Health check and monitoring endpoints for load balancers and monitoring systems.
"""

from flask import Blueprint, jsonify, current_app
from app.models import db, User, Project, Issue
from datetime import datetime
import logging

health_bp = Blueprint('health', __name__)
logger = logging.getLogger('monitoring')


@health_bp.route('/health', methods=['GET'])
@health_bp.route('/health/live', methods=['GET'])
def health_check():
    """
    Basic health check endpoint.
    Returns 200 if service is alive.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Project Management System',
        'version': current_app.config.get('APP_VERSION', '2.0.0')
    }), 200


@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check endpoint.
    Returns 200 only if all dependencies are available.
    """
    
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'logging': check_logging(),
    }
    
    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503
    
    return jsonify({
        'status': 'ready' if all_ready else 'not_ready',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': checks
    }), status_code


@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health():
    """
    Detailed health check with statistics.
    """
    
    try:
        # Database stats
        user_count = User.query.count()
        project_count = Project.query.count()
        issue_count = Issue.query.count()
        
        # Get database connection pool status
        pool = db.engine.pool
        pool_info = {
            'size': getattr(pool, 'size', lambda: 'N/A')(),
            'checked_out': getattr(pool, 'checkedout', lambda: 'N/A')(),
        }
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'status': 'connected',
                'users': user_count,
                'projects': project_count,
                'issues': issue_count,
                'pool': pool_info
            },
            'cache': check_cache(),
            'uptime_seconds': get_uptime_seconds(),
        }), 200
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Prometheus-compatible metrics endpoint.
    """
    
    metrics_data = []
    
    # Database metrics
    try:
        user_count = User.query.count()
        project_count = Project.query.count()
        issue_count = Issue.query.count()
        
        metrics_data.append(f'app_users_total {user_count}')
        metrics_data.append(f'app_projects_total {project_count}')
        metrics_data.append(f'app_issues_total {issue_count}')
        
    except Exception as e:
        logger.error(f"Failed to collect metrics: {str(e)}")
    
    # System metrics
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    metrics_data.append(f'process_memory_bytes {process.memory_info().rss}')
    metrics_data.append(f'process_cpu_percent {process.cpu_percent()}')
    metrics_data.append(f'process_uptime_seconds {get_uptime_seconds()}')
    
    # Combine all metrics
    metrics_text = '\n'.join(metrics_data)
    
    return metrics_text, 200, {'Content-Type': 'text/plain; version=0.0.4'}


def check_database():
    """Check if database is connected and responsive."""
    try:
        db.session.execute('SELECT 1')
        return True
    except Exception as e:
        logger.error(f"Database check failed: {str(e)}")
        return False


def check_cache():
    """Check if cache is available (stub - implement with Redis if used)."""
    try:
        # Placeholder - implement with actual cache check
        return True
    except Exception as e:
        logger.error(f"Cache check failed: {str(e)}")
        return False


def check_logging():
    """Check if logging is functional."""
    try:
        logger.info("Health check test log")
        return True
    except Exception as e:
        logger.error(f"Logging check failed: {str(e)}")
        return False


def get_uptime_seconds():
    """Get application uptime in seconds."""
    import time
    start_time = current_app.config.get('START_TIME')
    if start_time:
        return int(time.time() - start_time)
    return 0

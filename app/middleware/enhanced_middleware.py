# app/middleware/enhanced_middleware.py
"""
Enhanced middleware for request/response logging, rate limiting, and security.
"""

import logging
import time
import functools
from datetime import datetime, timedelta
from flask import request, session, g, abort, jsonify
from collections import defaultdict
import json

# Setup audit logger
audit_logger = logging.getLogger('audit')

class RequestLogger:
    """Comprehensive request/response logging."""
    
    def __init__(self):
        self.logger = logging.getLogger('requests')
    
    def log_request(self, method, path, user_id=None, ip_address=None):
        """Log incoming request."""
        timestamp = datetime.utcnow().isoformat()
        self.logger.info(f"{timestamp} | {method} {path} | User: {user_id} | IP: {ip_address}")
    
    def log_response(self, method, path, status_code, duration_ms, user_id=None):
        """Log outgoing response."""
        timestamp = datetime.utcnow().isoformat()
        status_emoji = '✅' if status_code < 400 else '⚠️' if status_code < 500 else '❌'
        self.logger.info(f"{timestamp} | {method} {path} | {status_code} {status_emoji} | {duration_ms:.2f}ms | User: {user_id}")
    
    def log_error(self, method, path, error_msg, status_code):
        """Log errors."""
        timestamp = datetime.utcnow().isoformat()
        self.logger.error(f"{timestamp} | {method} {path} | ERROR {status_code}: {error_msg}")
    
    def log_security_event(self, event_type, details, user_id=None, severity='INFO'):
        """Log security-related events."""
        timestamp = datetime.utcnow().isoformat()
        audit_logger.log(
            logging.WARNING if severity == 'HIGH' else logging.INFO,
            f"{timestamp} | {severity} | {event_type} | User: {user_id} | Details: {details}"
        )


class RateLimiter:
    """Rate limiting for API endpoints and sensitive routes."""
    
    def __init__(self, default_limit_per_minute=60, default_limit_per_hour=3600):
        self.default_limit_per_minute = default_limit_per_minute
        self.default_limit_per_hour = default_limit_per_hour
        self.request_counts = defaultdict(lambda: {'minute': [], 'hour': []})
        self.logger = logging.getLogger('rate_limit')
    
    def get_client_identifier(self, request):
        """Get unique identifier for client."""
        # Try to get from session first (authenticated user)
        if 'user_id' in session:
            return f"user_{session['user_id']}"
        
        # Fall back to IP address
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        
        return request.remote_addr
    
    def is_rate_limited(self, identifier, endpoint=None, limit_per_minute=None, limit_per_hour=None):
        """Check if request should be rate limited."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        limit_per_minute = limit_per_minute or self.default_limit_per_minute
        limit_per_hour = limit_per_hour or self.default_limit_per_hour
        
        # Clean old entries
        self.request_counts[identifier]['minute'] = [
            ts for ts in self.request_counts[identifier]['minute'] 
            if ts > minute_ago
        ]
        self.request_counts[identifier]['hour'] = [
            ts for ts in self.request_counts[identifier]['hour'] 
            if ts > hour_ago
        ]
        
        # Check limits
        minute_count = len(self.request_counts[identifier]['minute'])
        hour_count = len(self.request_counts[identifier]['hour'])
        
        if minute_count >= limit_per_minute or hour_count >= limit_per_hour:
            self.logger.warning(f"Rate limit exceeded for {identifier}: {minute_count}/min, {hour_count}/hour")
            return True
        
        # Record this request
        self.request_counts[identifier]['minute'].append(now)
        self.request_counts[identifier]['hour'].append(now)
        
        return False
    
    def get_limits(self, identifier):
        """Get current limits for identifier."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        minute_count = len([ts for ts in self.request_counts[identifier]['minute'] if ts > minute_ago])
        hour_count = len([ts for ts in self.request_counts[identifier]['hour'] if ts > hour_ago])
        
        return {
            'requests_this_minute': minute_count,
            'requests_this_hour': hour_count,
            'limit_per_minute': self.default_limit_per_minute,
            'limit_per_hour': self.default_limit_per_hour
        }


# Global instances
request_logger = RequestLogger()
rate_limiter = RateLimiter()


def register_middleware(app):
    """Register all middleware with Flask app."""
    
    @app.before_request
    def before_request():
        """Before request processing."""
        g.start_time = time.time()
        g.start_timestamp = datetime.utcnow()
        
        # Log request
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_id = session.get('user_id')
        request_logger.log_request(request.method, request.path, user_id, client_ip)
        
        # Rate limiting for sensitive routes
        sensitive_routes = ['/api/', '/login', '/register', '/forgot-password']
        is_sensitive = any(request.path.startswith(route) for route in sensitive_routes)
        
        if is_sensitive:
            identifier = rate_limiter.get_client_identifier(request)
            
            # Different limits for different endpoints
            if request.path.startswith('/api/'):
                limit_minute = 100
                limit_hour = 3000
            elif request.path.startswith('/login'):
                limit_minute = 5
                limit_hour = 50
            else:
                limit_minute = 30
                limit_hour = 500
            
            if rate_limiter.is_rate_limited(identifier, request.path, limit_minute, limit_hour):
                request_logger.log_security_event(
                    'RATE_LIMIT_EXCEEDED',
                    f'Endpoint: {request.path}, Identifier: {identifier}',
                    user_id,
                    'HIGH'
                )
                return jsonify({
                    'error': 'Too many requests',
                    'message': 'Please wait before making another request'
                }), 429
    
    @app.after_request
    def after_request(response):
        """After request processing."""
        duration = (time.time() - g.start_time) * 1000  # Convert to ms
        user_id = session.get('user_id')
        
        # Log response
        request_logger.log_response(
            request.method,
            request.path,
            response.status_code,
            duration,
            user_id
        )
        
        # Add timing headers
        response.headers['X-Response-Time'] = f"{duration:.2f}ms"
        response.headers['X-Request-ID'] = g.get('request_id', 'unknown')
        
        return response
    
    @app.errorhandler(429)
    def handle_rate_limit(e):
        """Handle rate limit errors."""
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429


def rate_limit(limit_per_minute=60, limit_per_hour=3600):
    """Decorator for rate limiting specific routes."""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = rate_limiter.get_client_identifier(request)
            
            if rate_limiter.is_rate_limited(identifier, request.path, limit_per_minute, limit_per_hour):
                abort(429)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def audit_log(action, resource_type='unknown'):
    """Decorator to log audit events."""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            
            try:
                result = f(*args, **kwargs)
                
                # Log success
                request_logger.log_security_event(
                    action,
                    f'Resource: {resource_type}, IP: {client_ip}',
                    user_id,
                    'INFO'
                )
                
                return result
            except Exception as e:
                # Log failure
                request_logger.log_security_event(
                    f'{action}_FAILED',
                    f'Resource: {resource_type}, Error: {str(e)}, IP: {client_ip}',
                    user_id,
                    'HIGH'
                )
                raise
        return decorated_function
    return decorator


# Endpoint-specific rate limiters
API_RATE_LIMIT = rate_limit(limit_per_minute=100, limit_per_hour=3000)
LOGIN_RATE_LIMIT = rate_limit(limit_per_minute=5, limit_per_hour=50)
GENERAL_RATE_LIMIT = rate_limit(limit_per_minute=60, limit_per_hour=1000)

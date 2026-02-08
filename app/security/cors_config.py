# app/security/cors_config.py
"""
CORS and security headers configuration.
"""

from flask_cors import CORS
from flask import request
import logging

logger = logging.getLogger('security')


def init_cors(app):
    """
    Initialize CORS with secure configuration.
    """
    
    cors_config = {
        'origins': [
            'http://localhost:3000',
            'http://localhost:5000',
            'http://127.0.0.1:5000',
            'http://127.0.0.1:3000',
        ],
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization', 'X-CSRF-Token'],
        'expose_headers': ['Content-Type', 'X-Total-Count', 'X-Page-Count'],
        'supports_credentials': True,
        'max_age': 3600,
    }
    
    # Add environment-specific origins
    if app.config.get('ENVIRONMENT') == 'production':
        cors_config['origins'] = [
            'https://yourapp.com',
            'https://www.yourapp.com',
        ]
    
    CORS(app, resources={
        '/api/*': cors_config,
        '/health*': {'origins': '*'},  # Health checks accessible from anywhere
    })
    
    logger.info('CORS configured with secure settings')


def add_security_headers(app):
    """
    Add comprehensive security headers to all responses.
    """
    
    @app.after_request
    def set_security_headers(response):
        """Add security headers to response."""
        
        # Content Security Policy - Strict policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'self'; "
            "form-action 'self'; "
            "base-uri 'self'; "
            "object-src 'none'"
        )
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Clickjacking protection
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # XSS Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response.headers['Permissions-Policy'] = (
            'camera=(self), '
            'microphone=(self), '
            'geolocation=(), '
            'payment=(), '
            'usb=(), '
            'magnetometer=(), '
            'gyroscope=(), '
            'accelerometer=()'
        )
        
        # Cache control for sensitive content
        if 'text/html' in response.content_type:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        # HTTPS enforcement in production
        if not app.debug:
            response.headers['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )
        
        # Disable client-side caching for security pages
        if any(path in request.path for path in ['/admin', '/profile', '/settings']):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        
        return response
    
    logger.info('Security headers configured')


def init_security(app):
    """
    Initialize all security features.
    """
    init_cors(app)
    add_security_headers(app)
    logger.info('Security configuration complete')

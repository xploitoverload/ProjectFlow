# app/__init__.py - Application Factory Pattern
"""
Enterprise-grade Flask Application Factory
Following clean architecture principles with proper separation of concerns.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from flask_talisman import Talisman
import logging
from logging.handlers import RotatingFileHandler
import os

from config import config
from models import db  # Use the db instance from models.py

# Initialize extensions (without creating new db)
login_manager = LoginManager()
csrf = CSRFProtect()
compress = Compress()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri="memory://",
    enabled=False  # Disabled for debugging
)


def create_app(config_name=None):
    """Application factory function following Flask best practices."""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)
    limiter.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Setup Talisman for security headers
    csp = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "https://unpkg.com", "https://cdn.jsdelivr.net"],
        'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        'font-src': ["'self'", "https://fonts.gstatic.com"],
        'img-src': ["'self'", "data:", "https:"],
        'connect-src': ["'self'"],
        'frame-ancestors': "'self'",
        'form-action': "'self'",
        'base-uri': "'self'",
        'object-src': "'none'"
    }
    
    # Apply Talisman with environment-appropriate settings
    # In development, use relaxed CSP; in production, use strict CSP with nonces
    if config_name == 'production':
        Talisman(app, 
                 content_security_policy=csp,
                 force_https=True,
                 strict_transport_security=True,
                 strict_transport_security_max_age=31536000,
                 session_cookie_secure=True,
                 session_cookie_http_only=True)
    # Skip Talisman in development for faster startup
    
    # Additional security headers via after_request
    @app.after_request
    def add_security_headers(response):
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # XSS Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Permissions Policy - ALLOW camera and microphone
        response.headers['Permissions-Policy'] = 'camera=(self), microphone=(self), geolocation=()'
        # Cache control for sensitive pages
        if 'text/html' in response.content_type:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
    
    # Setup logging
    _setup_logging(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register context processors
    _register_context_processors(app)
    
    # Register request hooks for user activity tracking
    _register_request_hooks(app)
    
    # Initialize Phase 6 Enterprise Systems
    _init_phase6_systems(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    app.logger.info(f'Application started in {config_name} mode')
    
    return app


def _register_request_hooks(app):
    """Register before/after request hooks."""
    from flask import session
    from datetime import datetime
    
    @app.before_request
    def update_user_activity():
        """Update user's last activity timestamp."""
        if 'user_id' in session:
            from app.models import User
            try:
                user = User.query.get(session['user_id'])
                if user:
                    user.last_activity = datetime.utcnow()
                    db.session.commit()
            except Exception:
                pass  # Don't break the request if activity update fails


def _setup_logging(app):
    """Configure application logging with rotation."""
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # File handler for errors
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # File handler for all logs
    info_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,
        backupCount=10
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    
    # Security audit log
    audit_handler = RotatingFileHandler(
        'logs/audit.log',
        maxBytes=10485760,
        backupCount=20
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(logging.Formatter(
        '%(asctime)s AUDIT: %(message)s'
    ))
    
    app.logger.addHandler(error_handler)
    app.logger.addHandler(info_handler)
    
    # Create audit logger
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(audit_handler)
    
    if app.config['DEBUG']:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)


def _register_blueprints(app):
    """Register application blueprints."""
    
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.projects import projects_bp
    from app.routes.phase6_routes import phase6_bp
    from app.routes.ml_routes import ml_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.automation_routes import automation_bp
    from app.routes.pwa_routes import pwa_bp
    from app.routes.notifications_routes import notifications_bp
    from app.routes.reporting_routes import reporting_bp
    from app.routes.integrations_routes import integrations_bp
    from app.routes.security_routes import security_bp
    from app.routes.face_recognition_routes import face_bp
    from app.routes.compliance_routes import compliance_bp
    from app.routes.knowledge_base_routes import kb_bp
    from app.routes.team_collaboration_routes import team_bp
    from app.routes.mobile_routes import mobile_bp
    from app.routes.tenant_routes import tenant_bp
    from app.routes.customer_portal_routes import portal_bp
    from app.admin_secure.routes import create_secure_admin_blueprint
    import secrets
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(ml_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(automation_bp)
    app.register_blueprint(pwa_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(reporting_bp)
    app.register_blueprint(integrations_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(face_bp)
    app.register_blueprint(compliance_bp)
    app.register_blueprint(kb_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(mobile_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(portal_bp)
    app.register_blueprint(phase6_bp)
    app.register_blueprint(projects_bp, url_prefix='/project')
    
    # Register secure admin blueprint with persistent hidden token
    token_file = os.path.join(os.path.dirname(__file__), '.secure_token')
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            hidden_token = f.read().strip()
    else:
        hidden_token = secrets.token_urlsafe(32)
        with open(token_file, 'w') as f:
            f.write(hidden_token)
    
    admin_secure_bp = create_secure_admin_blueprint(hidden_token)
    app.register_blueprint(admin_secure_bp, url_prefix=f'/secure-mgmt-{hidden_token}/')
    
    # Store hidden token in app config for access in templates
    app.config['HIDDEN_ADMIN_TOKEN'] = hidden_token
    app.logger.info(f'Secure admin panel available at: /secure-mgmt-{hidden_token}/')


def _register_error_handlers(app):
    """Register error handlers."""
    
    from flask import render_template, request, redirect, url_for, flash
    from flask_wtf.csrf import CSRFError
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """Handle CSRF token errors gracefully."""
        flash('Session expired or security token invalid. Please try again.', 'warning')
        # Try to redirect back to the previous page
        referrer = request.headers.get('Referer')
        if referrer:
            return redirect(referrer)
        return redirect(url_for('main.dashboard'))
    
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', 
                              error_code=400,
                              error_message='The request was invalid or malformed.'), 400
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html',
                              error_code=403,
                              error_message='You do not have permission to access this resource.'), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html',
                              error_code=404,
                              error_message='The requested resource was not found.'), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return render_template('error.html',
                              error_code=429,
                              error_message='Rate limit exceeded. Please try again later.'), 429
    
    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        app.logger.error(f'Internal error: {str(e)}')
        return render_template('error.html',
                              error_code=500,
                              error_message='An unexpected error occurred.'), 500


def _register_context_processors(app):
    """Register template context processors."""
    
    from datetime import datetime
    
    @app.context_processor
    def inject_globals():
        return {
            'now': datetime.utcnow(),
            'app_name': app.config.get('APP_NAME', 'Project Management'),
            'app_version': app.config.get('APP_VERSION', '2.0.0')
        }
    
    # Note: CSRF token is provided by Flask-WTF's CSRFProtect extension
    # Do NOT override csrf_token() - let Flask-WTF handle it
    
    # Template filter to format role names nicely
    @app.template_filter('format_role')
    def format_role(role):
        """Convert role slug to human-readable format"""
        if not role:
            return 'Unknown'
        # Replace underscores with spaces and title case
        return role.replace('_', ' ').title()
    
    # Template filter to get role badge color
    @app.template_filter('role_badge_color')
    def role_badge_color(role):
        """Get appropriate badge color for role"""
        if not role:
            return 'gray'
        role_lower = role.lower()
        if role_lower in ['admin', 'ceo', 'cto', 'vp_engineering']:
            return 'purple'
        elif role_lower in ['director', 'senior_manager', 'manager', 'team_lead', 'tech_lead']:
            return 'blue'
        elif 'senior' in role_lower or 'lead' in role_lower or 'principal' in role_lower:
            return 'green'
        elif 'engineer' in role_lower or 'developer' in role_lower:
            return 'cyan'
        elif 'designer' in role_lower:
            return 'pink'
        elif 'qa' in role_lower or 'test' in role_lower:
            return 'orange'
        elif role_lower in ['intern', 'trainee']:
            return 'yellow'
        else:
            return 'gray'
    
    # Template filter to format dates nicely
    @app.template_filter('dateformat')
    def dateformat(value, format_str='%B %d, %Y at %I:%M %p'):
        """Format date/datetime object to human-readable string"""
        if not value:
            return ''
        # Handle string timestamps (ISO format)
        if isinstance(value, str):
            from datetime import datetime
            try:
                # Try parsing ISO format
                if 'T' in value:
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return value
        # Format the datetime
        try:
            return value.strftime(format_str)
        except (AttributeError, ValueError):
            return str(value)

def _init_phase6_systems(app):
    """Initialize Phase 6 enterprise systems."""
    
    # Initialize WebSocket system
    try:
        from app.websocket import init_websocket
        socketio = init_websocket(app, None)  # SocketIO will be initialized separately
        app.socketio = socketio
        app.logger.info('✓ WebSocket system initialized')
    except Exception as e:
        app.logger.warning(f'WebSocket initialization deferred: {e}')
    
    # Initialize Batch Processor
    try:
        from app.operations import init_batch_processor
        init_batch_processor()
        app.logger.info('✓ Batch processor initialized')
    except Exception as e:
        app.logger.warning(f'Batch processor error: {e}')
    
    # Initialize Backup Manager
    try:
        from app.recovery import init_backup_manager
        backup_dir = os.path.join(app.instance_path, 'backups')
        db_path = os.path.join(app.instance_path, 'app.db')
        init_backup_manager(backup_dir, db_path)
        app.logger.info('✓ Backup manager initialized')
    except Exception as e:
        app.logger.warning(f'Backup manager error: {e}')
    
    # Initialize GraphQL
    try:
        from app.api.graphql_api import init_graphql
        init_graphql()
        app.logger.info('✓ GraphQL API initialized')
    except Exception as e:
        app.logger.warning(f'GraphQL initialization error: {e}')
    
    # Initialize Performance Monitor
    try:
        from app.monitoring.performance import init_performance_monitor
        init_performance_monitor(history_limit=10000)
        app.logger.info('✓ Performance monitor initialized')
    except Exception as e:
        app.logger.warning(f'Performance monitor error: {e}')
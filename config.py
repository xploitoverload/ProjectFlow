# config.py - Enhanced Configuration Settings
"""
Enterprise-grade configuration management with security best practices.
Supports environment variables for secrets and environment-specific settings.
"""

import os
from datetime import timedelta


def get_env_variable(name, default=None, required=False):
    """Get environment variable with optional default and required flag."""
    value = os.environ.get(name, default)
    if required and value is None:
        raise ValueError(f"Required environment variable '{name}' is not set")
    return value


class Config:
    """Base configuration with secure defaults."""
    
    # Application Info
    APP_NAME = 'Project Management System'
    APP_VERSION = '2.0.0'
    
    # Secret Key - MUST be set via environment variable in production
    SECRET_KEY = get_env_variable('SECRET_KEY', 'dev-secret-key-change-in-production-immediately')
    
    # Database - use absolute path
    _basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = get_env_variable(
        'DATABASE_URL', 
        f'sqlite:///{os.path.join(_basedir, "instance", "project_management.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Session Configuration
    SESSION_COOKIE_NAME = 'pms_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_TIMEOUT_MINUTES = 30
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Security Headers
    SECURITY_HEADERS_ENABLED = True
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    
    # Password Policy
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Account Lockout
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES = 30
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour


class DevelopmentConfig(Config):
    """Development configuration with debug features."""
    
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
    # Less strict session for development
    SESSION_COOKIE_SECURE = False
    
    # Verbose logging
    LOG_LEVEL = 'DEBUG'
    
    # Relaxed rate limiting for testing
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration with strict security."""
    
    DEBUG = False
    TESTING = False
    
    # Require SECRET_KEY in production (checked at runtime)
    @property
    def SECRET_KEY(self):
        key = get_env_variable('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY environment variable is required in production")
        return key
    
    # Production database
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        uri = get_env_variable('DATABASE_URL')
        if not uri:
            raise ValueError("DATABASE_URL environment variable is required in production")
        return uri
    
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
    }
    
    # Strict session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Stricter rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = get_env_variable('REDIS_URL', 'memory://')
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Shorter session in production
    SESSION_TIMEOUT_MINUTES = 20
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=20)
    
    # HSTS and other security headers
    PREFERRED_URL_SCHEME = 'https'


class TestingConfig(Config):
    """Testing configuration with isolated database."""
    
    TESTING = True
    DEBUG = True
    
    # Test database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/test_project_management.db'
    SQLALCHEMY_ECHO = False
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False
    
    # Simple secret key for testing
    SECRET_KEY = 'test-secret-key-not-for-production'
    
    # Fast password hashing for tests
    PASSWORD_HASH_ROUNDS = 4


class StagingConfig(ProductionConfig):
    """Staging configuration - production-like but with debug info."""
    
    DEBUG = True
    LOG_LEVEL = 'INFO'
    
    # Allow non-HTTPS in staging if needed
    SESSION_COOKIE_SECURE = get_env_variable('REQUIRE_HTTPS', 'false').lower() == 'true'


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = get_env_variable('FLASK_ENV', 'development')
    return config.get(env, config['default'])
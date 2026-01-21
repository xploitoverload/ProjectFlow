# app/security/__init__.py
"""
Comprehensive Security Module
Production-grade security following OWASP Top 10 and CWE Top 25.
"""

from .authorization import (
    check_ownership,
    check_resource_access,
    verify_user_owns_resource,
    admin_only,
    owner_or_admin,
    require_permission,
    ROLE_PERMISSIONS
)

from .validation import (
    validate_and_sanitize,
    InputValidator,
    sanitize_html,
    validate_file_upload,
    is_safe_redirect_url,
    get_safe_redirect_url
)

from .rate_limiting import (
    RateLimiter,
    login_rate_limit,
    api_rate_limit,
    sensitive_action_rate_limit
)

from .session_security import (
    SessionManager,
    regenerate_session,
    invalidate_all_sessions,
    require_fresh_auth
)

from .audit import (
    AuditLogger,
    log_security_event,
    log_access_attempt,
    log_data_access,
    log_admin_action
)

__all__ = [
    'check_ownership',
    'check_resource_access', 
    'verify_user_owns_resource',
    'admin_only',
    'owner_or_admin',
    'require_permission',
    'ROLE_PERMISSIONS',
    'validate_and_sanitize',
    'InputValidator',
    'sanitize_html',
    'validate_file_upload',
    'is_safe_redirect_url',
    'get_safe_redirect_url',
    'RateLimiter',
    'login_rate_limit',
    'api_rate_limit',
    'sensitive_action_rate_limit',
    'SessionManager',
    'regenerate_session',
    'invalidate_all_sessions',
    'require_fresh_auth',
    'AuditLogger',
    'log_security_event',
    'log_access_attempt',
    'log_data_access',
    'log_admin_action'
]

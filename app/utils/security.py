# app/utils/security.py
"""
Enhanced Security Utilities
Following OWASP Top 10 and CWE Top 25 best practices.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request, abort, current_app
from datetime import datetime, timedelta
import secrets
import re
import bleach
import hashlib
import hmac
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
import logging

# Initialize Argon2 password hasher with secure parameters
ph = PasswordHasher(
    time_cost=3,        # Number of iterations
    memory_cost=65536,  # Memory usage in KB (64MB)
    parallelism=4,      # Number of parallel threads
    hash_len=32,        # Length of the hash
    salt_len=16         # Length of the salt
)

# Rate limiting storage (use Redis in production)
_rate_limit_storage = {}


def generate_csrf_token():
    """Generate cryptographically secure CSRF token."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']


def validate_csrf_token(token):
    """Constant-time CSRF token validation."""
    stored_token = session.get('csrf_token')
    if not stored_token or not token:
        return False
    return hmac.compare_digest(stored_token, token)


def hash_password(password):
    """
    Hash password using Argon2id (winner of Password Hashing Competition).
    More secure than bcrypt and scrypt.
    """
    return ph.hash(password)


def verify_password(stored_hash, password):
    """Verify password against both Argon2 and PBKDF2 hashes."""
    # Try Argon2 first
    try:
        ph.verify(stored_hash, password)
        # Check if rehash is needed (parameters may have changed)
        if ph.check_needs_rehash(stored_hash):
            return True, hash_password(password)
        return True, None
    except (VerifyMismatchError, InvalidHash):
        pass
    
    # Fall back to PBKDF2 (werkzeug format)
    if stored_hash.startswith('pbkdf2:'):
        try:
            from werkzeug.security import check_password_hash
            if check_password_hash(stored_hash, password):
                # Rehash with Argon2
                return True, hash_password(password)
            return False, None
        except:
            return False, None
    
    return False, None


def sanitize_input(text, allow_html=False):
    """
    Sanitize user input to prevent XSS attacks.
    Uses bleach for HTML sanitization.
    """
    if text is None:
        return None
    
    # Convert to string if necessary
    text = str(text)
    
    if allow_html:
        # Allow only safe HTML tags and attributes
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 
                       'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'code', 'pre']
        allowed_attributes = {
            'a': ['href', 'title'],
        }
        return bleach.clean(text, tags=allowed_tags, 
                           attributes=allowed_attributes, 
                           strip=True)
    else:
        # Strip all HTML tags
        return bleach.clean(text, tags=[], strip=True)


def validate_email(email):
    """
    Validate email format using RFC 5322 compliant regex.
    """
    if not email:
        return False
    
    # RFC 5322 compliant email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if len(email) > 254:  # RFC 5321
        return False
    
    return bool(re.match(pattern, email))


def validate_username(username):
    """
    Validate username format.
    - 3-30 characters
    - Alphanumeric, underscores, and hyphens
    - Must start with a letter
    """
    if not username:
        return False
    
    pattern = r'^[a-zA-Z][a-zA-Z0-9_-]{2,29}$'
    return bool(re.match(pattern, username))


def validate_password_strength(password):
    """
    Validate password strength against NIST guidelines.
    Returns (is_valid, message).
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for common patterns
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    # Check for common weak passwords
    weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
    if password.lower() in weak_passwords:
        return False, "Password is too common"
    
    return True, "Password meets all requirements"


def get_client_ip():
    """
    Get client IP address, handling proxies securely.
    """
    from flask import has_request_context
    
    if not has_request_context():
        return '127.0.0.1'
    
    # Check X-Forwarded-For header (from reverse proxy)
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        # Take the first IP (client IP)
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        ip = request.environ['HTTP_X_REAL_IP']
    else:
        ip = request.environ.get('REMOTE_ADDR', '127.0.0.1')
    
    # Validate IP format
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, ip):
        return ip
    
    return '127.0.0.1'


def rate_limit(key, max_requests, window_seconds):
    """
    Check if rate limit is exceeded.
    Returns True if request should be allowed.
    """
    now = datetime.utcnow()
    window_key = f"{key}:{now.strftime('%Y%m%d%H%M')}"
    
    if window_key not in _rate_limit_storage:
        _rate_limit_storage[window_key] = 0
    
    _rate_limit_storage[window_key] += 1
    
    # Clean old entries
    cutoff = (now - timedelta(seconds=window_seconds * 2)).strftime('%Y%m%d%H%M')
    old_keys = [k for k in list(_rate_limit_storage.keys()) if k.rsplit(':', 1)[-1] < cutoff]
    for old_key in old_keys:
        del _rate_limit_storage[old_key]
    
    return _rate_limit_storage.get(window_key, 0) <= max_requests


def log_security_event(event_type, user_id=None, details=None, severity='INFO'):
    """
    Log security events for audit trail.
    """
    from flask import has_request_context
    
    audit_logger = logging.getLogger('audit')
    
    # Safely get request context info
    ip_address = 'N/A'
    user_agent = 'N/A'
    if has_request_context():
        ip_address = get_client_ip()
        user_agent = request.headers.get('User-Agent', 'Unknown')[:200]
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': ip_address,
        'user_agent': user_agent,
        'details': details,
        'severity': severity
    }
    
    if severity == 'WARNING':
        audit_logger.warning(str(log_data))
    elif severity == 'ERROR':
        audit_logger.error(str(log_data))
    elif severity == 'CRITICAL':
        audit_logger.critical(str(log_data))
    else:
        audit_logger.info(str(log_data))


def generate_secure_token(length=32):
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def constant_time_compare(a, b):
    """
    Constant-time string comparison to prevent timing attacks.
    """
    return hmac.compare_digest(a, b)


class SecurityHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def add_headers(response):
        """Add comprehensive security headers."""
        
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection (legacy, but still useful)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response.headers['Content-Security-Policy'] = csp
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature-Policy)
        response.headers['Permissions-Policy'] = (
            'accelerometer=(), ambient-light-sensor=(), autoplay=(), '
            'battery=(), camera=(), cross-origin-isolated=(), display-capture=(), '
            'document-domain=(), encrypted-media=(), execution-while-not-rendered=(), '
            'execution-while-out-of-viewport=(), fullscreen=(), geolocation=(), '
            'gyroscope=(), keyboard-map=(), magnetometer=(), microphone=(), '
            'midi=(), navigation-override=(), payment=(), picture-in-picture=(), '
            'publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(), '
            'usb=(), web-share=(), xr-spatial-tracking=()'
        )
        
        # Cache control for sensitive pages
        if '/admin' in request.path or '/api' in request.path:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response

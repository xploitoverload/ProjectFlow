# security.py - Security Utilities and Middleware
from functools import wraps
from flask import session, redirect, url_for, flash, request, abort
from datetime import datetime, timedelta
import secrets
import re
import bleach

# Rate limiting storage (in production, use Redis)
login_attempts = {}
request_counts = {}

def generate_csrf_token():
    """Generate CSRF token"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def validate_csrf_token(token):
    """Validate CSRF token"""
    return token == session.get('csrf_token')

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('login'))
        
        # Check session timeout (30 minutes)
        last_activity = session.get('last_activity')
        if last_activity:
            if datetime.fromisoformat(last_activity) < datetime.utcnow() - timedelta(minutes=30):
                session.clear()
                flash('Session expired. Please log in again.', 'error')
                return redirect(url_for('login'))
        
        session['last_activity'] = datetime.utcnow().isoformat()
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('login'))
        
        if session.get('role') != 'admin':
            log_audit(session.get('user_id'), 'UNAUTHORIZED_ACCESS_ATTEMPT', 
                     f'Attempted to access admin route: {request.endpoint}')
            flash('Admin access required', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_login(ip_address, max_attempts=5, window_minutes=15):
    """Rate limit login attempts by IP"""
    now = datetime.utcnow()
    
    if ip_address not in login_attempts:
        login_attempts[ip_address] = []
    
    # Remove old attempts
    login_attempts[ip_address] = [
        attempt for attempt in login_attempts[ip_address]
        if attempt > now - timedelta(minutes=window_minutes)
    ]
    
    # Check if rate limit exceeded
    if len(login_attempts[ip_address]) >= max_attempts:
        return False
    
    # Add new attempt
    login_attempts[ip_address].append(now)
    return True

def rate_limit_request(ip_address, max_requests=100, window_minutes=1):
    """General rate limiting for requests"""
    now = datetime.utcnow()
    key = f"{ip_address}:{now.strftime('%Y-%m-%d-%H-%M')}"
    
    if key not in request_counts:
        request_counts[key] = 0
    
    request_counts[key] += 1
    
    # Clean old entries
    old_keys = [k for k in request_counts.keys() if k.split(':')[1] < (now - timedelta(minutes=2)).strftime('%Y-%m-%d-%H-%M')]
    for old_key in old_keys:
        del request_counts[old_key]
    
    return request_counts[key] <= max_requests

def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if text is None:
        return None
    
    # Allow only safe HTML tags and attributes
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'ul', 'ol', 'li']
    allowed_attributes = {}
    
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username format"""
    # Only alphanumeric and underscore, 3-20 characters
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is strong"

def validate_sql_input(text):
    """Basic SQL injection prevention"""
    if text is None:
        return True
    
    # Check for common SQL injection patterns
    sql_patterns = [
        r"(\s|^)(union|select|insert|update|delete|drop|create|alter|exec|execute)(\s|$)",
        r"['\";]",
        r"--",
        r"/\*.*\*/",
        r"xp_",
        r"sp_"
    ]
    
    text_lower = str(text).lower()
    for pattern in sql_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False
    
    return True

def get_client_ip():
    """Get client IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    return request.environ.get('REMOTE_ADDR', 'unknown')

def log_audit(user_id, action, details=None):
    """Log security audit event"""
    try:
        from models import db, AuditLog
        audit = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=get_client_ip()
        )
        audit.details = details
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        print(f"Failed to log audit: {e}")

def check_account_lockout(user):
    """Check if account is locked due to failed login attempts"""
    if user.failed_login_attempts >= 5:
        if user.last_login:
            # Lock for 30 minutes
            lockout_time = user.last_login + timedelta(minutes=30)
            if datetime.utcnow() < lockout_time:
                return True, f"Account locked until {lockout_time.strftime('%H:%M')}"
            else:
                # Reset failed attempts after lockout period
                user.failed_login_attempts = 0
                from models import db
                db.session.commit()
                return False, None
        return True, "Account locked due to too many failed login attempts"
    return False, None

def record_failed_login(user):
    """Record failed login attempt"""
    user.failed_login_attempts += 1
    user.last_login = datetime.utcnow()
    from models import db
    db.session.commit()

def reset_failed_login(user):
    """Reset failed login attempts on successful login"""
    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()
    from models import db
    db.session.commit()

class SecurityHeaders:
    """Add security headers to responses"""
    
    @staticmethod
    def add_headers(response):
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevent MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'self';"
        )
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
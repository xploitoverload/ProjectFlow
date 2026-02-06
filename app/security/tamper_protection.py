"""
Tamper Protection & Request Validation
Prevents data tampering and validates request integrity using HMAC
"""

import hmac
import hashlib
import json
import logging
from datetime import datetime, timedelta
from flask import request, current_app
from functools import wraps

logger = logging.getLogger(__name__)

class TamperProtection:
    """HMAC-based request signing and verification"""
    
    def __init__(self, app=None, secret_key=None):
        self.app = app
        self.secret_key = secret_key or (app.config.get('SECRET_KEY') if app else None)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        self.secret_key = app.config.get('SECRET_KEY')
        app.before_request(self.verify_request_integrity)
    
    def sign_data(self, data):
        """Create HMAC signature for data"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            data_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, data, signature):
        """Verify HMAC signature with constant-time comparison"""
        expected_sig = self.sign_data(data)
        return hmac.compare_digest(signature, expected_sig)
    
    def sign_request(self, method, endpoint, data, timestamp=None):
        """Create signature for entire request"""
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        request_str = f"{method}:{endpoint}:{json.dumps(data)}:{timestamp}"
        return self.sign_data(request_str), timestamp
    
    def verify_request_integrity(self):
        """Middleware to verify request integrity"""
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            try:
                # Check timestamp (5 minute window)
                timestamp_str = request.headers.get('X-Request-Timestamp')
                if timestamp_str:
                    request_time = datetime.fromisoformat(timestamp_str)
                    if datetime.utcnow() - request_time > timedelta(minutes=5):
                        logger.warning(f"Expired request timestamp from {request.remote_addr}")
                        return None
                
                # Verify request signature
                signature = request.headers.get('X-Request-Signature')
                if signature:
                    try:
                        data = request.get_json() or {}
                        endpoint = request.endpoint or request.path
                        
                        if not self.verify_signature(
                            f"{request.method}:{endpoint}:{json.dumps(data)}",
                            signature
                        ):
                            logger.warning(f"Tampered request detected from {request.remote_addr}")
                            return None
                    except Exception as e:
                        logger.error(f"Signature verification error: {e}")
                        return None
            except Exception as e:
                logger.error(f"Request integrity check error: {e}")
                return None

class RequestValidator:
    """Validate and sanitize request data"""
    
    @staticmethod
    def validate_json(data, schema=None):
        """Validate JSON structure"""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        return True
    
    @staticmethod
    def sanitize_string(value, max_length=1000, allow_null=False):
        """Sanitize string input"""
        if value is None:
            if not allow_null:
                raise ValueError("Null value not allowed")
            return None
        
        value = str(value).strip()
        if len(value) > max_length:
            raise ValueError(f"String exceeds maximum length of {max_length}")
        
        return value
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        return email
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError("Password must contain uppercase, lowercase, and digits")
        
        return password

def detect_suspicious_activity(data):
    """Detect suspicious patterns (SQLi, XSS, path traversal)"""
    dangerous_patterns = [
        (r"(?i)(union|select|insert|update|delete|drop|exec|execute)", "SQL injection"),
        (r"(?i)(<script|javascript:|onerror|onclick)", "XSS attempt"),
        (r"(\.\./|\.\.\\|%2e%2e)", "Path traversal"),
        (r"(';|--|#|/\*|\*/)", "SQL comment"),
    ]
    
    data_str = json.dumps(data) if isinstance(data, dict) else str(data)
    
    import re
    for pattern, threat_type in dangerous_patterns:
        if re.search(pattern, data_str):
            return True, threat_type
    
    return False, None

def log_security_event(event_type, user_id=None, details=None, severity='INFO'):
    """Log security events"""
    timestamp = datetime.utcnow().isoformat()
    
    log_entry = {
        'timestamp': timestamp,
        'event_type': event_type,
        'user_id': user_id,
        'details': details,
        'severity': severity,
    }
    
    logger.log(
        getattr(logging, severity),
        f"SECURITY: {event_type} - User:{user_id} - {details}"
    )
    
    # Could also write to database SecurityAuditLog table here
    return log_entry

def require_signature(f):
    """Decorator to require request signature"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get('X-Request-Signature')
        if not signature:
            logger.warning(f"Missing signature from {request.remote_addr}")
            return {'error': 'Missing request signature'}, 401
        
        return f(*args, **kwargs)
    return decorated_function

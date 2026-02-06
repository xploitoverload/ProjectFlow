"""
Web Attack Prevention Module
Comprehensive protection against OWASP Top 10 and common web attacks
"""

import re
import logging
import bleach
from urllib.parse import urljoin, urlparse
from functools import wraps
from flask import request, abort, current_app
import html
from markupsafe import escape

logger = logging.getLogger(__name__)


class WebAttackDetection:
    """Detect and prevent web-based attacks"""
    
    # SQL Injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
        r"(-{2}|/\*|\*/|xp_|sp_)",
        r"(;|\|{2}|&{2}|\|\||exec|execute)",
        r"('.*'.*'|\".*\".*\")",
        r"(\bOR\b.*=.*|\bAND\b.*=.*)",
        r"(SLEEP|BENCHMARK|WAITFOR)",
    ]
    
    # Cross-Site Scripting (XSS) patterns
    XSS_PATTERNS = [
        r"(<script[^>]*>.*?</script>)",
        r"(javascript:)",
        r"(onerror|onclick|onload|onmouseover|onkeydown|onsubmit|onchange)=",
        r"(<iframe[^>]*>|<object[^>]*>|<embed[^>]*>)",
        r"(<img[^>]*src=)",
        r"(eval\(|expression\(|vbscript:)",
        r"(<!--.*?-->)",  # Comments
    ]
    
    # Path Traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"(\.\./|\.\.\\|\.\.%2f|\.\.%5c)",
        r"(\.\.\/){2,}",
        r"(%2e%2e/|%252e%252e)",
        r"(\.\.;/|\.\.;\\)",
    ]
    
    # LDAP Injection patterns
    LDAP_INJECTION_PATTERNS = [
        r"([*()\\&|])",
        r"(\*.*\*)",
    ]
    
    # XXE (XML External Entity) patterns
    XXE_PATTERNS = [
        r"(<!DOCTYPE|<!ENTITY|SYSTEM)",
        r"(xmlns|xsi:schemaLocation)",
    ]
    
    # Command Injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"([;&|`]|&&|\|\|)",
        r"(bash|cmd|powershell|sh)",
    ]
    
    # NoSQL Injection patterns
    NOSQL_INJECTION_PATTERNS = [
        r"(\$where|\$regex|\$exists|\$gt|\$lt|\$ne|\$in|\$nin|\$and|\$or)",
    ]
    
    # Log4j/JNDI Injection
    LOG4J_PATTERNS = [
        r"(\$\{jndi:|log4j)",
    ]
    
    # Header Injection patterns
    HEADER_INJECTION_PATTERNS = [
        r"(\r\n|\r|\n|%0d%0a|%0a|%0d)",
    ]

    @staticmethod
    def detect_sql_injection(value):
        """Detect SQL injection attempts"""
        if not isinstance(value, str):
            return False
        
        normalized = value.upper().replace(' ', '')
        for pattern in WebAttackDetection.SQL_INJECTION_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                logger.warning(f"SQL Injection detected in: {value[:50]}")
                return True
        return False
    
    @staticmethod
    def detect_xss(value):
        """Detect Cross-Site Scripting attempts"""
        if not isinstance(value, str):
            return False
        
        for pattern in WebAttackDetection.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"XSS attempt detected in: {value[:50]}")
                return True
        return False
    
    @staticmethod
    def detect_path_traversal(value):
        """Detect path traversal attacks"""
        if not isinstance(value, str):
            return False
        
        for pattern in WebAttackDetection.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Path traversal detected in: {value[:50]}")
                return True
        return False
    
    @staticmethod
    def detect_ldap_injection(value):
        """Detect LDAP injection attempts"""
        if not isinstance(value, str):
            return False
        
        for pattern in WebAttackDetection.LDAP_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"LDAP injection detected in: {value[:50]}")
                return True
        return False
    
    @staticmethod
    def detect_xxe(value):
        """Detect XXE (XML External Entity) attacks"""
        if not isinstance(value, str):
            return False
        
        for pattern in WebAttackDetection.XXE_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"XXE attack detected in: {value[:50]}")
                return True
        return False
    
    @staticmethod
    def detect_command_injection(value):
        """Detect command injection attempts"""
        if not isinstance(value, str):
            return False
        
        for pattern in WebAttackDetection.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Command injection detected in: {value[:50]}")
                return True
        return False
    
    @staticmethod
    def detect_nosql_injection(value):
        """Detect NoSQL injection attempts"""
        if not isinstance(value, str):
            return False
        
        for pattern in WebAttackDetection.NOSQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"NoSQL injection detected in: {value[:50]}")
                return True
        return False
    
    @staticmethod
    def detect_log4j_injection(value):
        """Detect Log4j/JNDI injection"""
        if not isinstance(value, str):
            return False
        
        for pattern in WebAttackDetection.LOG4J_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Log4j injection detected in: {value[:50]}")
                return True
        return False
    
    @staticmethod
    def detect_header_injection(value):
        """Detect header injection attempts"""
        if not isinstance(value, str):
            return False
        
        for pattern in WebAttackDetection.HEADER_INJECTION_PATTERNS:
            if re.search(pattern, value):
                logger.warning(f"Header injection detected in: {value[:50]}")
                return True
        return False
    
    @staticmethod
    def detect_all_attacks(value):
        """Comprehensive attack detection"""
        detectors = [
            WebAttackDetection.detect_sql_injection,
            WebAttackDetection.detect_xss,
            WebAttackDetection.detect_path_traversal,
            WebAttackDetection.detect_ldap_injection,
            WebAttackDetection.detect_xxe,
            WebAttackDetection.detect_command_injection,
            WebAttackDetection.detect_nosql_injection,
            WebAttackDetection.detect_log4j_injection,
            WebAttackDetection.detect_header_injection,
        ]
        
        for detector in detectors:
            if detector(value):
                return True
        return False


class InputSanitizer:
    """Sanitize user inputs to prevent attacks"""
    
    ALLOWED_TAGS = [
        'b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol',
        'li', 'blockquote', 'code', 'pre'
    ]
    
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
    }
    
    @staticmethod
    def sanitize_html(html_content):
        """Sanitize HTML to prevent XSS"""
        if not isinstance(html_content, str):
            return str(html_content)
        
        # Use bleach to sanitize
        cleaned = bleach.clean(
            html_content,
            tags=InputSanitizer.ALLOWED_TAGS,
            attributes=InputSanitizer.ALLOWED_ATTRIBUTES,
            strip=True
        )
        return cleaned
    
    @staticmethod
    def sanitize_text(text):
        """Escape text to prevent XSS"""
        if not isinstance(text, str):
            return str(text)
        
        # HTML escape
        return html.escape(text)
    
    @staticmethod
    def sanitize_url(url):
        """Validate and sanitize URLs"""
        if not isinstance(url, str):
            return ''
        
        try:
            parsed = urlparse(url)
            # Allow only safe schemes
            if parsed.scheme not in ['http', 'https', '']:
                return ''
            
            # Prevent javascript: and data: URLs
            if url.startswith(('javascript:', 'data:', 'vbscript:')):
                return ''
            
            return url
        except Exception as e:
            logger.error(f"URL sanitization error: {e}")
            return ''
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize uploaded filenames"""
        if not isinstance(filename, str):
            return 'file'
        
        # Remove path components
        filename = filename.replace('\\', '').replace('/', '')
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # Prevent empty filenames
        if not filename:
            return 'file'
        
        return filename
    
    @staticmethod
    def sanitize_email(email):
        """Sanitize and validate email"""
        if not isinstance(email, str):
            return ''
        
        # Remove whitespace
        email = email.strip().lower()
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return email
        return ''
    
    @staticmethod
    def sanitize_number(value):
        """Sanitize numeric input"""
        try:
            # Accept integers and floats
            if isinstance(value, (int, float)):
                return value
            
            # Convert string to number
            if isinstance(value, str):
                # Remove any non-numeric characters except . and -
                cleaned = re.sub(r'[^\d\.\-]', '', value)
                
                if '.' in cleaned:
                    return float(cleaned)
                else:
                    return int(cleaned)
        except (ValueError, TypeError):
            return None
        return None


class CSRFProtection:
    """CSRF (Cross-Site Request Forgery) protection"""
    
    @staticmethod
    def require_csrf_token(f):
        """Decorator to require CSRF token"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                token = request.form.get('csrf_token') or \
                        request.headers.get('X-CSRF-Token')
                
                if not token:
                    logger.warning("CSRF token missing")
                    abort(403)
            
            return f(*args, **kwargs)
        return decorated_function


class ClickjackingProtection:
    """Prevent clickjacking attacks"""
    
    @staticmethod
    def require_same_origin(f):
        """Ensure requests come from same origin"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check Origin header
            origin = request.headers.get('Origin')
            referer = request.headers.get('Referer')
            
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                if origin:
                    allowed_origin = request.host_url.rstrip('/')
                    if not origin.startswith(allowed_origin):
                        logger.warning(f"Clickjacking attempt from: {origin}")
                        abort(403)
            
            return f(*args, **kwargs)
        return decorated_function


class FileUploadProtection:
    """Protect against malicious file uploads"""
    
    ALLOWED_EXTENSIONS = {
        'images': {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'},
        'documents': {'pdf', 'doc', 'docx', 'xlsx', 'txt'},
        'archives': {'zip', 'tar', 'gz'},
    }
    
    FORBIDDEN_EXTENSIONS = {
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js',
        'jar', 'zip', 'rar', 'iso', 'dmg', 'pkg', 'deb', 'rpm',
        'apk', 'app', 'bin', 'dll', 'so', 'dylib', 'sh', 'bash',
    }
    
    FORBIDDEN_MIME_TYPES = {
        'application/x-executable',
        'application/x-msdownload',
        'application/x-msdos-program',
        'application/x-sh',
        'application/x-bash',
        'text/x-shellscript',
    }
    
    @staticmethod
    def is_allowed_file(filename, file_category='images'):
        """Check if file is allowed"""
        if not filename:
            return False
        
        # Check extension
        parts = filename.rsplit('.', 1)
        if len(parts) != 2:
            return False
        
        ext = parts[1].lower()
        
        # Forbidden extensions
        if ext in FileUploadProtection.FORBIDDEN_EXTENSIONS:
            return False
        
        # Check against allowed list
        if file_category in FileUploadProtection.ALLOWED_EXTENSIONS:
            return ext in FileUploadProtection.ALLOWED_EXTENSIONS[file_category]
        
        return False
    
    @staticmethod
    def validate_file(file_obj, max_size=5*1024*1024):
        """Validate uploaded file"""
        if not file_obj:
            return False, "No file provided"
        
        # Check size
        file_obj.seek(0, 2)  # Seek to end
        file_size = file_obj.tell()
        file_obj.seek(0)  # Reset to start
        
        if file_size > max_size:
            return False, f"File too large (max {max_size} bytes)"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, "OK"


class CSPHeaderManager:
    """Manage Content Security Policy headers"""
    
    @staticmethod
    def generate_nonce():
        """Generate CSP nonce"""
        import secrets
        return secrets.token_hex(16)
    
    @staticmethod
    def get_csp_header(nonce=None, strict=False):
        """Get appropriate CSP header"""
        if strict:
            # Strict CSP for production
            csp = {
                'default-src': "'self'",
                'script-src': ["'self'"] + ([f"'nonce-{nonce}'"] if nonce else []),
                'style-src': ["'self'"] + ([f"'nonce-{nonce}'"] if nonce else []),
                'img-src': ["'self'", "data:", "https:"],
                'font-src': ["'self'", "https:"],
                'connect-src': ["'self'"],
                'frame-ancestors': "'self'",
                'form-action': "'self'",
                'base-uri': "'self'",
                'object-src': "'none'",
            }
        else:
            # Relaxed CSP for development
            csp = {
                'default-src': "'self'",
                'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
                'style-src': ["'self'", "'unsafe-inline'"],
                'img-src': ["'self'", "data:", "https:"],
                'font-src': ["'self'", "https:"],
                'connect-src': ["'self'"],
                'frame-ancestors': "'self'",
                'form-action': "'self'",
                'base-uri': "'self'",
                'object-src': "'none'",
            }
        
        return csp


def validate_request_input(f):
    """Decorator to validate all request inputs"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check all parameters
        all_params = {}
        
        # GET parameters
        all_params.update(request.args.to_dict())
        
        # POST parameters
        if request.form:
            all_params.update(request.form.to_dict())
        
        # JSON data
        if request.is_json:
            all_params.update(request.get_json() or {})
        
        # Detect attacks in all parameters
        for key, value in all_params.items():
            if isinstance(value, str) and WebAttackDetection.detect_all_attacks(value):
                logger.warning(f"Attack detected in parameter '{key}': {value[:50]}")
                abort(400)
        
        return f(*args, **kwargs)
    return decorated_function


def prevent_open_redirect(url, allowed_hosts=None):
    """Prevent open redirect attacks"""
    if not url:
        return '/'
    
    try:
        parsed = urlparse(url)
        
        # If no scheme, it's relative - allow it
        if not parsed.scheme:
            return url
        
        # If scheme is http or https
        if parsed.scheme in ['http', 'https']:
            if allowed_hosts:
                if parsed.netloc in allowed_hosts:
                    return url
            elif parsed.netloc == request.host:
                return url
        
        # Default redirect
        return '/'
    except Exception as e:
        logger.error(f"Redirect validation error: {e}")
        return '/'

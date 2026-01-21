# app/security/validation.py
"""
Input Validation and Sanitization Module
Prevents XSS, SQL Injection, Command Injection, and other attacks.
"""

import re
import html
import bleach
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse, urljoin
from flask import request
import logging
import os

# python-magic for file type detection (optional but recommended)
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logging.getLogger('security').warning(
        "python-magic not installed. File type detection will be limited. "
        "Install with: pip install python-magic"
    )

security_logger = logging.getLogger('security')

# Allowed HTML tags for rich text
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote', 'span'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'span': ['class'],
}

# Dangerous patterns for SQL injection prevention
SQL_INJECTION_PATTERNS = [
    r"(\s|^)(union|select|insert|update|delete|drop|create|alter|exec|execute)(\s|$|;)",
    r"['\";]--",
    r"/\*.*\*/",
    r"(\s|^)(or|and)(\s+)[\d\w]+=[\d\w]+",
    r"xp_\w+",
    r"sp_\w+",
    r"0x[0-9a-fA-F]+",
    r"char\s*\(\s*\d+\s*\)",
]

# Dangerous patterns for command injection
COMMAND_INJECTION_PATTERNS = [
    r"[;&|`$]",
    r"\$\(",
    r"`.*`",
    r"\|\|",
    r"&&",
    r">\s*\w+",
    r"<\s*\w+",
]

# Dangerous patterns for path traversal
PATH_TRAVERSAL_PATTERNS = [
    r"\.\./",
    r"\.\.\\",
    r"%2e%2e%2f",
    r"%2e%2e/",
    r"\.%2e/",
    r"%2e\./",
]

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {
    'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
    'document': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv'],
    'archive': ['zip', 'tar', 'gz', '7z'],
}

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
    'application/pdf', 'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain', 'text/csv',
    'application/zip', 'application/x-tar', 'application/gzip', 'application/x-7z-compressed',
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class InputValidator:
    """Comprehensive input validation class."""
    
    @staticmethod
    def validate_string(value: Any, min_length: int = 0, max_length: int = 1000,
                        allow_empty: bool = False, pattern: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate a string input.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            if allow_empty:
                return True, ""
            return False, "Value is required"
        
        if not isinstance(value, str):
            return False, "Value must be a string"
        
        value = value.strip()
        
        if not allow_empty and len(value) == 0:
            return False, "Value cannot be empty"
        
        if len(value) < min_length:
            return False, f"Value must be at least {min_length} characters"
        
        if len(value) > max_length:
            return False, f"Value must be at most {max_length} characters"
        
        if pattern and not re.match(pattern, value):
            return False, "Value does not match required format"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format."""
        if not email:
            return False, "Email is required"
        
        email = email.strip().lower()
        
        if len(email) > 254:
            return False, "Email is too long"
        
        # RFC 5322 compliant pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """Validate username format."""
        if not username:
            return False, "Username is required"
        
        username = username.strip()
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 30:
            return False, "Username must be at most 30 characters"
        
        # Alphanumeric, underscores, hyphens, must start with letter
        pattern = r'^[a-zA-Z][a-zA-Z0-9_-]{2,29}$'
        if not re.match(pattern, username):
            return False, "Username must start with a letter and contain only letters, numbers, underscores, and hyphens"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength following NIST guidelines.
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 12:
            return False, "Password must be at least 12 characters"
        
        if len(password) > 128:
            return False, "Password must be at most 128 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+\[\]\\;\'`~]', password):
            return False, "Password must contain at least one special character"
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '123456', 'qwerty', 'admin', 'letmein', 'welcome',
            'monkey', 'dragon', 'master', 'password123', 'admin123'
        ]
        if password.lower() in weak_passwords:
            return False, "Password is too common"
        
        return True, ""
    
    @staticmethod
    def validate_integer(value: Any, min_val: Optional[int] = None, 
                         max_val: Optional[int] = None) -> Tuple[bool, int, str]:
        """
        Validate and parse integer input.
        
        Returns:
            Tuple of (is_valid, parsed_value, error_message)
        """
        try:
            parsed = int(value)
        except (ValueError, TypeError):
            return False, 0, "Value must be a valid integer"
        
        if min_val is not None and parsed < min_val:
            return False, 0, f"Value must be at least {min_val}"
        
        if max_val is not None and parsed > max_val:
            return False, 0, f"Value must be at most {max_val}"
        
        return True, parsed, ""
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """
        Check for SQL injection patterns.
        Returns True if injection detected.
        """
        if not value:
            return False
        
        value_lower = value.lower()
        
        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                security_logger.warning(f"SQL injection pattern detected: {value[:100]}")
                return True
        
        return False
    
    @staticmethod
    def check_command_injection(value: str) -> bool:
        """
        Check for command injection patterns.
        Returns True if injection detected.
        """
        if not value:
            return False
        
        for pattern in COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value):
                security_logger.warning(f"Command injection pattern detected: {value[:100]}")
                return True
        
        return False
    
    @staticmethod
    def check_path_traversal(value: str) -> bool:
        """
        Check for path traversal patterns.
        Returns True if attack detected.
        """
        if not value:
            return False
        
        for pattern in PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                security_logger.warning(f"Path traversal pattern detected: {value[:100]}")
                return True
        
        return False


def sanitize_html(text: str, allow_tags: bool = True) -> str:
    """
    Sanitize HTML content to prevent XSS.
    
    Args:
        text: Input text to sanitize
        allow_tags: Whether to allow safe HTML tags
    """
    if not text:
        return ""
    
    if allow_tags:
        return bleach.clean(
            text,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True
        )
    else:
        return bleach.clean(text, tags=[], strip=True)


def escape_output(text: str) -> str:
    """Escape HTML entities for safe output."""
    if not text:
        return ""
    return html.escape(str(text))


def validate_and_sanitize(data: Dict[str, Any], schema: Dict[str, dict]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Validate and sanitize a dictionary of data against a schema.
    
    Args:
        data: Input data dictionary
        schema: Validation schema
        
    Schema format:
        {
            'field_name': {
                'type': 'string'|'email'|'username'|'password'|'integer'|'boolean',
                'required': True|False,
                'min_length': int,
                'max_length': int,
                'min_val': int,
                'max_val': int,
                'pattern': 'regex',
                'sanitize': True|False,
                'allow_html': True|False,
            }
        }
    
    Returns:
        Tuple of (is_valid, sanitized_data, errors)
    """
    errors = []
    sanitized = {}
    
    for field, rules in schema.items():
        value = data.get(field)
        field_type = rules.get('type', 'string')
        required = rules.get('required', False)
        
        # Check required
        if required and (value is None or value == ''):
            errors.append(f"{field}: This field is required")
            continue
        
        if value is None or value == '':
            sanitized[field] = None
            continue
        
        # Validate based on type
        if field_type == 'string':
            is_valid, error = InputValidator.validate_string(
                value,
                min_length=rules.get('min_length', 0),
                max_length=rules.get('max_length', 1000),
                allow_empty=not required,
                pattern=rules.get('pattern')
            )
            if not is_valid:
                errors.append(f"{field}: {error}")
                continue
            
            # Check for injection attacks
            if InputValidator.check_sql_injection(value):
                errors.append(f"{field}: Invalid characters detected")
                continue
            
            # Sanitize
            if rules.get('sanitize', True):
                if rules.get('allow_html', False):
                    sanitized[field] = sanitize_html(value, allow_tags=True)
                else:
                    sanitized[field] = sanitize_html(value, allow_tags=False)
            else:
                sanitized[field] = value.strip()
                
        elif field_type == 'email':
            is_valid, error = InputValidator.validate_email(value)
            if not is_valid:
                errors.append(f"{field}: {error}")
                continue
            sanitized[field] = value.strip().lower()
            
        elif field_type == 'username':
            is_valid, error = InputValidator.validate_username(value)
            if not is_valid:
                errors.append(f"{field}: {error}")
                continue
            sanitized[field] = value.strip()
            
        elif field_type == 'password':
            is_valid, error = InputValidator.validate_password(value)
            if not is_valid:
                errors.append(f"{field}: {error}")
                continue
            sanitized[field] = value  # Don't strip passwords
            
        elif field_type == 'integer':
            is_valid, parsed, error = InputValidator.validate_integer(
                value,
                min_val=rules.get('min_val'),
                max_val=rules.get('max_val')
            )
            if not is_valid:
                errors.append(f"{field}: {error}")
                continue
            sanitized[field] = parsed
            
        elif field_type == 'boolean':
            if isinstance(value, bool):
                sanitized[field] = value
            elif isinstance(value, str):
                sanitized[field] = value.lower() in ('true', '1', 'yes', 'on')
            else:
                sanitized[field] = bool(value)
        else:
            sanitized[field] = value
    
    return len(errors) == 0, sanitized, errors


def validate_file_upload(file) -> Tuple[bool, str]:
    """
    Validate uploaded file for security.
    
    Args:
        file: FileStorage object from Flask
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file or not file.filename:
        return False, "No file provided"
    
    filename = file.filename
    
    # Check for path traversal
    if InputValidator.check_path_traversal(filename):
        security_logger.warning(f"Path traversal in filename: {filename}")
        return False, "Invalid filename"
    
    # Check extension
    if '.' not in filename:
        return False, "File must have an extension"
    
    ext = filename.rsplit('.', 1)[1].lower()
    all_allowed = []
    for exts in ALLOWED_EXTENSIONS.values():
        all_allowed.extend(exts)
    
    if ext not in all_allowed:
        return False, f"File type not allowed: {ext}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Seek back to start
    
    if size > MAX_FILE_SIZE:
        return False, f"File too large (max {MAX_FILE_SIZE // (1024*1024)}MB)"
    
    if size == 0:
        return False, "File is empty"
    
    # Check MIME type using magic bytes (if available)
    if MAGIC_AVAILABLE:
        try:
            file_content = file.read(2048)
            file.seek(0)
            
            mime = magic.from_buffer(file_content, mime=True)
            if mime not in ALLOWED_MIME_TYPES:
                security_logger.warning(f"Invalid MIME type: {mime} for file {filename}")
                return False, "File type not allowed"
        except Exception as e:
            security_logger.error(f"Error checking file type: {e}")
            return False, "Could not verify file type"
    else:
        # Fallback: just check extension-based MIME type from request
        security_logger.info(f"Magic bytes check skipped (python-magic not installed)")
    
    return True, ""


def is_safe_redirect_url(target: str) -> bool:
    """
    Check if a redirect URL is safe (same origin).
    Prevents open redirect vulnerabilities.
    """
    if not target:
        return False
    
    # Must be relative URL or same host
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return (
        test_url.scheme in ('http', 'https') and
        ref_url.netloc == test_url.netloc
    )


def get_safe_redirect_url(target: Optional[str], fallback: str = '/') -> str:
    """
    Get a safe redirect URL or return fallback.
    """
    if target and is_safe_redirect_url(target):
        return target
    return fallback

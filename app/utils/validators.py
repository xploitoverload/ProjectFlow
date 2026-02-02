# app/utils/validators.py
"""
Input Validation Utilities
Comprehensive validation for all user inputs.
"""

from datetime import datetime
import re
import os
from werkzeug.utils import secure_filename


class ValidationError(Exception):
    """Custom validation exception with field information."""
    
    def __init__(self, field, message, code=None):
        self.field = field
        self.message = message
        self.code = code or 'validation_error'
        super().__init__(f"{field}: {message}")
    
    def to_dict(self):
        return {
            'field': self.field,
            'message': self.message,
            'code': self.code
        }


def validate_required(value, field_name):
    """Validate that a field is not empty."""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(field_name, f'{field_name} is required', 'required')
    return value


def validate_length(value, field_name, min_length=None, max_length=None):
    """Validate string length within bounds."""
    if value is None:
        return value
    
    length = len(str(value))
    
    if min_length is not None and length < min_length:
        raise ValidationError(
            field_name, 
            f'{field_name} must be at least {min_length} characters',
            'min_length'
        )
    
    if max_length is not None and length > max_length:
        raise ValidationError(
            field_name,
            f'{field_name} must be at most {max_length} characters',
            'max_length'
        )
    
    return value


def validate_integer(value, field_name, min_value=None, max_value=None):
    """Validate and convert to integer within range."""
    if value is None:
        return None
    
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(field_name, f'{field_name} must be a valid integer', 'invalid_type')
    
    if min_value is not None and int_value < min_value:
        raise ValidationError(
            field_name,
            f'{field_name} must be at least {min_value}',
            'min_value'
        )
    
    if max_value is not None and int_value > max_value:
        raise ValidationError(
            field_name,
            f'{field_name} must be at most {max_value}',
            'max_value'
        )
    
    return int_value


def validate_float(value, field_name, min_value=None, max_value=None):
    """Validate and convert to float within range."""
    if value is None:
        return None
    
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        raise ValidationError(field_name, f'{field_name} must be a valid number', 'invalid_type')
    
    if min_value is not None and float_value < min_value:
        raise ValidationError(
            field_name,
            f'{field_name} must be at least {min_value}',
            'min_value'
        )
    
    if max_value is not None and float_value > max_value:
        raise ValidationError(
            field_name,
            f'{field_name} must be at most {max_value}',
            'max_value'
        )
    
    return float_value


def validate_date(value, field_name, format='%Y-%m-%d'):
    """Validate and parse date string."""
    if value is None or value == '':
        return None
    
    try:
        return datetime.strptime(value, format)
    except (ValueError, TypeError):
        raise ValidationError(
            field_name,
            f'{field_name} must be a valid date in format {format}',
            'invalid_date'
        )


def validate_date_range(start_date, end_date, start_field='start_date', end_field='end_date'):
    """Validate that end date is after start date."""
    if start_date is None or end_date is None:
        return True
    
    if end_date < start_date:
        raise ValidationError(
            end_field,
            f'{end_field} must be after {start_field}',
            'invalid_date_range'
        )
    
    return True


def validate_enum(value, field_name, allowed_values):
    """Validate that value is in allowed set."""
    if value is None or value == '':
        return None
    
    if value not in allowed_values:
        raise ValidationError(
            field_name,
            f'{field_name} must be one of: {", ".join(allowed_values)}',
            'invalid_enum'
        )
    
    return value


def validate_file_upload(file, field_name, 
                         allowed_extensions=None, 
                         max_size_mb=10,
                         allowed_mimes=None):
    """
    Validate file upload security.
    
    Args:
        file: FileStorage object
        field_name: Name of the field for error messages
        allowed_extensions: Set of allowed file extensions
        max_size_mb: Maximum file size in megabytes
        allowed_mimes: Set of allowed MIME types
    """
    if file is None or file.filename == '':
        return None
    
    # Secure the filename
    filename = secure_filename(file.filename)
    if not filename:
        raise ValidationError(field_name, 'Invalid filename', 'invalid_filename')
    
    # Check extension
    ext = os.path.splitext(filename)[1].lower()
    default_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt'}
    allowed = allowed_extensions or default_extensions
    
    if ext not in allowed:
        raise ValidationError(
            field_name,
            f'File type not allowed. Allowed types: {", ".join(allowed)}',
            'invalid_extension'
        )
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size = max_size_mb * 1024 * 1024
    if size > max_size:
        raise ValidationError(
            field_name,
            f'File too large. Maximum size is {max_size_mb}MB',
            'file_too_large'
        )
    
    # Check MIME type
    if allowed_mimes:
        content_type = file.content_type
        if content_type not in allowed_mimes:
            raise ValidationError(
                field_name,
                f'Invalid file type',
                'invalid_mime'
            )
    
    return filename


def validate_project_key(key):
    """Validate project key format (e.g., PROJ, NUC)."""
    if not key:
        raise ValidationError('key', 'Project key is required', 'required')
    
    pattern = r'^[A-Z]{2,10}$'
    if not re.match(pattern, key.upper()):
        raise ValidationError(
            'key',
            'Project key must be 2-10 uppercase letters',
            'invalid_format'
        )
    
    return key.upper()


def validate_issue_type(issue_type):
    """Validate issue type."""
    allowed = ['story', 'task', 'bug', 'epic', 'subtask']
    return validate_enum(issue_type, 'issue_type', allowed)


def validate_priority(priority):
    """Validate priority level."""
    allowed = ['lowest', 'low', 'medium', 'high', 'highest', 'critical']
    return validate_enum(priority, 'priority', allowed)


def validate_status(status):
    """Validate issue status."""
    allowed = ['open', 'todo', 'in_progress', 'code_review', 
               'testing', 'ready_deploy', 'done', 'closed', 'reopened']
    
    # Allow empty/None values
    if status is None or status == '':
        return None
    
    return validate_enum(status, 'status', allowed)


def validate_project_status(status):
    """Validate project status."""
    allowed = ['Not Started', 'In Progress', 'On Hold', 'Completed', 
               'Active', 'At Risk', 'Blocked']
    return validate_enum(status, 'status', allowed)


def validate_workflow_type(workflow_type):
    """Validate workflow type."""
    allowed = ['agile', 'waterfall', 'hybrid', 'kanban', 'scrum']
    return validate_enum(workflow_type, 'workflow_type', allowed)


def sanitize_input(text, allow_html=False):
    """
    Sanitize input to prevent XSS attacks.
    If allow_html is True, only allow a safe subset of HTML tags.
    """
    try:
        import bleach
        
        if allow_html:
            allowed_tags = ['b', 'i', 'strong', 'em', 'p', 'br', 'blockquote',
                            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'code', 'pre']
            allowed_attributes = {
                'a': ['href', 'title'],
            }
            return bleach.clean(text, tags=allowed_tags, 
                               attributes=allowed_attributes, 
                               strip=True)
        else:
            # Strip all HTML tags
            return bleach.clean(text, tags=[], strip=True)
    except ImportError:
        # If bleach is not installed, do basic sanitization
        import html
        return html.escape(text)


def validate_email(email):
    """
    Validate email format using regex.
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if len(email) > 254:  # RFC 5321 limit
        return False
    
    if re.match(pattern, email):
        return True
    else:
        return False


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
    
    return True, None


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
    if re.match(pattern, username):
        return True
    else:
        return False
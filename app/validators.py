# app/validators.py
"""
Comprehensive input validators for forms and API endpoints.
"""

import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, ValidationError, 
    Optional, NumberRange, URL, AnyOf
)
import bleach


class SecurityValidator:
    """Security-focused validators."""
    
    @staticmethod
    def validate_username(form, field):
        """Validate username format and length."""
        username = field.data.strip() if field.data else ""
        
        # Check length
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters long.')
        if len(username) > 32:
            raise ValidationError('Username must not exceed 32 characters.')
        
        # Check allowed characters (alphanumeric, dash, underscore only)
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValidationError('Username can only contain letters, numbers, dashes, and underscores.')
        
        # Check if already exists
        from app.models import User
        existing = User.query.filter_by(username=username).first()
        if existing and form.user_id != existing.id:
            raise ValidationError('Username already taken.')
    
    @staticmethod
    def validate_password(form, field):
        """Validate password strength."""
        password = field.data
        
        if not password:
            raise ValidationError('Password is required.')
        
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        if len(password) > 128:
            raise ValidationError('Password must not exceed 128 characters.')
        
        # Check password complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not (has_upper and has_lower and has_digit):
            raise ValidationError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, and one number.'
            )
    
    @staticmethod
    def validate_email(form, field):
        """Validate email address."""
        email = field.data.lower().strip() if field.data else ""
        
        # RFC 5322 simplified email regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_regex, email):
            raise ValidationError('Please enter a valid email address.')
        
        # Check against disposable email list (basic check)
        disposable_domains = ['tempmail.com', 'throwaway.email', '10minutemail.com']
        domain = email.split('@')[1]
        if domain in disposable_domains:
            raise ValidationError('Disposable email addresses are not allowed.')
        
        # Check if email already exists
        from app.models import User
        existing = User.query.filter_by(email=email).first()
        if existing and form.user_id != existing.id:
            raise ValidationError('Email already registered.')
    
    @staticmethod
    def sanitize_text(text, allowed_tags=None):
        """Sanitize text to prevent XSS attacks."""
        if not text:
            return ""
        
        if allowed_tags is None:
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
        
        # Allow only specified tags
        cleaned = bleach.clean(
            text,
            tags=allowed_tags,
            attributes={'a': ['href', 'title']},
            strip=True
        )
        
        return cleaned
    
    @staticmethod
    def validate_project_name(form, field):
        """Validate project name."""
        name = field.data.strip() if field.data else ""
        
        if len(name) < 3:
            raise ValidationError('Project name must be at least 3 characters.')
        
        if len(name) > 255:
            raise ValidationError('Project name must not exceed 255 characters.')
        
        # Prevent HTML/JavaScript
        if any(char in name for char in '<>{}'):
            raise ValidationError('Project name contains invalid characters.')
    
    @staticmethod
    def validate_description(form, field):
        """Validate description field."""
        description = field.data
        
        if description and len(description) > 5000:
            raise ValidationError('Description must not exceed 5000 characters.')
    
    @staticmethod
    def validate_priority(form, field):
        """Validate priority field."""
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if field.data not in valid_priorities:
            raise ValidationError('Invalid priority value.')
    
    @staticmethod
    def validate_status(form, field):
        """Validate status field."""
        valid_statuses = ['pending', 'in_progress', 'completed', 'blocked', 'on_hold']
        if field.data not in valid_statuses:
            raise ValidationError('Invalid status value.')


# Form Classes

class LoginForm(FlaskForm):
    """User login form with validation."""
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=32, message='Username must be 3-32 characters')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=8, message='Password must be at least 8 characters')
        ]
    )


class RegisterForm(FlaskForm):
    """User registration form with validation."""
    username = StringField(
        'Username',
        validators=[DataRequired(), SecurityValidator.validate_username]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), SecurityValidator.validate_email]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), SecurityValidator.validate_password]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )
    
    user_id = None  # Used for validation context


class CreateProjectForm(FlaskForm):
    """Create project form."""
    name = StringField(
        'Project Name',
        validators=[DataRequired(), SecurityValidator.validate_project_name]
    )
    description = TextAreaField(
        'Description',
        validators=[Optional(), SecurityValidator.validate_description]
    )
    priority = SelectField(
        'Priority',
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        validators=[DataRequired()]
    )


class CreateIssueForm(FlaskForm):
    """Create issue form."""
    title = StringField(
        'Title',
        validators=[
            DataRequired(),
            Length(min=5, max=255, message='Title must be 5-255 characters')
        ]
    )
    description = TextAreaField(
        'Description',
        validators=[Optional(), SecurityValidator.validate_description]
    )
    priority = SelectField(
        'Priority',
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        validators=[DataRequired()]
    )
    status = SelectField(
        'Status',
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('blocked', 'Blocked'),
            ('on_hold', 'On Hold')
        ],
        validators=[DataRequired()]
    )


class ProgressUpdateForm(FlaskForm):
    """Progress update form."""
    title = StringField(
        'Update Title',
        validators=[
            DataRequired(),
            Length(min=5, max=255)
        ]
    )
    description = TextAreaField(
        'Update Details',
        validators=[
            DataRequired(),
            Length(min=10, max=5000)
        ]
    )
    percentage = IntegerField(
        'Progress %',
        validators=[
            DataRequired(),
            NumberRange(min=0, max=100, message='Progress must be between 0-100%')
        ]
    )


class ChangePasswordForm(FlaskForm):
    """Change password form."""
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired()]
    )
    new_password = PasswordField(
        'New Password',
        validators=[DataRequired(), SecurityValidator.validate_password]
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(),
            EqualTo('new_password', message='Passwords must match')
        ]
    )


class UpdateProfileForm(FlaskForm):
    """Update user profile form."""
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    first_name = StringField(
        'First Name',
        validators=[Optional(), Length(max=100)]
    )
    last_name = StringField(
        'Last Name',
        validators=[Optional(), Length(max=100)]
    )
    
    user_id = None  # Used for validation context


# Helper functions

def sanitize_input(input_data, max_length=5000, allowed_tags=None):
    """Sanitize user input to prevent XSS."""
    if not input_data:
        return ""
    
    # Trim length
    if len(input_data) > max_length:
        input_data = input_data[:max_length]
    
    # Sanitize HTML
    return SecurityValidator.sanitize_text(input_data, allowed_tags)


def validate_input_length(input_data, min_length=1, max_length=5000):
    """Validate input length."""
    if not input_data:
        return False
    
    length = len(input_data.strip())
    return min_length <= length <= max_length

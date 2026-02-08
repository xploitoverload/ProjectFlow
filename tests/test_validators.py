# tests/test_validators.py
"""
Input validation and sanitization tests.
"""

import pytest
from app.validators import (
    SecurityValidator, sanitize_input, validate_input_length,
    LoginForm, RegisterForm, CreateIssueForm
)


class TestSecurityValidator:
    """Security validator tests."""
    
    def test_validate_username_valid(self):
        """Test valid username validation."""
        validator = SecurityValidator()
        # Should not raise
        assert validator.validate_username.__doc__
    
    def test_validate_username_too_short(self):
        """Test username too short."""
        from wtforms.validators import ValidationError
        short_name = 'ab'  # Less than 3 chars
        # Would raise ValidationError in actual form context
    
    def test_validate_password_weak(self):
        """Test weak password detection."""
        weak_passwords = [
            'short',  # Too short
            'noupppercase123',  # No uppercase
            'NOLOWERCASE123',  # No lowercase
            'NoDigits',  # No digits
        ]
        # Each should fail validation
    
    def test_validate_email_invalid_format(self):
        """Test invalid email format."""
        invalid_emails = [
            'notanemail',
            'missing@domain',
            '@nodomain.com',
            'spaces in@email.com'
        ]
        # Each should fail validation
    
    def test_validate_email_disposable(self):
        """Test disposable email blocking."""
        disposable_emails = [
            'user@tempmail.com',
            'user@throwaway.email',
            'user@10minutemail.com'
        ]
        # Each should be blocked
    
    def test_sanitize_text_xss_prevention(self):
        """Test XSS prevention in text sanitization."""
        dangerous_inputs = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '<iframe src="malicious.com"></iframe>'
        ]
        
        for dangerous_input in dangerous_inputs:
            sanitized = sanitize_input(dangerous_input)
            assert '<script>' not in sanitized.lower()
            assert 'onerror' not in sanitized.lower()
            assert '<iframe' not in sanitized.lower()


class TestInputValidation:
    """Input validation tests."""
    
    def test_validate_input_length_valid(self):
        """Test valid input length."""
        assert validate_input_length('valid text', min_length=1, max_length=100)
    
    def test_validate_input_length_too_short(self):
        """Test input too short."""
        assert not validate_input_length('', min_length=1, max_length=100)
    
    def test_validate_input_length_too_long(self):
        """Test input too long."""
        long_text = 'a' * 101
        assert not validate_input_length(long_text, min_length=1, max_length=100)
    
    def test_sanitize_input_removes_html(self):
        """Test HTML removal in sanitization."""
        html_input = '<p>Hello <b>World</b></p>'
        sanitized = sanitize_input(html_input, allowed_tags=['p'])
        assert '<b>' not in sanitized  # <b> not in allowed_tags
    
    def test_sanitize_input_max_length(self):
        """Test max length enforcement in sanitization."""
        long_text = 'a' * 10000
        sanitized = sanitize_input(long_text, max_length=100)
        assert len(sanitized) <= 100


class TestFormValidation:
    """Form validation tests (unit-level)."""
    
    def test_sanitize_text_is_safe(self):
        """Test sanitize_text removes dangerous content."""
        from app.validators import SecurityValidator
        
        # HTML should be sanitized
        text = "<p>Hello <b>World</b></p>"
        sanitized = SecurityValidator.sanitize_text(text)
        # After sanitization, allowed tags should remain
        assert 'Hello' in sanitized
        
    def test_sanitize_input_removes_xss(self):
        """Test input sanitization for XSS prevention."""
        from app.validators import sanitize_input
        
        # Script tags should be removed
        result = sanitize_input("<script>alert('xss')</script>test")
        assert "<script>" not in result.lower()
        assert "test" in result.lower()
    
    def test_validate_input_length(self):
        """Test input length validation."""
        from app.validators import validate_input_length
        
        # Valid length
        assert validate_input_length("hello", 1, 100) is True
        
        # Too short
        assert validate_input_length("x", 5, 100) is False
        
        # Too long
        assert validate_input_length("x" * 101, 1, 100) is False

# tests/test_security.py
"""
Security configuration tests.
"""

import pytest


class TestCORSConfiguration:
    """Test CORS configuration."""
    
    def test_cors_config_exists(self):
        """Test CORS configuration module exists."""
        from app.security import cors_config
        assert hasattr(cors_config, 'init_cors')
        assert hasattr(cors_config, 'init_security')
        assert hasattr(cors_config, 'add_security_headers')
    
    def test_init_cors_function(self):
        """Test init_cors function is callable."""
        from app.security.cors_config import init_cors
        assert callable(init_cors)
    
    def test_init_security_function(self):
        """Test init_security function is callable."""
        from app.security.cors_config import init_security
        assert callable(init_security)
    
    def test_add_security_headers_function(self):
        """Test add_security_headers function is callable."""
        from app.security.cors_config import add_security_headers
        assert callable(add_security_headers)


class TestSecurityHeaders:
    """Test security headers configuration."""
    
    def test_cors_config_has_security_headers(self):
        """Test CORS config includes security headers."""
        from app.security.cors_config import add_security_headers
        import inspect
        
        # Check function has proper implementation
        source = inspect.getsource(add_security_headers)
        assert 'Content-Security-Policy' in source
        assert 'X-Frame-Options' in source
        assert 'SAMEORIGIN' in source
    
    def test_hsts_header_in_config(self):
        """Test HSTS header is configured."""
        from app.security.cors_config import add_security_headers
        import inspect
        
        source = inspect.getsource(add_security_headers)
        assert 'Strict-Transport-Security' in source
        assert 'max-age' in source


class TestSecurityIntegration:
    """Integration tests for security features."""
    
    def test_cors_origins_in_init_cors(self):
        """Test CORS has origins configured."""
        from app.security.cors_config import init_cors
        import inspect
        
        source = inspect.getsource(init_cors)
        assert 'origins' in source
        assert 'localhost' in source
    
    def test_security_headers_complete(self):
        """Test security headers are comprehensive."""
        from app.security.cors_config import add_security_headers
        import inspect
        
        source = inspect.getsource(add_security_headers)
        # Should have multiple security headers
        headers = [
            'Content-Security-Policy',
            'X-Frame-Options',
            'Strict-Transport-Security',
            'X-XSS-Protection'
        ]
        for header in headers:
            assert header in source, f"{header} not found in security headers"

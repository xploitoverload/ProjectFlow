# tests/test_auth.py
"""
Authentication tests - Login, Register, Password Reset
"""

import pytest
from app.models import User, db


class TestLogin:
    """Login endpoint tests."""
    
    def test_login_success(self, client, auth_user):
        """Test successful login."""
        response = client.post(
            '/login',
            data={'username': 'testuser', 'password': 'SecurePass123!'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'testuser' in response.data
    
    def test_login_invalid_username(self, client):
        """Test login with invalid username."""
        response = client.post(
            '/login',
            data={'username': 'nonexistent', 'password': 'password'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'error' in response.data.lower()
    
    def test_login_invalid_password(self, client, auth_user):
        """Test login with invalid password."""
        response = client.post(
            '/login',
            data={'username': 'testuser', 'password': 'WrongPassword123!'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'error' in response.data.lower()
    
    def test_login_rate_limiting(self, client):
        """Test rate limiting on login attempts."""
        for i in range(6):  # Try 6 times (limit is 5)
            response = client.post(
                '/login',
                data={'username': 'testuser', 'password': 'WrongPass'},
                follow_redirects=True
            )
            if i >= 5:
                assert response.status_code == 429  # Too Many Requests


class TestRegister:
    """Registration endpoint tests."""
    
    def test_register_success(self, client):
        """Test successful registration."""
        response = client.post(
            '/register',
            data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'SecurePass123!',
                'confirm_password': 'SecurePass123!'
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Verify user was created
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
    
    def test_register_duplicate_username(self, client, auth_user):
        """Test registration with existing username."""
        response = client.post(
            '/register',
            data={
                'username': 'testuser',
                'email': 'another@example.com',
                'password': 'SecurePass123!',
                'confirm_password': 'SecurePass123!'
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'taken' in response.data.lower() or b'exist' in response.data.lower()
    
    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post(
            '/register',
            data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': '123',  # Too short, no uppercase/lowercase
                'confirm_password': '123'
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'password' in response.data.lower()
    
    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords."""
        response = client.post(
            '/register',
            data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'SecurePass123!',
                'confirm_password': 'DifferentPass123!'
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'match' in response.data.lower()


class TestLogout:
    """Logout endpoint tests."""
    
    def test_logout_success(self, client, auth_user):
        """Test successful logout."""
        # Login first
        client.post(
            '/login',
            data={'username': 'testuser', 'password': 'SecurePass123!'}
        )
        
        # Logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

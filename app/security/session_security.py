# app/security/session_security.py
"""
Session Security Module
Secure session management, invalidation, and fresh authentication.
"""

from functools import wraps
from flask import session, request, abort, flash, redirect, url_for, g, current_app
from datetime import datetime, timedelta
from typing import Optional, Callable
import secrets
import hashlib
import logging

security_logger = logging.getLogger('security')

# Session storage for invalidation tracking (use Redis in production)
_session_tokens: dict = {}
_invalidated_sessions: set = set()


class SessionManager:
    """Secure session management."""
    
    # Session timeout in minutes
    DEFAULT_TIMEOUT = 30
    EXTENDED_TIMEOUT = 120  # For "remember me"
    FRESH_AUTH_TIMEOUT = 5  # Minutes before requiring re-auth for sensitive actions
    
    @staticmethod
    def create_session(user_id: int, role: str, username: str,
                       remember: bool = False, team_id: Optional[int] = None) -> str:
        """
        Create a new secure session.
        
        Returns:
            Session token for tracking
        """
        # Generate secure session token
        session_token = secrets.token_urlsafe(32)
        
        # Clear any existing session data
        session.clear()
        
        # Set session data
        session['user_id'] = user_id
        session['role'] = role
        session['username'] = username
        session['team_id'] = team_id
        session['session_token'] = session_token
        session['created_at'] = datetime.utcnow().isoformat()
        session['last_activity'] = datetime.utcnow().isoformat()
        session['fresh_auth_at'] = datetime.utcnow().isoformat()
        session['ip_address'] = _get_client_ip()
        session['user_agent'] = request.headers.get('User-Agent', '')[:200]
        session['remember'] = remember
        
        # Store token for tracking
        _session_tokens[session_token] = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'ip': _get_client_ip()
        }
        
        # Make session permanent if remember
        if remember:
            session.permanent = True
        
        security_logger.info(f"Session created for user {user_id}")
        
        return session_token
    
    @staticmethod
    def validate_session() -> tuple[bool, Optional[str]]:
        """
        Validate current session.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if 'user_id' not in session:
            return False, "No active session"
        
        # Check if session was invalidated
        session_token = session.get('session_token')
        if session_token in _invalidated_sessions:
            session.clear()
            return False, "Session has been invalidated"
        
        # Check session timeout
        last_activity = session.get('last_activity')
        if last_activity:
            try:
                last_time = datetime.fromisoformat(last_activity)
                timeout = SessionManager.EXTENDED_TIMEOUT if session.get('remember') else SessionManager.DEFAULT_TIMEOUT
                
                if last_time < datetime.utcnow() - timedelta(minutes=timeout):
                    SessionManager.destroy_session()
                    return False, "Session expired"
            except (ValueError, TypeError):
                SessionManager.destroy_session()
                return False, "Invalid session"
        
        # Verify session binding (IP + User-Agent)
        if current_app.config.get('SESSION_BINDING_ENABLED', True):
            stored_ip = session.get('ip_address')
            current_ip = _get_client_ip()
            
            # Allow some IP variation (e.g., mobile networks)
            if stored_ip and stored_ip.split('.')[:2] != current_ip.split('.')[:2]:
                security_logger.warning(
                    f"Session IP mismatch: stored={stored_ip}, current={current_ip}"
                )
                # Don't invalidate immediately, but log it
        
        # Update last activity
        session['last_activity'] = datetime.utcnow().isoformat()
        
        return True, None
    
    @staticmethod
    def destroy_session() -> None:
        """Destroy current session."""
        session_token = session.get('session_token')
        if session_token:
            _invalidated_sessions.add(session_token)
            if session_token in _session_tokens:
                del _session_tokens[session_token]
        
        user_id = session.get('user_id')
        session.clear()
        
        if user_id:
            security_logger.info(f"Session destroyed for user {user_id}")
    
    @staticmethod
    def invalidate_all_user_sessions(user_id: int) -> int:
        """
        Invalidate all sessions for a user.
        Used on password change, account lock, etc.
        
        Returns:
            Number of sessions invalidated
        """
        count = 0
        tokens_to_remove = []
        
        for token, data in _session_tokens.items():
            if data.get('user_id') == user_id:
                _invalidated_sessions.add(token)
                tokens_to_remove.append(token)
                count += 1
        
        for token in tokens_to_remove:
            del _session_tokens[token]
        
        security_logger.info(f"Invalidated {count} sessions for user {user_id}")
        
        return count
    
    @staticmethod
    def is_fresh_auth() -> bool:
        """Check if session has fresh authentication (for sensitive actions)."""
        fresh_auth_at = session.get('fresh_auth_at')
        if not fresh_auth_at:
            return False
        
        try:
            auth_time = datetime.fromisoformat(fresh_auth_at)
            return auth_time > datetime.utcnow() - timedelta(minutes=SessionManager.FRESH_AUTH_TIMEOUT)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def refresh_auth() -> None:
        """Mark session as freshly authenticated."""
        session['fresh_auth_at'] = datetime.utcnow().isoformat()
    
    @staticmethod
    def get_active_sessions(user_id: int) -> list:
        """Get list of active sessions for a user."""
        sessions = []
        
        for token, data in _session_tokens.items():
            if data.get('user_id') == user_id and token not in _invalidated_sessions:
                sessions.append({
                    'created_at': data.get('created_at'),
                    'ip': data.get('ip'),
                    'is_current': token == session.get('session_token')
                })
        
        return sessions


def _get_client_ip() -> str:
    """Get client IP address."""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        return request.environ['HTTP_X_REAL_IP']
    return request.environ.get('REMOTE_ADDR', '127.0.0.1')


def regenerate_session() -> None:
    """
    Regenerate session ID to prevent session fixation.
    Call this after login and privilege changes.
    """
    # Store session data
    data = dict(session)
    
    # Clear session
    session.clear()
    
    # Generate new session token
    data['session_token'] = secrets.token_urlsafe(32)
    data['last_activity'] = datetime.utcnow().isoformat()
    
    # Restore data
    for key, value in data.items():
        session[key] = value
    
    # Track new token
    if 'user_id' in data:
        _session_tokens[data['session_token']] = {
            'user_id': data['user_id'],
            'created_at': datetime.utcnow(),
            'ip': _get_client_ip()
        }


def invalidate_all_sessions(user_id: int) -> int:
    """Convenience function to invalidate all user sessions."""
    return SessionManager.invalidate_all_user_sessions(user_id)


def require_fresh_auth(f: Callable) -> Callable:
    """
    Decorator to require fresh authentication for sensitive actions.
    Redirects to re-authentication if session is not fresh.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not SessionManager.is_fresh_auth():
            flash('Please confirm your password to continue', 'warning')
            next_url = request.url
            return redirect(url_for('auth.confirm_password', next=next_url))
        return f(*args, **kwargs)
    return decorated_function


def require_valid_session(f: Callable) -> Callable:
    """
    Decorator to validate session on each request.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, message = SessionManager.validate_session()
        
        if not is_valid:
            flash(message or 'Please log in to continue', 'warning')
            next_url = request.url
            return redirect(url_for('auth.login', next=next_url))
        
        return f(*args, **kwargs)
    return decorated_function

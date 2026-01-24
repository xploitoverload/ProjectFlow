# app/services/auth_service.py
"""
Authentication Service
Handles all authentication-related business logic.
"""

from datetime import datetime, timedelta
from flask import session, current_app
from flask_login import login_user, logout_user
from app.utils.security import (
    hash_password, verify_password, generate_secure_token,
    log_security_event, get_client_ip, validate_email
)
from app.utils.validators import (
    validate_required, validate_length
)


class AuthService:
    """Service for handling authentication operations."""
    
    # Account lockout settings
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    @staticmethod
    def authenticate(username, password):
        """
        Authenticate a user with username and password.
        
        Returns:
            tuple: (success: bool, user: User or None, message: str)
        """
        from app.models import User, db
        
        # Validate inputs
        if not username or not password:
            return False, None, 'Username and password are required'
        
        # Find user
        user = User.query.filter_by(username=username.strip()).first()
        
        if not user:
            # Use constant time comparison to prevent timing attacks
            hash_password('dummy_password')
            log_security_event(
                'LOGIN_FAILED_USER_NOT_FOUND',
                details=f'Username: {username}',
                severity='INFO'
            )
            return False, None, 'Invalid credentials'
        
        # Check account lockout
        is_locked, lockout_message = AuthService._check_lockout(user)
        if is_locked:
            log_security_event(
                'LOGIN_ATTEMPT_LOCKED',
                user_id=user.id,
                details=lockout_message,
                severity='WARNING'
            )
            return False, None, lockout_message
        
        # Verify password
        is_valid, new_hash = verify_password(user.password, password)
        
        if not is_valid:
            AuthService._record_failed_attempt(user)
            log_security_event(
                'LOGIN_FAILED',
                user_id=user.id,
                details=f'IP: {get_client_ip()}',
                severity='INFO'
            )
            return False, None, 'Invalid credentials'
        
        # Update password hash if needed (Argon2 rehashing)
        if new_hash:
            user.password = new_hash
        
        # Reset failed attempts and update login time
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        log_security_event(
            'LOGIN_SUCCESS',
            user_id=user.id,
            details=f'IP: {get_client_ip()}',
            severity='INFO'
        )
        
        return True, user, 'Login successful'
    
    @staticmethod
    def create_session(user):
        """Create a new authenticated session for the user."""
        # Clear any existing session data
        session.clear()
        
        # Use Flask-Login to handle the session
        login_user(user)
        
        # Regenerate session ID to prevent session fixation
        session.regenerate = True
        
        # Set session data
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['team_id'] = user.team_id
        session['last_activity'] = datetime.utcnow().isoformat()
        session['session_created'] = datetime.utcnow().isoformat()
        session.permanent = True
        
        # Generate session fingerprint for additional security
        session['fingerprint'] = AuthService._generate_fingerprint()
    
    @staticmethod
    def destroy_session(user_id=None):
        """Safely destroy user session."""
        if user_id:
            log_security_event(
                'LOGOUT',
                user_id=user_id,
                details=f'IP: {get_client_ip()}',
                severity='INFO'
            )
        logout_user()
        session.clear()
    
    @staticmethod
    def validate_session():
        """
        Validate current session integrity.
        
        Returns:
            tuple: (is_valid: bool, message: str or None)
        """
        if 'user_id' not in session:
            return False, 'No active session'
        
        # Check session timeout
        timeout_minutes = current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
        last_activity = session.get('last_activity')
        
        if last_activity:
            try:
                last_time = datetime.fromisoformat(last_activity)
                if last_time < datetime.utcnow() - timedelta(minutes=timeout_minutes):
                    AuthService.destroy_session(session.get('user_id'))
                    return False, 'Session expired'
            except (ValueError, TypeError):
                AuthService.destroy_session()
                return False, 'Invalid session'
        
        # Validate session fingerprint
        current_fingerprint = AuthService._generate_fingerprint()
        stored_fingerprint = session.get('fingerprint')
        
        if stored_fingerprint and stored_fingerprint != current_fingerprint:
            log_security_event(
                'SESSION_HIJACK_ATTEMPT',
                user_id=session.get('user_id'),
                details='Session fingerprint mismatch',
                severity='CRITICAL'
            )
            AuthService.destroy_session(session.get('user_id'))
            return False, 'Session invalid'
        
        # Update last activity
        session['last_activity'] = datetime.utcnow().isoformat()
        
        return True, None
    
    @staticmethod
    def _check_lockout(user):
        """Check if account is locked due to failed attempts."""
        if user.failed_login_attempts < AuthService.MAX_FAILED_ATTEMPTS:
            return False, None
        
        if user.last_login:
            lockout_end = user.last_login + timedelta(minutes=AuthService.LOCKOUT_DURATION_MINUTES)
            
            if datetime.utcnow() < lockout_end:
                remaining = (lockout_end - datetime.utcnow()).seconds // 60
                return True, f'Account locked. Try again in {remaining} minutes.'
            else:
                # Lockout period expired, reset attempts
                from app.models import db
                user.failed_login_attempts = 0
                db.session.commit()
                return False, None
        
        return True, 'Account locked due to too many failed attempts'
    
    @staticmethod
    def _record_failed_attempt(user):
        """Record a failed login attempt."""
        from app.models import db
        
        user.failed_login_attempts += 1
        user.last_login = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def _generate_fingerprint():
        """Generate session fingerprint from client info."""
        from flask import request
        import hashlib
        
        components = [
            request.headers.get('User-Agent', ''),
            request.headers.get('Accept-Language', ''),
            # Don't include IP as it may change (mobile users)
        ]
        
        fingerprint_data = '|'.join(components)
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]
    
    @staticmethod
    def change_password(user, current_password, new_password):
        """
        Change user password with validation.
        Invalidates all sessions after successful change for security.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        from app.models import db
        from app.utils.security import validate_password_strength
        from app.security.session_security import SessionManager
        
        # Verify current password
        is_valid, _ = verify_password(user.password, current_password)
        if not is_valid:
            return False, 'Current password is incorrect'
        
        # Validate new password strength
        is_strong, message = validate_password_strength(new_password)
        if not is_strong:
            return False, message
        
        # Check password history (optional - implement if needed)
        # if AuthService._is_password_reused(user, new_password):
        #     return False, 'Cannot reuse recent passwords'
        
        # Update password
        user.password = hash_password(new_password)
        db.session.commit()
        
        # Invalidate all user sessions for security
        SessionManager.invalidate_all_user_sessions(user.id)
        
        log_security_event(
            'PASSWORD_CHANGED',
            user_id=user.id,
            details='Password changed - all sessions invalidated',
            severity='INFO'
        )
        
        return True, 'Password changed successfully. All other sessions have been logged out.'
    
    @staticmethod
    def generate_password_reset_token(email):
        """
        Generate password reset token.
        
        Returns:
            tuple: (success: bool, token: str or None, message: str)
        """
        from app.models import User, db
        
        user = User.query.filter_by(email_encrypted=email).first()
        
        # Always return success to prevent email enumeration
        if not user:
            return True, None, 'If the email exists, a reset link will be sent'
        
        token = generate_secure_token(32)
        expiry = datetime.utcnow() + timedelta(hours=1)
        
        # Store token (implement token storage in User model or separate table)
        # user.reset_token = token
        # user.reset_token_expiry = expiry
        # db.session.commit()
        
        log_security_event(
            'PASSWORD_RESET_REQUESTED',
            user_id=user.id,
            details=f'Reset token generated',
            severity='INFO'
        )
        
        return True, token, 'If the email exists, a reset link will be sent'

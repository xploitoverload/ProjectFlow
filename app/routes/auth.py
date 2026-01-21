# app/routes/auth.py
"""
Authentication Routes
Handles login, logout, and session management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from app.services import AuthService
from app.utils.security import (
    validate_csrf_token, get_client_ip, log_security_event,
    validate_username, rate_limit
)
from app.middleware import login_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Note: CSRF validation is handled automatically by Flask-WTF
        
        # Rate limiting
        ip = get_client_ip()
        if not rate_limit(f'login:{ip}', max_requests=5, window_seconds=900):
            log_security_event(
                'RATE_LIMIT_EXCEEDED',
                details=f'Login rate limit exceeded for IP: {ip}',
                severity='WARNING'
            )
            flash('Too many login attempts. Please try again in 15 minutes.', 'error')
            return redirect(url_for('auth.login'))
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        # Basic input validation
        if not validate_username(username):
            flash('Invalid username format', 'error')
            return redirect(url_for('auth.login'))
        
        # Authenticate
        success, user, message = AuthService.authenticate(username, password)
        
        if success:
            # Create session
            AuthService.create_session(user)
            
            # Handle "remember me"
            if remember:
                session.permanent = True
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next URL or dashboard
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('main.dashboard'))
        else:
            flash(message, 'error')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Handle user logout."""
    user_id = session.get('user_id')
    AuthService.destroy_session(user_id)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset request."""
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        email = request.form.get('email', '').strip()
        
        # Generate reset token
        success, token, message = AuthService.generate_password_reset_token(email)
        
        # Always show same message to prevent email enumeration
        flash('If the email exists in our system, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Handle password change for logged-in users."""
    from app.models import User
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('auth.change_password'))
        
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('auth.change_password'))
        
        user = User.query.get(session['user_id'])
        success, message = AuthService.change_password(user, current_password, new_password)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash(message, 'error')
            return redirect(url_for('auth.change_password'))
    
    return render_template('change_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    from app.models import User, db
    from app.utils.security import hash_password, validate_password_strength
    
    # Find user with valid token
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.now():
        flash('Invalid or expired reset link. Please request a new one.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        # Validate password strength
        is_strong, message = validate_password_strength(new_password)
        if not is_strong:
            flash(message, 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        # Update password and clear token
        user.password = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        user.failed_login_attempts = 0
        db.session.commit()
        
        log_security_event(
            'PASSWORD_RESET_COMPLETED',
            user_id=user.id,
            details='Password reset via token',
            severity='INFO'
        )
        
        flash('Password reset successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', token=token)


@auth_bp.route('/confirm-password', methods=['GET', 'POST'])
@login_required
def confirm_password():
    """Re-authenticate for sensitive actions."""
    from app.models import User
    from app.security.session_security import SessionManager
    from app.security.validation import get_safe_redirect_url
    
    next_url = request.args.get('next', url_for('main.dashboard'))
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'error')
            return redirect(url_for('auth.confirm_password', next=next_url))
        
        password = request.form.get('password', '')
        
        user = User.query.get(session['user_id'])
        if not user:
            flash('Session error. Please log in again.', 'error')
            return redirect(url_for('auth.login'))
        
        if user.check_password(password):
            # Refresh authentication timestamp
            SessionManager.refresh_auth()
            log_security_event(
                'PASSWORD_CONFIRMED',
                user_id=user.id,
                details='Re-authentication for sensitive action',
                severity='INFO'
            )
            
            # Redirect to safe URL only
            safe_url = get_safe_redirect_url(next_url, url_for('main.dashboard'))
            return redirect(safe_url)
        else:
            log_security_event(
                'PASSWORD_CONFIRM_FAILED',
                user_id=user.id,
                details='Failed re-authentication attempt',
                severity='WARNING'
            )
            flash('Incorrect password.', 'error')
            return redirect(url_for('auth.confirm_password', next=next_url))
    
    return render_template('confirm_password.html', next_url=next_url)

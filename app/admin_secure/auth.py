"""
Secure Admin System
Hidden admin panel with dynamic URLs, 2FA, and comprehensive audit logging
"""

import os
import secrets
import base64
from datetime import datetime, timedelta
from typing import Optional, Tuple
from functools import wraps
from io import BytesIO

from flask import (
    Blueprint, render_template, request, redirect, url_for, 
    flash, session, abort, jsonify, current_app
)
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from models import db, User

import logging
logger = logging.getLogger(__name__)

# Lazy imports for heavy dependencies
def _get_pyotp():
    """Lazy import pyotp to avoid slow startup"""
    global _pyotp_module
    if '_pyotp_module' not in globals():
        import pyotp
        _pyotp_module = pyotp
    return _pyotp_module

def _get_qrcode():
    """Lazy import qrcode to avoid slow startup"""
    global _qrcode_module
    if '_qrcode_module' not in globals():
        import qrcode
        _qrcode_module = qrcode
    return _qrcode_module


class AdminSecurityModel(db.Model):
    """Model for storing admin security settings"""
    
    __tablename__ = 'admin_security'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 2FA Settings
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))  # Encrypted TOTP secret
    mfa_backup_codes = Column(JSON)   # Encrypted backup codes
    
    # IP Whitelist
    ip_whitelist = Column(JSON, default=list)
    ip_whitelist_enabled = Column(Boolean, default=True)
    
    # Session Management
    allowed_ips = Column(JSON, default=list)
    session_timeout_minutes = Column(Integer, default=15)
    max_concurrent_sessions = Column(Integer, default=1)
    
    # Audit
    last_login = Column(DateTime)
    last_login_ip = Column(String(45))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminAuditLog(db.Model):
    """Audit log for all admin actions"""
    
    __tablename__ = 'admin_audit_log'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    
    details = Column(JSON)
    status = Column(String(50))  # success, failure, denied
    reason = Column(Text)
    
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class SecureAdminManager:
    """Manages secure admin authentication and authorization"""
    
    def __init__(self):
        self.hidden_route_tokens = {}
        self.admin_session_tokens = {}
    
    def generate_hidden_admin_url(self, user_id: int) -> str:
        """Generate unique hidden admin URL for user session"""
        
        token = secrets.token_urlsafe(32)
        self.hidden_route_tokens[token] = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=8),
            'used': False
        }
        
        logger.info(f"Generated hidden admin URL for user {user_id}")
        return token
    
    def validate_hidden_url(self, token: str) -> Optional[int]:
        """Validate hidden admin URL token"""
        
        token_data = self.hidden_route_tokens.get(token)
        
        if not token_data:
            logger.warning(f"Invalid hidden admin URL token attempted")
            return None
        
        if datetime.utcnow() > token_data['expires_at']:
            logger.warning(f"Hidden admin URL token expired for user {token_data['user_id']}")
            del self.hidden_route_tokens[token]
            return None
        
        return token_data['user_id']
    
    def setup_2fa_for_user(self, user_id: int) -> Tuple[str, str]:
        """
        Setup 2FA for admin user
        Returns: (secret_key, QR_code_image_base64)
        """
        
        admin_sec = AdminSecurityModel.query.filter_by(user_id=user_id).first()
        if not admin_sec:
            admin_sec = AdminSecurityModel(user_id=user_id)
            db.session.add(admin_sec)
        
        # Generate TOTP secret
        pyotp = _get_pyotp()
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # Generate QR code
        provisioning_uri = totp.provisioning_uri(
            name=f"Admin-{user_id}",
            issuer_name='ProjectMgmt-Admin'
        )
        
        qrcode = _get_qrcode()
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Store encrypted secret
        admin_sec.mfa_secret = secret  # Should be encrypted in production
        admin_sec.mfa_enabled = False  # Requires verification
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4) for _ in range(10)]
        admin_sec.mfa_backup_codes = backup_codes
        
        db.session.commit()
        
        logger.info(f"2FA setup initiated for user {user_id}")
        return secret, f"data:image/png;base64,{qr_code_b64}"
    
    def verify_2fa_token(self, user_id: int, token: str) -> bool:
        """Verify 2FA TOTP token"""
        
        admin_sec = AdminSecurityModel.query.filter_by(user_id=user_id).first()
        if not admin_sec or not admin_sec.mfa_secret:
            return False
        
        pyotp = _get_pyotp()
        totp = pyotp.TOTP(admin_sec.mfa_secret)
        
        # Allow 30-second window on either side
        return totp.verify(token, valid_window=1)
    
    def verify_backup_code(self, user_id: int, code: str) -> bool:
        """Verify backup code (single use)"""
        
        admin_sec = AdminSecurityModel.query.filter_by(user_id=user_id).first()
        if not admin_sec or not admin_sec.mfa_backup_codes:
            return False
        
        if code in admin_sec.mfa_backup_codes:
            # Remove used backup code
            admin_sec.mfa_backup_codes.remove(code)
            db.session.commit()
            
            logger.info(f"Backup code used for user {user_id}")
            return True
        
        return False
    
    def set_ip_whitelist(self, user_id: int, ips: list) -> bool:
        """Set IP whitelist for admin user"""
        
        admin_sec = AdminSecurityModel.query.filter_by(user_id=user_id).first()
        if not admin_sec:
            admin_sec = AdminSecurityModel(user_id=user_id)
            db.session.add(admin_sec)
        
        admin_sec.ip_whitelist = ips
        admin_sec.ip_whitelist_enabled = True
        db.session.commit()
        
        logger.info(f"IP whitelist updated for user {user_id}: {ips}")
        return True
    
    def validate_ip(self, user_id: int, ip_address: str) -> bool:
        """Validate if IP is whitelisted for admin user"""
        
        admin_sec = AdminSecurityModel.query.filter_by(user_id=user_id).first()
        
        if not admin_sec or not admin_sec.ip_whitelist_enabled:
            return True
        
        if not admin_sec.ip_whitelist:
            logger.warning(f"Admin {user_id} has no whitelisted IPs configured")
            return False
        
        if ip_address in admin_sec.ip_whitelist:
            return True
        
        logger.warning(f"Admin {user_id} attempted access from non-whitelisted IP: {ip_address}")
        return False
    
    def log_admin_action(
        self,
        admin_id: int,
        action: str,
        resource_type: str = None,
        resource_id: str = None,
        details: dict = None,
        status: str = 'success',
        reason: str = None
    ):
        """Log admin action to audit log"""
        
        log = AdminAuditLog(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            status=status,
            reason=reason,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        db.session.add(log)
        db.session.commit()
        
        logger.info(f"Admin action logged: {action} by user {admin_id}")
    
    def record_failed_login(self, user_id: int):
        """Record failed admin login attempt"""
        
        admin_sec = AdminSecurityModel.query.filter_by(user_id=user_id).first()
        if not admin_sec:
            admin_sec = AdminSecurityModel(user_id=user_id)
            db.session.add(admin_sec)
        
        admin_sec.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if admin_sec.failed_login_attempts >= 5:
            admin_sec.locked_until = datetime.utcnow() + timedelta(minutes=30)
            logger.warning(f"Admin account {user_id} locked due to failed login attempts")
        
        db.session.commit()
    
    def check_admin_lock(self, user_id: int) -> bool:
        """Check if admin account is locked"""
        
        admin_sec = AdminSecurityModel.query.filter_by(user_id=user_id).first()
        
        if not admin_sec or not admin_sec.locked_until:
            return False
        
        if datetime.utcnow() > admin_sec.locked_until:
            # Unlock account
            admin_sec.locked_until = None
            admin_sec.failed_login_attempts = 0
            db.session.commit()
            return False
        
        return True
    
    def record_successful_login(self, user_id: int):
        """Record successful admin login"""
        
        admin_sec = AdminSecurityModel.query.filter_by(user_id=user_id).first()
        if not admin_sec:
            admin_sec = AdminSecurityModel(user_id=user_id)
            db.session.add(admin_sec)
        
        admin_sec.last_login = datetime.utcnow()
        admin_sec.last_login_ip = request.remote_addr
        admin_sec.failed_login_attempts = 0
        admin_sec.locked_until = None
        
        db.session.commit()
        
        logger.info(f"Admin successful login: user {user_id} from {request.remote_addr}")


# Global instance
secure_admin = SecureAdminManager()


def require_admin_with_2fa(f):
    """Decorator for routes requiring admin role and 2FA verification"""
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import User
        
        # Check user is logged in
        if 'user_id' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('auth.login'))
        
        # Check user is admin
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'super_admin']:
            logger.warning(f"Non-admin user {session['user_id']} attempted admin access")
            abort(403)
        
        # Check IP whitelist
        ip_addr = request.remote_addr
        if not secure_admin.validate_ip(user.id, ip_addr):
            logger.warning(f"Admin {user.id} blocked: non-whitelisted IP {ip_addr}")
            abort(403)
        
        # Check 2FA if enabled
        admin_sec = AdminSecurityModel.query.filter_by(user_id=user.id).first()
        if admin_sec and admin_sec.mfa_enabled:
            if '2fa_verified' not in session or session['2fa_verified'] < datetime.utcnow().timestamp():
                return redirect(url_for('admin_secure.verify_2fa'))
        
        return f(*args, **kwargs)
    
    return decorated_function

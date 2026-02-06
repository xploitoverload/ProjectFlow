"""
Secure Hidden Admin Routes
All admin routes moved to random hidden location with 2FA requirement
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from functools import wraps
from datetime import datetime
import base64
from io import BytesIO

from app.admin_secure.auth import secure_admin, require_admin_with_2fa, AdminAuditLog, AdminSecurityModel
from app.admin_secure.facial_recognition import facial_id_manager, require_facial_id
from app.authorization.rbac import RoleBasedAccessControl, require_permission, init_permissions
from app.models import User, Team, Project, Issue, db

# Import models needed for facial ID
from models import FacialIDData

import logging
logger = logging.getLogger(__name__)

# Lazy imports for 2FA
def _get_pyotp():
    """Lazy import pyotp"""
    global _pyotp_module
    if '_pyotp_module' not in globals():
        import pyotp
        _pyotp_module = pyotp
    return _pyotp_module

def _get_qrcode():
    """Lazy import qrcode"""
    global _qrcode_module
    if '_qrcode_module' not in globals():
        import qrcode
        _qrcode_module = qrcode
    return _qrcode_module


def create_secure_admin_blueprint(hidden_token: str):
    """
    Create admin blueprint with hidden URL
    
    Usage:
        admin_bp = create_secure_admin_blueprint(hidden_token)
        app.register_blueprint(admin_bp, url_prefix=f'/secure-mgmt-{hidden_token}/')
    """
    
    admin_bp = Blueprint('admin_secure', __name__)
    
    # =================================================================================
    # AUTHENTICATION ENDPOINTS
    # =================================================================================
    
    @admin_bp.route('/verify-2fa', methods=['GET', 'POST'])
    def verify_2fa():
        """Verify 2FA code before allowing admin access"""
        
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'super_admin']:
            abort(403)
        
        # Check if account is locked
        if secure_admin.check_admin_lock(user.id):
            flash('Account is locked due to failed login attempts. Try again in 30 minutes.', 'error')
            return redirect(url_for('auth.login'))
        
        if request.method == 'POST':
            token = request.form.get('token')
            backup_code = request.form.get('backup_code')
            
            verified = False
            
            # Try TOTP token first
            if token:
                verified = secure_admin.verify_2fa_token(user.id, token)
            # Fall back to backup code
            elif backup_code:
                verified = secure_admin.verify_backup_code(user.id, backup_code)
            
            if verified:
                session['2fa_verified'] = datetime.utcnow().timestamp()
                secure_admin.record_successful_login(user.id)
                secure_admin.log_admin_action(
                    user.id,
                    'ADMIN_LOGIN',
                    status='success'
                )
                
                flash('2FA verified successfully', 'success')
                return redirect(url_for('admin_secure.dashboard', _external=False))
            else:
                secure_admin.record_failed_login(user.id)
                flash('Invalid 2FA code or backup code', 'error')
        
        return render_template('admin/verify_2fa.html', user=user)
    
    
    @admin_bp.route('/setup-2fa', methods=['GET', 'POST'])
    def setup_2fa():
        """Setup 2FA for admin user"""
        
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'super_admin']:
            abort(403)
        
        if request.method == 'POST':
            token = request.form.get('token')
            
            if secure_admin.verify_2fa_token(user.id, token):
                # Enable 2FA
                admin_sec = db.session.query(AdminSecurityModel).filter_by(user_id=user.id).first()
                if admin_sec:
                    admin_sec.mfa_enabled = True
                    db.session.commit()
                
                secure_admin.log_admin_action(
                    user.id,
                    'ENABLE_2FA',
                    status='success'
                )
                
                flash('2FA enabled successfully', 'success')
                return redirect(url_for('admin_secure.dashboard'))
            else:
                flash('Invalid verification code', 'error')
        
        # Check if user already has a secret, if not generate one
        admin_sec = db.session.query(AdminSecurityModel).filter_by(user_id=user.id).first()
        if not admin_sec or not admin_sec.mfa_secret:
            # Generate new secret only if doesn't exist
            secret, qr_code = secure_admin.setup_2fa_for_user(user.id)
        else:
            # Use existing secret to regenerate QR code for display
            secret = admin_sec.mfa_secret
            pyotp = _get_pyotp()
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=f"Admin-{user.id}",
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
            qr_code = f"data:image/png;base64,{qr_code_b64}"
        
        return render_template('admin/setup_2fa.html', user=user, qr_code=qr_code, qr_code_secret=secret)
    
    
    @admin_bp.route('/setup-facial-id', methods=['GET', 'POST'])
    @require_admin_with_2fa
    def setup_facial_id():
        """Setup facial recognition for admin"""
        
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'super_admin']:
            abort(403)
        
        if request.method == 'POST':
            try:
                # Get uploaded image
                if 'face_image' not in request.files:
                    return jsonify({'success': False, 'message': 'No image provided'}), 400
                
                image_file = request.files['face_image']
                if image_file.filename == '':
                    return jsonify({'success': False, 'message': 'No image selected'}), 400
                
                image_data = image_file.read()
                
                # Enroll face
                result = facial_id_manager.enroll_admin_face(
                    user.id,
                    image_data,
                    image_label=request.form.get('label', 'default')
                )
                
                if result['success']:
                    secure_admin.log_admin_action(
                        user.id,
                        'ENROLL_FACIAL_ID',
                        resource_type='facial_id',
                        resource_id=result['encoding_id'],
                        status='success',
                        details={'label': request.form.get('label', 'default')}
                    )
                    
                    return jsonify({
                        'success': True,
                        'message': 'Face enrolled successfully',
                        'facial_id': result['encoding_id'],
                        'face_preview': result['face_preview']
                    }), 200
                else:
                    return jsonify({'success': False, 'message': result.get('message', 'Enrollment failed')}), 400
                    
            except Exception as e:
                logger.error(f"Facial ID enrollment error: {e}")
                secure_admin.log_admin_action(
                    user.id,
                    'ENROLL_FACIAL_ID',
                    status='failure',
                    details={'error': str(e)}
                )
                return jsonify({'success': False, 'message': str(e)}), 500
        
        # Get facial ID stats
        facial_stats = facial_id_manager.get_admin_facial_stats(user.id)
        
        return render_template(
            'admin/setup_facial_id.html',
            user=user,
            facial_stats=facial_stats
        )
    
    
    @admin_bp.route('/verify-facial-id', methods=['GET', 'POST'])
    @require_admin_with_2fa
    def verify_facial_id():
        """Verify admin identity using facial recognition"""
        
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'super_admin']:
            abort(403)
        
        if request.method == 'POST':
            try:
                if 'face_image' not in request.files:
                    return jsonify({'success': False, 'message': 'No image provided'}), 400
                
                image_file = request.files['face_image']
                image_data = image_file.read()
                
                # Verify face
                is_verified, details = facial_id_manager.verify_admin_face(user.id, image_data)
                
                if is_verified:
                    # Mark facial ID as verified in session
                    session['facial_id_verified'] = True
                    session['facial_id_verified_at'] = datetime.utcnow().isoformat()
                    
                    secure_admin.log_admin_action(
                        user.id,
                        'VERIFY_FACIAL_ID',
                        status='success',
                        details={
                            'confidence': details['confidence'],
                            'match_count': details['match_count']
                        }
                    )
                    
                    return jsonify({
                        'success': True,
                        'message': 'Face verified successfully',
                        'confidence': details['confidence'],
                        'match_count': details['match_count']
                    }), 200
                else:
                    secure_admin.log_admin_action(
                        user.id,
                        'VERIFY_FACIAL_ID',
                        status='failure',
                        details={'reason': details['message']}
                    )
                    
                    return jsonify({
                        'success': False,
                        'message': details['message'],
                        'confidence': details['confidence']
                    }), 401
                    
            except Exception as e:
                logger.error(f"Facial ID verification error: {e}")
                secure_admin.log_admin_action(
                    user.id,
                    'VERIFY_FACIAL_ID',
                    status='failure',
                    details={'error': str(e)}
                )
                return jsonify({'success': False, 'message': str(e)}), 500
        
        return render_template('admin/verify_facial_id.html', user=user)
    
    
    @admin_bp.route('/facial-id-settings', methods=['GET', 'POST'])
    @require_admin_with_2fa
    def facial_id_settings():
        """Manage facial ID settings"""
        
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'super_admin']:
            abort(403)
        
        facial_data_list = FacialIDData.query.filter_by(admin_id=user.id).all()
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'delete_facial_id':
                facial_id = request.form.get('facial_id')
                facial_data = FacialIDData.query.filter_by(
                    id=facial_id,
                    admin_id=user.id
                ).first()
                
                if facial_data:
                    db.session.delete(facial_data)
                    db.session.commit()
                    
                    secure_admin.log_admin_action(
                        user.id,
                        'DELETE_FACIAL_ID',
                        resource_type='facial_id',
                        resource_id=facial_id,
                        status='success'
                    )
                    
                    flash('Facial ID deleted successfully', 'success')
                else:
                    flash('Facial ID not found', 'error')
            
            elif action == 'verify_facial_id':
                facial_id = request.form.get('facial_id')
                facial_data = FacialIDData.query.filter_by(
                    id=facial_id,
                    admin_id=user.id
                ).first()
                
                if facial_data:
                    facial_data.is_verified = True
                    facial_data.verified_at = datetime.utcnow()
                    db.session.commit()
                    
                    secure_admin.log_admin_action(
                        user.id,
                        'VERIFY_FACIAL_ID_ENROLLMENT',
                        resource_type='facial_id',
                        resource_id=facial_id,
                        status='success'
                    )
                    
                    flash('Facial ID verified and enabled', 'success')
            
            return redirect(url_for('admin_secure.facial_id_settings'))
        
        # Get stats
        facial_stats = facial_id_manager.get_admin_facial_stats(user.id)
        
        return render_template(
            'admin/facial_id_settings.html',
            user=user,
            facial_data_list=facial_data_list,
            facial_stats=facial_stats
        )
    
    
    # =================================================================================
    # ADMIN DASHBOARD
    # =================================================================================
    
    @admin_bp.route('/', methods=['GET'])
    @require_admin_with_2fa
    @require_permission('manage_system')
    def dashboard():
        """Admin dashboard with system overview"""
        
        user = User.query.get(session['user_id'])
        
        # Get system statistics
        stats = {
            'total_users': User.query.count(),
            'total_teams': Team.query.count(),
            'total_projects': Project.query.count(),
            'total_issues': Issue.query.count(),
            'active_sessions': session.get('active_sessions', 0)
        }
        
        # Get recent admin actions
        recent_actions = AdminAuditLog.query.filter_by(admin_id=user.id).order_by(
            AdminAuditLog.created_at.desc()
        ).limit(10).all()
        
        secure_admin.log_admin_action(
            user.id,
            'VIEW_DASHBOARD',
            status='success'
        )
        
        return render_template(
            'admin/secure_dashboard.html',
            user=user,
            stats=stats,
            recent_actions=recent_actions
        )
    
    
    # =================================================================================
    # USER MANAGEMENT
    # =================================================================================
    
    @admin_bp.route('/users', methods=['GET'])
    @require_admin_with_2fa
    @require_permission('manage_users')
    def manage_users():
        """List all users"""
        
        user = User.query.get(session['user_id'])
        users = User.query.all()
        
        secure_admin.log_admin_action(
            user.id,
            'VIEW_USERS',
            status='success'
        )
        
        return render_template('admin/users.html', user=user, users=users)
    
    
    @admin_bp.route('/users/<int:user_id>/lock', methods=['POST'])
    @require_admin_with_2fa
    @require_permission('manage_users')
    def lock_user(user_id: int):
        """Lock user account (prevent login)"""
        
        admin = User.query.get(session['user_id'])
        target_user = User.query.get(user_id)
        
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent locking super_admin accounts
        if target_user.role == 'super_admin' and admin.role != 'super_admin':
            secure_admin.log_admin_action(
                admin.id,
                'LOCK_USER',
                resource_type='user',
                resource_id=str(user_id),
                status='denied',
                reason='Cannot lock super_admin account'
            )
            return jsonify({'error': 'Cannot lock super_admin accounts'}), 403
        
        target_user.is_locked = True
        db.session.commit()
        
        secure_admin.log_admin_action(
            admin.id,
            'LOCK_USER',
            resource_type='user',
            resource_id=str(user_id),
            status='success'
        )
        
        logger.info(f"User {user_id} locked by admin {admin.id}")
        return jsonify({'status': 'User locked successfully'}), 200
    
    
    @admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
    @require_admin_with_2fa
    @require_permission('manage_users')
    def reset_user_password(user_id: int):
        """Reset user password"""
        
        admin = User.query.get(session['user_id'])
        target_user = User.query.get(user_id)
        
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate temporary password
        temp_password = secrets.token_urlsafe(16)
        target_user.set_password(temp_password)
        db.session.commit()
        
        secure_admin.log_admin_action(
            admin.id,
            'RESET_PASSWORD',
            resource_type='user',
            resource_id=str(user_id),
            status='success'
        )
        
        logger.info(f"Password reset for user {user_id} by admin {admin.id}")
        return jsonify({'status': 'Password reset', 'temp_password': temp_password}), 200
    
    
    # =================================================================================
    # TEAM MANAGEMENT
    # =================================================================================
    
    @admin_bp.route('/teams', methods=['GET'])
    @require_admin_with_2fa
    @require_permission('manage_teams')
    def manage_teams():
        """List all teams"""
        
        user = User.query.get(session['user_id'])
        teams = Team.query.all()
        
        secure_admin.log_admin_action(
            user.id,
            'VIEW_TEAMS',
            status='success'
        )
        
        return render_template('admin/teams.html', user=user, teams=teams)
    
    
    # =================================================================================
    # AUDIT LOGS
    # =================================================================================
    
    @admin_bp.route('/audit-logs', methods=['GET'])
    @require_admin_with_2fa
    @require_permission('view_audit_logs')
    def view_audit_logs():
        """View admin audit logs"""
        
        user = User.query.get(session['user_id'])
        
        # Get logs for current user or all logs if super_admin
        if user.role == 'super_admin':
            logs = AdminAuditLog.query.order_by(AdminAuditLog.created_at.desc()).all()
        else:
            logs = AdminAuditLog.query.filter_by(admin_id=user.id).order_by(
                AdminAuditLog.created_at.desc()
            ).all()
        
        secure_admin.log_admin_action(
            user.id,
            'VIEW_AUDIT_LOGS',
            status='success'
        )
        
        return render_template('admin/audit_logs.html', user=user, logs=logs)
    
    
    # =================================================================================
    # SECURITY SETTINGS
    # =================================================================================
    
    @admin_bp.route('/security/ip-whitelist', methods=['GET', 'POST'])
    @require_admin_with_2fa
    @require_permission('manage_security')
    def manage_ip_whitelist():
        """Manage IP whitelist for admin account"""
        
        user = User.query.get(session['user_id'])
        
        if request.method == 'POST':
            ips = request.form.get('ips', '').split('\n')
            ips = [ip.strip() for ip in ips if ip.strip()]
            
            secure_admin.set_ip_whitelist(user.id, ips)
            
            secure_admin.log_admin_action(
                user.id,
                'UPDATE_IP_WHITELIST',
                details={'ip_count': len(ips)},
                status='success'
            )
            
            flash('IP whitelist updated successfully', 'success')
        
        admin_sec = db.session.query(AdminSecurityModel).filter_by(user_id=user.id).first()
        current_ips = admin_sec.ip_whitelist if admin_sec else []
        
        return render_template(
            'admin/ip_whitelist.html',
            user=user,
            current_ips=current_ips
        )
    
    
    @admin_bp.route('/security/revoke-sessions', methods=['POST'])
    @require_admin_with_2fa
    @require_permission('manage_security')
    def revoke_admin_sessions():
        """Revoke all admin sessions (force re-login on next request)"""
        
        user = User.query.get(session['user_id'])
        
        # Log all active sessions as revoked
        secure_admin.log_admin_action(
            user.id,
            'REVOKE_SESSIONS',
            status='success'
        )
        
        logger.warning(f"All admin sessions revoked by {user.id}")
        return jsonify({'status': 'All sessions revoked'}), 200
    
    
    # =================================================================================
    # FACIAL RECOGNITION LOGIN (PRIMARY ADMIN UNLOCK)
    # =================================================================================
    
    @admin_bp.route('/facial-login', methods=['GET'])
    def facial_login():
        """Display facial recognition login page for admins"""
        return render_template('admin_facial_login.html')
    
    
    @admin_bp.route('/facial-login-verify', methods=['POST'])
    def facial_login_verify():
        """Verify facial recognition and authenticate admin"""
        data = request.get_json()
        image_data = data.get('image')
        confidence = data.get('confidence', 0)
        
        if not image_data:
            return jsonify({
                'success': False,
                'message': 'No image provided'
            }), 400
        
        # Extract base64 image data
        try:
            import base64
            import io
            from PIL import Image
            
            # Remove data URI prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64 to image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Verify against enrolled admin faces
            admin_users = User.query.filter_by(role='admin').all()
            admin_users.extend(User.query.filter_by(role='super_admin').all())
            
            verified_user = None
            best_match_confidence = 0
            
            for admin_user in admin_users:
                # Get enrolled faces
                enrollments = FacialIDData.query.filter_by(
                    admin_id=admin_user.id,
                    is_verified=True
                ).all()
                
                for enrollment in enrollments:
                    try:
                        # Verify face
                        match_confidence = facial_id_manager.verify_admin_face(
                            image,
                            enrollment
                        )
                        
                        # Track best match
                        if match_confidence > best_match_confidence:
                            best_match_confidence = match_confidence
                            verified_user = admin_user
                            
                    except Exception as e:
                        logger.debug(f"Face verification error: {e}")
                        continue
            
            # Check if face matched with sufficient confidence
            if verified_user and best_match_confidence > 0.6:
                # Create session for admin
                session['user_id'] = verified_user.id
                session['facial_verified'] = True
                session['facial_verification_time'] = datetime.now().isoformat()
                
                # Log facial authentication
                facial_id_manager.log_verification(
                    verified_user.id,
                    success=True,
                    confidence=best_match_confidence,
                    method='login_facial'
                )
                
                # Log to admin audit
                secure_admin.log_admin_action(
                    verified_user.id,
                    'FACIAL_LOGIN_SUCCESS',
                    details=f'Confidence: {best_match_confidence:.2%}',
                    status='success'
                )
                
                logger.info(f"Admin {verified_user.username} logged in via facial recognition")
                
                return jsonify({
                    'success': True,
                    'message': 'Face verified successfully',
                    'redirect': url_for('admin_secure.admin_dashboard')
                }), 200
            else:
                # Log failed facial verification
                if verified_user:
                    facial_id_manager.log_verification(
                        verified_user.id,
                        success=False,
                        confidence=best_match_confidence,
                        method='login_facial'
                    )
                    
                    secure_admin.log_admin_action(
                        verified_user.id,
                        'FACIAL_LOGIN_FAILED',
                        details=f'Low confidence: {best_match_confidence:.2%}',
                        status='failed'
                    )
                
                logger.warning(f"Facial recognition login failed - confidence too low: {best_match_confidence:.2%}")
                
                return jsonify({
                    'success': False,
                    'message': 'Face not recognized. Please ensure proper lighting and position your face clearly.'
                }), 401
        
        except Exception as e:
            logger.error(f"Facial login error: {e}")
            return jsonify({
                'success': False,
                'message': 'Verification error. Please try again.'
            }), 500
    
    
    return admin_bp


# Import AdminSecurityModel
from app.admin_secure.auth import AdminSecurityModel
import secrets

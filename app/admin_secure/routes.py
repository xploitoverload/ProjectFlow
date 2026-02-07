"""
Secure Hidden Admin Routes
All admin routes moved to random hidden location with 2FA requirement
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import login_user
from functools import wraps
from datetime import datetime
import base64
from io import BytesIO

from app.admin_secure.auth import secure_admin, require_admin_with_2fa, AdminAuditLog, AdminSecurityModel
from app.admin_secure.facial_recognition import facial_id_manager, require_facial_id
from app.authorization.rbac import RoleBasedAccessControl, require_permission, init_permissions
from app.models import User, Team, Project, Issue, db
from app import csrf

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
                return redirect(url_for('admin_secure.setup_facial_id', _external=False))
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
            token = request.form.get('token', '').strip()
            print(f"DEBUG ROUTE: POST request received with token='{token}' length={len(token)}")
            
            # Validate token format
            if not token or len(token) != 6 or not token.isdigit():
                print(f"DEBUG ROUTE: Token format invalid")
                flash('Invalid code format. Please enter exactly 6 digits.', 'error')
            elif secure_admin.verify_2fa_token(user.id, token):
                print(f"DEBUG ROUTE: Token verified successfully for user {user.id}")
                # Enable 2FA
                admin_sec = db.session.query(AdminSecurityModel).filter_by(user_id=user.id).first()
                if admin_sec:
                    admin_sec.mfa_enabled = True
                    db.session.commit()
                    print(f"DEBUG ROUTE: 2FA enabled in database")
                
                secure_admin.log_admin_action(
                    user.id,
                    'ENABLE_2FA',
                    status='success'
                )
                
                flash('2FA enabled successfully! Your account is now protected.', 'success')
                return redirect(url_for('admin_secure.dashboard'))
            else:
                print(f"DEBUG ROUTE: Token verification failed for user {user.id}")
                flash('Invalid verification code. The code may have expired. Please try again.', 'error')
        
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
                logger.info("POST /setup-facial-id - Enrollment request received")
                logger.info(f"Request content type: {request.content_type}")
                logger.info(f"Request files: {list(request.files.keys())}")
                logger.info(f"Request form: {list(request.form.keys())}")
                
                # Get image - can be file upload or base64
                image_data = None
                
                # Try file upload first
                if 'face_image' in request.files:
                    image_file = request.files['face_image']
                    if image_file.filename != '':
                        image_data = image_file.read()
                        logger.info(f"Image from file: {len(image_data)} bytes, filename: {image_file.filename}")
                
                # Try base64 from form if no file
                elif 'face_image_base64' in request.form:
                    base64_str = request.form.get('face_image_base64', '')
                    if base64_str:
                        import base64
                        try:
                            image_data = base64.b64decode(base64_str)
                            logger.info(f"Image from base64: {len(image_data)} bytes")
                        except Exception as e:
                            logger.error(f"Failed to decode base64: {e}")
                            return jsonify({'success': False, 'message': 'Invalid image data'}), 400
                
                if not image_data:
                    logger.error("No image data provided")
                    return jsonify({'success': False, 'message': 'No image provided'}), 400
                
                # Enroll face
                logger.info(f"Calling enroll_admin_face for admin {user.id}...")
                result = facial_id_manager.enroll_admin_face(
                    user.id,
                    image_data,
                    image_label=request.form.get('label', 'default')
                )
                logger.info(f"Enrollment result: {result}")
                
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
                    logger.error(f"Enrollment failed: {result}")
                    return jsonify({'success': False, 'message': result.get('message', 'Enrollment failed')}), 400
                    
            except Exception as e:
                logger.error(f"Facial ID enrollment error: {e}", exc_info=True)
                secure_admin.log_admin_action(
                    user.id,
                    'ENROLL_FACIAL_ID',
                    status='failure',
                    details={'error': str(e)}
                )
                return jsonify({'success': False, 'message': str(e)}), 500
        
        # Get facial ID stats
        try:
            facial_stats = facial_id_manager.get_admin_facial_stats(user.id)
        except Exception as e:
            logger.error(f"Error getting facial stats: {e}")
            facial_stats = {'enrolled': False}
        
        return render_template(
            'admin/setup_facial_id.html',
            user=user,
            facial_stats=facial_stats
        )
    
    
    @admin_bp.route('/verify-facial-id', methods=['GET', 'POST'])
    def verify_facial_id():
        """Verify admin identity using facial recognition (supports both file and descriptor)"""
        
        # Check authentication
        if 'user_id' not in session:
            if request.method == 'POST':
                return jsonify({'success': False, 'message': 'Not authenticated'}), 401
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'super_admin']:
            abort(403)
        
        # For GET requests, require 2FA
        if request.method == 'GET':
            admin_sec = AdminSecurityModel.query.filter_by(user_id=user.id).first()
            if admin_sec and admin_sec.mfa_enabled:
                if '2fa_verified' not in session:
                    return redirect(url_for('admin_secure.verify_2fa'))
        
        if request.method == 'POST':
            try:
                logger.info(f"Facial verification request from admin {user.id}")
                logger.info(f"Request content type: {request.content_type}")
                logger.info(f"Request files: {list(request.files.keys())}")
                
                # Check if JSON descriptor is provided (from auto-verification)
                if request.is_json:
                    logger.info("Processing JSON descriptor request")
                    data = request.get_json()
                    if 'face_descriptor' not in data:
                        logger.error("No face descriptor provided in JSON")
                        return jsonify({'success': False, 'message': 'No face descriptor provided'}), 400
                    
                    # Verify using descriptor
                    logger.info("Calling verify_admin_face_descriptor...")
                    is_verified, details = facial_id_manager.verify_admin_face_descriptor(
                        user.id,
                        data['face_descriptor']
                    )
                # Check if file upload is provided
                elif 'face_image' in request.files:
                    logger.info("Processing face image upload")
                    image_file = request.files['face_image']
                    image_data = image_file.read()
                    logger.info(f"Image data received: {len(image_data)} bytes, filename: {image_file.filename}")
                    
                    if not image_data:
                        logger.error("Image data is empty")
                        return jsonify({'success': False, 'message': 'Image is empty'}), 400
                    
                    # Verify face from image
                    logger.info(f"Calling verify_admin_face for admin {user.id}...")
                    is_verified, details = facial_id_manager.verify_admin_face(user.id, image_data)
                else:
                    logger.warning(f"No image or descriptor provided - Files: {list(request.files.keys())}, Is JSON: {request.is_json}")
                    return jsonify({'success': False, 'message': 'No image or descriptor provided'}), 400
                
                logger.info(f"Verification result - verified: {is_verified}, details: {details}")
                
                if is_verified:
                    # Mark facial ID as verified in session
                    session['facial_id_verified'] = True
                    session['facial_id_verified_at'] = datetime.utcnow().isoformat()
                    
                    secure_admin.log_admin_action(
                        user.id,
                        'VERIFY_FACIAL_ID',
                        status='success',
                        details={
                            'confidence': details.get('confidence', 0),
                            'match_count': details.get('match_count', 0)
                        }
                    )
                    
                    logger.info(f"Facial verification successful for admin {user.id}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Face verified successfully',
                        'confidence': details.get('confidence', 0),
                        'match_count': details.get('match_count', 0)
                    }), 200
                else:
                    secure_admin.log_admin_action(
                        user.id,
                        'VERIFY_FACIAL_ID',
                        status='failure',
                        details={'reason': details.get('message', 'Verification failed')}
                    )
                    
                    logger.warning(f"Facial verification failed for admin {user.id}: {details}")
                    
                    return jsonify({
                        'success': False,
                        'message': details.get('message', 'Face did not match'),
                        'confidence': details.get('confidence', 0)
                    }), 401
                    
            except Exception as e:
                logger.error(f"Facial ID verification error: {e}", exc_info=True)
                secure_admin.log_admin_action(
                    user.id,
                    'VERIFY_FACIAL_ID',
                    status='failure',
                    details={'error': str(e)}
                )
                return jsonify({'success': False, 'message': f'Verification error: {str(e)}'}), 500
        
        return render_template('admin/verify_facial_id.html', user=user)
    
    
    @admin_bp.route('/get-facial-stats', methods=['GET'])
    def get_facial_stats():
        """Get facial ID stats for current admin"""
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        try:
            user = User.query.get(session.get('user_id'))
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            stats = facial_id_manager.get_admin_facial_stats(user.id)
            return jsonify(stats), 200
        except Exception as e:
            logger.error(f"Error getting facial stats: {e}")
            return jsonify({'error': str(e)}), 500
    
    
    @admin_bp.route('/get-enrolled-faces', methods=['GET'])
    def get_enrolled_faces():
        """Get enrolled faces for current admin"""
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        try:
            user = User.query.get(session.get('user_id'))
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            facial_data_list = FacialIDData.query.filter_by(admin_id=user.id).all()
            faces = []
            for fd in facial_data_list:
                faces.append({
                    'id': fd.id,
                    'label': fd.encoding_label or 'Enrolled Face',
                    'enrolled_at': fd.enrolled_at.isoformat() if fd.enrolled_at else None,
                    'preview': fd.face_preview or '',
                    'capture_quality': fd.capture_quality or 0.0
                })
            
            return jsonify({'faces': faces}), 200
        except Exception as e:
            logger.error(f"Error getting enrolled faces: {e}")
            return jsonify({'error': str(e)}), 500
    
    @admin_bp.route('/delete-enrolled-face/<int:face_id>', methods=['DELETE', 'POST'])
    def delete_enrolled_face(face_id):
        """Delete an enrolled facial ID"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        try:
            from app import db
            user = User.query.get(session.get('user_id'))
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 401
            
            # Get the facial data and verify it belongs to this user
            facial_data = FacialIDData.query.filter_by(id=face_id, admin_id=user.id).first()
            if not facial_data:
                return jsonify({'success': False, 'error': 'Face not found or access denied'}), 404
            
            # Delete it
            db.session.delete(facial_data)
            db.session.commit()
            
            secure_admin.log_admin_action(
                user.id,
                'DELETE_FACIAL_ID',
                status='success',
                details={'face_id': face_id}
            )
            
            return jsonify({'success': True, 'message': f'Face {face_id} deleted'}), 200
            
        except Exception as e:
            logger.error(f"Error deleting enrolled face: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @admin_bp.route('/delete-all-enrolled-faces', methods=['DELETE', 'POST'])
    def delete_all_enrolled_faces():
        """Delete ALL enrolled facial IDs for current admin"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        try:
            from app import db
            user = User.query.get(session.get('user_id'))
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 401
            
            # Get all facial data for this user
            facial_data_list = FacialIDData.query.filter_by(admin_id=user.id).all()
            count = len(facial_data_list)
            
            # Delete all
            for facial_data in facial_data_list:
                db.session.delete(facial_data)
            
            db.session.commit()
            
            secure_admin.log_admin_action(
                user.id,
                'DELETE_ALL_FACIAL_IDS',
                status='success',
                details={'count': count}
            )
            
            return jsonify({'success': True, 'message': f'{count} faces deleted'}), 200
            
        except Exception as e:
            logger.error(f"Error deleting all enrolled faces: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @admin_bp.route('/enroll-facial-id', methods=['POST'])
    @require_admin_with_2fa
    def enroll_facial_id():
        """Enroll a new facial ID with descriptor"""
        try:
            user = User.query.get(session.get('user_id'))
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            data = request.get_json()
            descriptor = data.get('descriptor')
            label = data.get('label', 'Primary Face')
            
            if not descriptor or not isinstance(descriptor, list):
                return jsonify({'error': 'Invalid descriptor'}), 400
            
            # Enroll using descriptor
            success, details = facial_id_manager.enroll_admin_face_descriptor(
                user.id,
                descriptor,
                label
            )
            
            if success:
                secure_admin.log_admin_action(
                    user.id,
                    'ENROLL_FACIAL_ID',
                    status='success'
                )
                return jsonify({'success': True, 'message': 'Facial ID enrolled'}), 200
            else:
                return jsonify({'success': False, 'message': details.get('error', 'Enrollment failed')}), 400
        except Exception as e:
            logger.error(f"Error enrolling facial ID: {e}")
            return jsonify({'error': str(e)}), 500
    
    
    @admin_bp.route('/delete-facial-id', methods=['POST'])
    @require_admin_with_2fa
    def delete_facial_id():
        """Delete all facial ID data"""
        try:
            user = User.query.get(session.get('user_id'))
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            FacialIDData.query.filter_by(admin_id=user.id).delete()
            db.session.commit()
            
            secure_admin.log_admin_action(
                user.id,
                'DELETE_FACIAL_ID',
                status='success'
            )
            
            return jsonify({'success': True}), 200
        except Exception as e:
            logger.error(f"Error deleting facial ID: {e}")
            return jsonify({'error': str(e)}), 500
    
    
    @admin_bp.route('/delete-face/<int:face_id>', methods=['DELETE'])
    @require_admin_with_2fa
    def delete_face(face_id):
        """Delete a specific face"""
        try:
            user = User.query.get(session.get('user_id'))
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            facial_data = FacialIDData.query.filter_by(
                id=face_id,
                admin_id=user.id
            ).first()
            
            if facial_data:
                db.session.delete(facial_data)
                db.session.commit()
                
                secure_admin.log_admin_action(
                    user.id,
                    'DELETE_FACIAL_ID_ENROLLMENT',
                    resource_type='facial_id',
                    resource_id=face_id,
                    status='success'
                )
                
                return jsonify({'success': True}), 200
            else:
                return jsonify({'error': 'Face not found'}), 404
        except Exception as e:
            logger.error(f"Error deleting face: {e}")
            return jsonify({'error': str(e)}), 500
    
    
    
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
            'admin_facial_dashboard.html',
            user=user,
            stats=stats,
            recent_actions=recent_actions,
            project_count=stats['total_projects'],
            user_count=stats['total_users'],
            team_count=stats['total_teams'],
            issue_count=stats['total_issues'],
            online_users_count=stats['active_sessions'],
            facial_id_count=FacialIDData.query.filter_by(is_verified=True).count()
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
        return render_template('facial_login_improved.html')
    
    
    @admin_bp.route('/facial-login-verify', methods=['POST'])
    @csrf.exempt  # CSRF exempt - public facial authentication endpoint
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
            
            logger.info("Processing facial login verification request")
            
            # Remove data URI prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64 to image bytes
            image_bytes = base64.b64decode(image_data)
            logger.info(f"Decoded image bytes: {len(image_bytes)} bytes")
            
            # Verify against enrolled admin faces
            # Only check admins who actually have enrolled faces
            admin_users = User.query.filter_by(role='admin').all()
            admin_users.extend(User.query.filter_by(role='super_admin').all())
            
            # Filter to only users with enrolled faces
            admin_users_with_faces = []
            for user in admin_users:
                has_faces = FacialIDData.query.filter_by(
                    admin_id=user.id,
                    is_verified=True
                ).first()
                if has_faces:
                    admin_users_with_faces.append(user)
            
            logger.info(f"Found {len(admin_users_with_faces)} admin users with enrolled faces out of {len(admin_users)} total admins")
            
            verified_user = None
            best_match_confidence = 0
            verification_details = None
            
            # If no one has enrolled faces, fail immediately
            if not admin_users_with_faces:
                logger.warning("No admin users with enrolled faces found")
                return jsonify({
                    'success': False,
                    'message': 'No enrolled faces in system. Please enroll first.'
                }), 401
            
            for admin_user in admin_users_with_faces:
                try:
                    logger.info(f"Verifying against admin user {admin_user.id} ({admin_user.username})")
                    
                    # Verify face against all enrolled faces for this admin
                    # Pass image bytes, not PIL Image object
                    is_verified, details = facial_id_manager.verify_admin_face(
                        admin_user.id,
                        image_bytes  # Pass bytes instead of PIL Image
                    )
                    
                    logger.info(f"Verification result for {admin_user.username}: is_verified={is_verified}, confidence={details.get('confidence', 0):.4f}")
                    
                    # Track best match across all users
                    current_confidence = details.get('confidence', 0)
                    if current_confidence > best_match_confidence:
                        best_match_confidence = current_confidence
                        verified_user = admin_user
                        verification_details = details
                        
                        logger.info(f"New best match: user={admin_user.username}, confidence={best_match_confidence:.4f}, is_verified={is_verified}")
                        
                        # If verified, we found a match - continue checking others for best match
                        # (don't break early - find the absolute best match)
                            
                except Exception as e:
                    logger.error(f"Face verification error for admin {admin_user.id}: {e}", exc_info=True)
                    continue
            
            # Check if face matched
            if verified_user and verification_details:
                is_match = verification_details.get('success', False)
                confidence = verification_details.get('confidence', 0)
                
                logger.info(f"Final verification decision: is_match={is_match}, confidence={confidence:.4f}, user={verified_user.username}")
                
                if is_match:
                    # Get the matched face ID
                    matched_face_id = None
                    matched_face_label = None
                    
                    if verification_details.get('matches'):
                        # Find the best matching face
                        best_match_face = max(
                            verification_details.get('matches', []),
                            key=lambda x: x.get('confidence', 0)
                        )
                        matched_face_id = best_match_face.get('encoding_id')
                        matched_face_label = best_match_face.get('label', 'Unknown')
                    
                    # Create session for admin - use Flask-Login to properly authenticate
                    login_user(verified_user, remember=True)
                    session['facial_verified'] = True
                    session['2fa_verified'] = datetime.utcnow().timestamp()  # Mark 2FA as verified for facial login
                    session['facial_verification_time'] = datetime.now().isoformat()
                    session['facial_encoding_id'] = str(matched_face_id)  # Store matched face ID
                    
                    logger.info(f"Admin {verified_user.username} logged in via facial recognition (Face ID: {matched_face_id}, Label: {matched_face_label}, Confidence: {best_match_confidence:.2%})")
                
                return jsonify({
                    'success': True,
                    'message': 'Face verified successfully',
                    'confidence': best_match_confidence,
                    'face_id': str(matched_face_id),  # Unique ID of matched face
                    'face_label': matched_face_label,
                    'admin_id': verified_user.id,
                    'redirect': '/'
                }), 200
            else:
                # Log failed facial verification
                if verified_user:
                    logger.warning(f"Facial verification failed - low confidence: {best_match_confidence:.2%}")
                
                return jsonify({
                    'success': False,
                    'message': 'Face not recognized. Please ensure proper lighting and position your face clearly.'
                }), 401
        
        except Exception as e:
            import traceback
            logger.error(f"Facial login error: {e}", exc_info=True)
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # More specific error messages
            error_msg = str(e).lower()
            if 'padding' in error_msg:
                return jsonify({
                    'success': False,
                    'message': 'Invalid image data. Please try again.',
                    'error_detail': 'Base64 decoding failed'
                }), 400
            elif 'face' in error_msg or 'detect' in error_msg:
                return jsonify({
                    'success': False,
                    'message': 'No face detected. Please try again.',
                    'error_detail': str(e)
                }), 401
            else:
                return jsonify({
                    'success': False,
                    'message': 'Verification error. Please try again.',
                    'error_detail': str(e)
                }), 500
    
    
    return admin_bp


# Import AdminSecurityModel
from app.admin_secure.auth import AdminSecurityModel
import secrets

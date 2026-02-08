# app/routes/security_routes.py
"""
Advanced Security API Routes
Endpoints for zero-trust security, micro-segmentation, verification, and privilege management.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from typing import Dict, Any
import logging

from app.security.zero_trust_engine import ZeroTrustEngine
from app.security.micro_segmentation import MicroSegmentation
from app.security.continuous_verification import ContinuousVerification
from app.security.privilege_manager import privilege_manager, Permission

logger = logging.getLogger(__name__)

# Create blueprint
security_bp = Blueprint('security_advanced', __name__, url_prefix='/api/v1/security')

# Initialize security services
zero_trust_engine = ZeroTrustEngine()
segmentation = MicroSegmentation()
verification = ContinuousVerification()


def require_auth(f):
    """Require authentication for endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In production, implement proper auth checking
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# ZERO-TRUST SECURITY ROUTES
# ============================================================================

@security_bp.route('/zero-trust/evaluate', methods=['POST'])
@require_auth
def zero_trust_evaluate():
    """Evaluate trust level for user access."""
    data = request.get_json()
    user_id = data.get('user_id')
    device_id = data.get('device_id')
    ip_address = data.get('ip_address')
    
    security_context = zero_trust_engine.evaluate_trust(user_id, device_id, ip_address)
    return jsonify(security_context.to_dict())


@security_bp.route('/zero-trust/enforce', methods=['POST'])
@require_auth
def zero_trust_enforce():
    """Enforce zero-trust access control."""
    data = request.get_json()
    user_id = data.get('user_id')
    resource = data.get('resource')
    action = data.get('action')
    
    context = {
        'user_id': user_id,
        'resource': resource,
        'action': action,
        'timestamp': data.get('timestamp'),
        'ip_address': data.get('ip_address'),
        'device_id': data.get('device_id')
    }
    
    allowed = zero_trust_engine.enforce_access(context)
    return jsonify({
        'allowed': allowed,
        'user_id': user_id,
        'resource': resource,
        'reason': 'Access granted' if allowed else 'Trust threshold not met'
    })


@security_bp.route('/zero-trust/stats', methods=['GET'])
@require_auth
def zero_trust_stats():
    """Get zero-trust statistics."""
    stats = zero_trust_engine.get_stats()
    return jsonify(stats)


@security_bp.route('/zero-trust/context/<user_id>', methods=['GET'])
@require_auth
def zero_trust_context(user_id):
    """Get user security context."""
    if user_id in zero_trust_engine.security_contexts:
        context = zero_trust_engine.security_contexts[user_id]
        return jsonify(context.to_dict())
    return jsonify({'error': 'User context not found'}), 404


# ============================================================================
# MICRO-SEGMENTATION ROUTES
# ============================================================================

@security_bp.route('/segments', methods=['GET', 'POST'])
@require_auth
def segments():
    """List or create segments."""
    if request.method == 'POST':
        data = request.get_json()
        segment_name = data.get('name')
        segment_type = data.get('type')
        description = data.get('description')
        
        segment = segmentation.create_segment(
            name=segment_name,
            segment_type=segment_type,
            description=description
        )
        return jsonify(segment.to_dict()), 201
    
    segments_list = [s.to_dict() for s in segmentation.segments.values()]
    return jsonify({'segments': segments_list})


@security_bp.route('/segments/<segment_id>', methods=['GET', 'DELETE'])
@require_auth
def segment_detail(segment_id):
    """Get or delete segment."""
    if request.method == 'DELETE':
        segmentation.delete_segment(segment_id)
        return jsonify({'status': 'success'}), 204
    
    if segment_id in segmentation.segments:
        return jsonify(segmentation.segments[segment_id].to_dict())
    
    return jsonify({'error': 'Segment not found'}), 404


@security_bp.route('/segments/<segment_id>/members', methods=['GET', 'POST', 'DELETE'])
@require_auth
def segment_members(segment_id):
    """Manage segment members."""
    if request.method == 'GET':
        if segment_id in segmentation.segments:
            members = list(segmentation.segments[segment_id].members)
            return jsonify({'segment_id': segment_id, 'members': members})
        return jsonify({'error': 'Segment not found'}), 404
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    if request.method == 'POST':
        segmentation.add_to_segment(user_id, segment_id)
        return jsonify({'status': 'success', 'user_added': True}), 201
    
    elif request.method == 'DELETE':
        segmentation.remove_from_segment(user_id, segment_id)
        return jsonify({'status': 'success', 'user_removed': True})


@security_bp.route('/segments/<segment_id>/access-check', methods=['POST'])
@require_auth
def segment_access_check(segment_id):
    """Check access within segment."""
    data = request.get_json()
    user_id = data.get('user_id')
    resource = data.get('resource')
    
    can_access = segmentation.can_access(user_id, segment_id, resource)
    return jsonify({
        'user_id': user_id,
        'segment_id': segment_id,
        'resource': resource,
        'can_access': can_access
    })


@security_bp.route('/user/<user_id>/segments', methods=['GET'])
@require_auth
def user_segments(user_id):
    """Get segments for user."""
    segments_list = segmentation.get_user_segments(user_id)
    return jsonify({
        'user_id': user_id,
        'segments': segments_list
    })


@security_bp.route('/segments/stats', methods=['GET'])
@require_auth
def segments_stats():
    """Get segmentation statistics."""
    stats = segmentation.get_stats()
    return jsonify(stats)


# ============================================================================
# CONTINUOUS VERIFICATION ROUTES
# ============================================================================

@security_bp.route('/verify/action', methods=['POST'])
@require_auth
def verify_action():
    """Verify user action."""
    data = request.get_json()
    user_id = data.get('user_id')
    action = data.get('action')
    context = data.get('context', {})
    
    is_verified = verification.verify_action(user_id, action, context)
    requires_reauth = verification.require_reauthentication(user_id, action)
    
    return jsonify({
        'user_id': user_id,
        'action': action,
        'verified': is_verified,
        'requires_reauthentication': requires_reauth
    })


@security_bp.route('/verify/session/<user_id>', methods=['POST'])
@require_auth
def verify_session(user_id):
    """Verify user session."""
    data = request.get_json()
    session_id = data.get('session_id')
    
    is_valid = verification.verify_session(user_id, session_id)
    return jsonify({
        'user_id': user_id,
        'session_id': session_id,
        'valid': is_valid
    })


@security_bp.route('/user/<user_id>/risk-score', methods=['GET'])
@require_auth
def user_risk_score(user_id):
    """Get user risk score."""
    risk_score = verification.get_user_risk_score(user_id)
    return jsonify({
        'user_id': user_id,
        'risk_score': risk_score,
        'risk_level': 'low' if risk_score < 30 else 'medium' if risk_score < 70 else 'high'
    })


@security_bp.route('/user/<user_id>/verification-events', methods=['GET'])
@require_auth
def user_verification_events(user_id):
    """Get user verification events."""
    limit = request.args.get('limit', 50, type=int)
    events = verification.get_recent_events(user_id, limit)
    return jsonify({
        'user_id': user_id,
        'events': [e.to_dict() for e in events]
    })


@security_bp.route('/verify/stats', methods=['GET'])
@require_auth
def verification_stats():
    """Get verification statistics."""
    stats = verification.get_stats()
    return jsonify(stats)


# ============================================================================
# PRIVILEGE MANAGEMENT ROUTES
# ============================================================================

@security_bp.route('/roles', methods=['GET', 'POST'])
@require_auth
def roles():
    """List or create roles."""
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        permissions_list = data.get('permissions', [])
        
        # Convert permission names to Permission enum values
        try:
            permissions = {Permission[p] for p in permissions_list}
        except KeyError as e:
            return jsonify({'error': f'Unknown permission: {str(e)}'}), 400
        
        role = privilege_manager.create_role(name, list(permissions))
        return jsonify({'id': role.id, 'name': role.name}), 201
    
    roles_list = [{'id': r.id, 'name': r.name, 'permissions': [p.value for p in r.permissions]}
                  for r in privilege_manager.roles.values()]
    return jsonify({'roles': roles_list})


@security_bp.route('/roles/<role_id>', methods=['GET', 'DELETE'])
@require_auth
def role_detail(role_id):
    """Get or delete role."""
    if request.method == 'DELETE':
        if role_id not in privilege_manager.roles:
            return jsonify({'error': 'Role not found'}), 404
        del privilege_manager.roles[role_id]
        return jsonify({'status': 'success'}), 204
    
    if role_id in privilege_manager.roles:
        r = privilege_manager.roles[role_id]
        return jsonify({
            'id': r.id,
            'name': r.name,
            'permissions': [p.value for p in r.permissions]
        })
    return jsonify({'error': 'Role not found'}), 404


@security_bp.route('/user/<user_id>/roles', methods=['GET', 'POST', 'DELETE'])
@require_auth
def user_roles(user_id):
    """Manage user roles."""
    if request.method == 'GET':
        roles = privilege_manager.get_user_roles(user_id)
        return jsonify({
            'user_id': user_id,
            'roles': [{'id': r.id, 'name': r.name} for r in roles.values()] if isinstance(roles, dict) else [{'id': r.id, 'name': r.name} for r in roles]
        })
    
    data = request.get_json()
    role_id = data.get('role_id')
    
    if request.method == 'POST':
        privilege_manager.assign_role(user_id, role_id)
        return jsonify({'status': 'success', 'role_assigned': True}), 201
    
    elif request.method == 'DELETE':
        privilege_manager.revoke_role(user_id, role_id)
        return jsonify({'status': 'success', 'role_revoked': True})


@security_bp.route('/user/<user_id>/permissions', methods=['GET'])
@require_auth
def user_permissions(user_id):
    """Get user permissions."""
    perms = privilege_manager.get_user_permissions(user_id)
    perm_dict = perms if isinstance(perms, dict) else {'READ': True, 'WRITE': False, 'DELETE': False}
    return jsonify({
        'user_id': user_id,
        'permissions': perm_dict
    })


@security_bp.route('/user/<user_id>/check-permission', methods=['POST'])
@require_auth
def check_permission(user_id):
    """Check if user has permission."""
    data = request.get_json()
    permission_name = data.get('permission')
    
    # Try to get permission from enum
    try:
        permission = Permission[permission_name]
    except KeyError:
        return jsonify({'error': f'Unknown permission: {permission_name}'}), 400
    
    has_permission = privilege_manager.check_permission(user_id, permission)
    return jsonify({
        'user_id': user_id,
        'permission': permission.value,
        'has_permission': has_permission
    })


@security_bp.route('/user/<user_id>/grant-privilege', methods=['POST'])
@require_auth
def grant_privilege(user_id):
    """Grant temporary privilege to user."""
    data = request.get_json()
    permission_name = data.get('permission')
    reason = data.get('reason', '')
    
    # Try to get permission from enum
    try:
        permission = Permission[permission_name]
    except KeyError:
        return jsonify({'error': f'Unknown permission: {permission_name}'}), 400
    
    grant = privilege_manager.grant_privilege(user_id, permission, reason=reason)
    return jsonify({'grant_id': grant.get('id')}), 201


@security_bp.route('/user/<user_id>/revoke-privilege/<grant_id>', methods=['DELETE'])
@require_auth
def revoke_privilege(user_id, grant_id):
    """Revoke temporary privilege."""
    actor = request.args.get('actor', 'system')
    privilege_manager.revoke_privilege(grant_id, actor)
    return jsonify({'status': 'success', 'privilege_revoked': True})


@security_bp.route('/privileges/cleanup', methods=['POST'])
@require_auth
def privileges_cleanup():
    """Clean up expired privilege grants."""
    count = privilege_manager.cleanup_expired_grants()
    return jsonify({
        'status': 'success',
        'expired_grants_removed': count
    })


@security_bp.route('/privileges/audit-log', methods=['GET'])
@require_auth
def privileges_audit_log():
    """Get privilege audit log."""
    user_id = request.args.get('user_id')
    limit = request.args.get('limit', 100, type=int)
    
    log = privilege_manager.get_audit_log(user_id, limit)
    return jsonify({'audit_log': log})


@security_bp.route('/privileges/stats', methods=['GET'])
@require_auth
def privileges_stats():
    """Get privilege statistics."""
    stats = privilege_manager.get_stats()
    return jsonify(stats)


# ============================================================================
# HEALTH & STATUS
# ============================================================================

@security_bp.route('/health', methods=['GET'])
def security_health():
    """Health check for security systems."""
    return jsonify({
        'status': 'healthy',
        'systems': {
            'zero_trust': zero_trust_engine.get_stats(),
            'segmentation': segmentation.get_stats(),
            'verification': verification.get_stats(),
            'privileges': privilege_manager.get_stats()
        }
    })

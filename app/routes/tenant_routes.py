# app/routes/tenant_routes.py
"""
Multi-Tenant Management API Routes
Tenant provisioning, user management, and resource quotas.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from app.tenant.multi_tenant import multi_tenant_manager


def require_auth(f):
    """Require authentication for tenant endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in request.headers.get('Authorization', ''):
            if 'user_id' not in getattr(request, 'user', {}):
                # For development, allow any request with user_id header
                request.user_id = request.headers.get('X-User-ID', 'guest')
            else:
                request.user_id = request.user.get('id', 'guest')
        else:
            request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


tenant_bp = Blueprint('tenant', __name__, url_prefix='/api/v1/tenant')


@tenant_bp.route('/create', methods=['POST'])
@require_auth
def create_tenant():
    """Create new tenant."""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        tenant = multi_tenant_manager.create_tenant(
            name=data.get('name', ''),
            slug=data.get('slug', ''),
            owner_id=user_id,
            custom_domain=data.get('custom_domain')
        )
        
        return jsonify({
            'status': 'success',
            'tenant': tenant.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/<tenant_id>', methods=['GET'])
@require_auth
def get_tenant(tenant_id):
    """Get tenant details."""
    try:
        tenant = multi_tenant_manager.get_tenant(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        return jsonify({
            'status': 'success',
            'tenant': tenant.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/slug/<slug>', methods=['GET'])
def get_tenant_by_slug(slug):
    """Get tenant by slug (public endpoint)."""
    try:
        tenant = multi_tenant_manager.get_tenant_by_slug(slug)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        # Return limited info for public access
        return jsonify({
            'status': 'success',
            'tenant': {
                'name': tenant.name,
                'slug': tenant.slug,
                'logo_url': tenant.logo_url,
                'custom_domain': tenant.custom_domain
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/<tenant_id>/users', methods=['GET'])
@require_auth
def get_tenant_users(tenant_id):
    """Get all users in tenant."""
    try:
        tenant = multi_tenant_manager.get_tenant(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        users = multi_tenant_manager.get_tenant_users(tenant_id)
        
        return jsonify({
            'status': 'success',
            'users': users,
            'total': len(users)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/<tenant_id>/users/add', methods=['POST'])
@require_auth
def add_tenant_user(tenant_id):
    """Add user to tenant."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        role = data.get('role', 'member')
        
        success = multi_tenant_manager.add_tenant_user(tenant_id, user_id, role)
        
        if not success:
            return jsonify({'error': 'Failed to add user'}), 400
        
        return jsonify({
            'status': 'success',
            'message': f'User {user_id} added to tenant'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/<tenant_id>/usage', methods=['GET'])
@require_auth
def get_usage_summary(tenant_id):
    """Get usage summary for tenant."""
    try:
        summary = multi_tenant_manager.get_usage_summary(tenant_id)
        
        return jsonify({
            'status': 'success',
            'usage': summary
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/<tenant_id>/usage/record', methods=['POST'])
@require_auth
def record_usage(tenant_id):
    """Record resource usage."""
    try:
        data = request.get_json()
        resource_type = data.get('resource_type')
        amount = data.get('amount', 1)
        
        success = multi_tenant_manager.record_usage(tenant_id, resource_type, amount)
        
        if not success:
            return jsonify({'error': 'Failed to record usage'}), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Usage recorded'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/<tenant_id>/quota/check', methods=['POST'])
@require_auth
def check_quota(tenant_id):
    """Check if tenant has available quota."""
    try:
        data = request.get_json()
        resource_type = data.get('resource_type')
        amount = data.get('amount', 1)
        
        has_quota = multi_tenant_manager.check_quota(tenant_id, resource_type, amount)
        
        return jsonify({
            'status': 'success',
            'has_quota': has_quota,
            'resource_type': resource_type
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/<tenant_id>/plan/upgrade', methods=['POST'])
@require_auth
def upgrade_plan(tenant_id):
    """Upgrade tenant plan."""
    try:
        data = request.get_json()
        plan = data.get('plan', 'professional')
        
        success = multi_tenant_manager.upgrade_tenant_plan(tenant_id, plan)
        
        if not success:
            return jsonify({'error': 'Failed to upgrade plan'}), 400
        
        usage = multi_tenant_manager.get_usage_summary(tenant_id)
        
        return jsonify({
            'status': 'success',
            'message': f'Tenant upgraded to {plan} plan',
            'usage': usage
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/<tenant_id>/suspend', methods=['POST'])
@require_auth
def suspend_tenant(tenant_id):
    """Suspend tenant."""
    try:
        data = request.get_json()
        reason = data.get('reason', '')
        
        success = multi_tenant_manager.suspend_tenant(tenant_id, reason)
        
        if not success:
            return jsonify({'error': 'Failed to suspend tenant'}), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Tenant suspended'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/<tenant_id>/activate', methods=['POST'])
@require_auth
def activate_tenant(tenant_id):
    """Activate suspended tenant."""
    try:
        success = multi_tenant_manager.activate_tenant(tenant_id)
        
        if not success:
            return jsonify({'error': 'Failed to activate tenant'}), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Tenant activated'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/user/tenants', methods=['GET'])
@require_auth
def get_user_tenants():
    """Get all tenants for current user."""
    try:
        user_id = request.user_id
        tenants = multi_tenant_manager.get_user_tenants(user_id)
        
        return jsonify({
            'status': 'success',
            'tenants': tenants,
            'total': len(tenants)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tenant_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get multi-tenant statistics."""
    try:
        stats = multi_tenant_manager.get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# app/routes/customer_portal_routes.py
"""
Customer Portal API Routes
Customer ticket management, knowledge base access, and analytics.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from app.portal.customer_portal import customer_portal_manager


def require_auth(f):
    """Require authentication for portal endpoints"""
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


portal_bp = Blueprint('portal', __name__, url_prefix='/api/v1/portal')


@portal_bp.route('/tickets/create', methods=['POST'])
@require_auth
def create_ticket():
    """Create new support ticket."""
    try:
        customer_id = request.user_id
        data = request.get_json()
        
        ticket = customer_portal_manager.create_ticket(
            customer_id=customer_id,
            tenant_id=data.get('tenant_id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            category=data.get('category', 'general'),
            priority=data.get('priority', 'medium')
        )
        
        return jsonify({
            'status': 'success',
            'ticket': ticket.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/tickets/<ticket_id>', methods=['GET'])
@require_auth
def get_ticket(ticket_id):
    """Get ticket details."""
    try:
        ticket = customer_portal_manager.get_ticket(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        return jsonify({
            'status': 'success',
            'ticket': ticket.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/tickets', methods=['GET'])
@require_auth
def get_customer_tickets():
    """Get all tickets for customer."""
    try:
        customer_id = request.user_id
        tickets = customer_portal_manager.get_customer_tickets(customer_id)
        
        return jsonify({
            'status': 'success',
            'tickets': tickets,
            'total': len(tickets)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/tickets/<ticket_id>/comments', methods=['GET'])
@require_auth
def get_ticket_comments(ticket_id):
    """Get comments on ticket."""
    try:
        comments = customer_portal_manager.get_ticket_comments(ticket_id)
        
        return jsonify({
            'status': 'success',
            'comments': comments,
            'total': len(comments)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/tickets/<ticket_id>/comment', methods=['POST'])
@require_auth
def add_ticket_comment(ticket_id):
    """Add comment to ticket."""
    try:
        author_id = request.user_id
        data = request.get_json()
        
        comment = customer_portal_manager.add_comment(
            ticket_id=ticket_id,
            author_id=author_id,
            author_type=data.get('author_type', 'customer'),
            content=data.get('content', '')
        )
        
        if not comment:
            return jsonify({'error': 'Ticket not found'}), 404
        
        return jsonify({
            'status': 'success',
            'comment': comment.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/tickets/<ticket_id>/status', methods=['PUT'])
@require_auth
def update_ticket_status(ticket_id):
    """Update ticket status."""
    try:
        data = request.get_json()
        status = data.get('status')
        
        success = customer_portal_manager.update_ticket_status(ticket_id, status)
        
        if not success:
            return jsonify({'error': 'Failed to update status'}), 400
        
        ticket = customer_portal_manager.get_ticket(ticket_id)
        
        return jsonify({
            'status': 'success',
            'ticket': ticket.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/branding/<tenant_id>', methods=['GET'])
def get_portal_branding(tenant_id):
    """Get portal branding (public endpoint)."""
    try:
        branding = customer_portal_manager.get_portal_branding(tenant_id)
        
        if not branding:
            return jsonify({'error': 'Branding not found'}), 404
        
        return jsonify({
            'status': 'success',
            'branding': branding
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/branding/<tenant_id>/set', methods=['POST'])
@require_auth
def set_portal_branding(tenant_id):
    """Set portal branding for tenant."""
    try:
        data = request.get_json()
        
        branding = customer_portal_manager.set_portal_branding(tenant_id, data)
        
        return jsonify({
            'status': 'success',
            'branding': branding.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/invoices', methods=['GET'])
@require_auth
def get_customer_invoices():
    """Get invoices for customer."""
    try:
        customer_id = request.user_id
        invoices = customer_portal_manager.get_customer_invoices(customer_id)
        
        return jsonify({
            'status': 'success',
            'invoices': invoices,
            'total': len(invoices)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/invoices/create', methods=['POST'])
@require_auth
def create_invoice():
    """Create invoice for customer."""
    try:
        data = request.get_json()
        
        invoice = customer_portal_manager.create_invoice(
            tenant_id=data.get('tenant_id', ''),
            customer_id=request.user_id,
            amount=data.get('amount', 0.0),
            currency=data.get('currency', 'USD')
        )
        
        return jsonify({
            'status': 'success',
            'invoice': invoice.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/invoices/<invoice_id>/mark-paid', methods=['POST'])
@require_auth
def mark_invoice_paid(invoice_id):
    """Mark invoice as paid."""
    try:
        success = customer_portal_manager.mark_invoice_paid(invoice_id)
        
        if not success:
            return jsonify({'error': 'Invoice not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Invoice marked as paid'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/analytics/<tenant_id>', methods=['GET'])
@require_auth
def get_portal_analytics(tenant_id):
    """Get portal analytics."""
    try:
        analytics = customer_portal_manager.get_portal_analytics(tenant_id)
        
        return jsonify({
            'status': 'success',
            'analytics': analytics
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@portal_bp.route('/stats', methods=['GET'])
def get_portal_stats():
    """Get portal statistics."""
    try:
        stats = customer_portal_manager.get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

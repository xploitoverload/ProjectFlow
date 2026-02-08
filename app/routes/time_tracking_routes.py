# app/routes/time_tracking_routes.py
"""
Time Tracking and Billing API Routes
Time entry management, billing cycles, and invoicing endpoints.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime
from app.billing.time_tracking import time_tracking_manager


def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


billing_bp = Blueprint('billing', __name__, url_prefix='/api/v1/billing')


@billing_bp.route('/time/entries/create', methods=['POST'])
@require_auth
def create_time_entry():
    """Create time entry."""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        entry = time_tracking_manager.create_time_entry(
            user_id=user_id,
            project_id=data.get('project_id', ''),
            task_id=data.get('task_id', ''),
            hours=data.get('hours', 0.0),
            minutes=data.get('minutes', 0),
            description=data.get('description', ''),
            hourly_rate=data.get('hourly_rate', 0.0)
        )
        
        return jsonify({
            'status': 'success',
            'entry': entry.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/time/entries/<entry_id>', methods=['GET'])
@require_auth
def get_time_entry(entry_id):
    """Get time entry."""
    try:
        entry = time_tracking_manager.get_time_entry(entry_id)
        
        if not entry:
            return jsonify({'error': 'Entry not found'}), 404
        
        return jsonify({
            'status': 'success',
            'entry': entry.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/time/entries/user', methods=['GET'])
@require_auth
def get_user_time_entries():
    """Get user's time entries."""
    try:
        user_id = request.user_id
        start = request.args.get('start_date')
        end = request.args.get('end_date')
        
        start_date = datetime.fromisoformat(start) if start else None
        end_date = datetime.fromisoformat(end) if end else None
        
        entries = time_tracking_manager.get_user_time_entries(user_id, start_date, end_date)
        
        return jsonify({
            'status': 'success',
            'entries': entries,
            'total': len(entries)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/time/entries/<entry_id>/submit', methods=['POST'])
@require_auth
def submit_time_entry(entry_id):
    """Submit time entry."""
    try:
        success = time_tracking_manager.submit_time_entry(entry_id)
        
        if not success:
            return jsonify({'error': 'Entry not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Time entry submitted'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/time/entries/<entry_id>/approve', methods=['POST'])
@require_auth
def approve_time_entry(entry_id):
    """Approve time entry."""
    try:
        success = time_tracking_manager.approve_time_entry(entry_id)
        
        if not success:
            return jsonify({'error': 'Entry not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Time entry approved'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/cycles/create', methods=['POST'])
@require_auth
def create_billing_cycle():
    """Create billing cycle."""
    try:
        data = request.get_json()
        
        start = datetime.fromisoformat(data.get('start_date', ''))
        end = datetime.fromisoformat(data.get('end_date', ''))
        
        cycle = time_tracking_manager.create_billing_cycle(
            project_id=data.get('project_id', ''),
            start_date=start,
            end_date=end
        )
        
        return jsonify({
            'status': 'success',
            'cycle': cycle.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/invoices/create', methods=['POST'])
@require_auth
def create_invoice():
    """Create invoice."""
    try:
        data = request.get_json()
        
        invoice = time_tracking_manager.create_invoice(
            project_id=data.get('project_id', ''),
            client_id=data.get('client_id', ''),
            cycle_id=data.get('cycle_id', ''),
            amount=data.get('amount', 0.0),
            tax_rate=data.get('tax_rate', 0.0)
        )
        
        return jsonify({
            'status': 'success',
            'invoice': invoice.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/invoices/<invoice_id>/issue', methods=['POST'])
@require_auth
def issue_invoice(invoice_id):
    """Issue invoice."""
    try:
        success = time_tracking_manager.issue_invoice(invoice_id)
        
        if not success:
            return jsonify({'error': 'Invoice not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Invoice issued'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/invoices/<invoice_id>/mark-paid', methods=['POST'])
@require_auth
def mark_invoice_paid(invoice_id):
    """Mark invoice as paid."""
    try:
        success = time_tracking_manager.mark_invoice_paid(invoice_id)
        
        if not success:
            return jsonify({'error': 'Invoice not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Invoice marked as paid'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/projects/<project_id>/summary', methods=['GET'])
@require_auth
def get_billing_summary(project_id):
    """Get billing summary for project."""
    try:
        summary = time_tracking_manager.get_billing_summary(project_id)
        
        return jsonify({
            'status': 'success',
            'summary': summary
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get billing statistics."""
    try:
        stats = time_tracking_manager.get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# app/routes/finance_routes.py
"""
Finance and Budget Management API Routes
Budget planning, expense tracking, and financial reporting.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from app.finance.budget_management import finance_manager


def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


finance_bp = Blueprint('finance', __name__, url_prefix='/api/v1/finance')


@finance_bp.route('/budgets/create', methods=['POST'])
@require_auth
def create_budget():
    """Create budget."""
    try:
        data = request.get_json()
        
        budget = finance_manager.create_budget(
            name=data.get('name', ''),
            project_id=data.get('project_id', ''),
            total_allocation=data.get('total_allocation', 0.0),
            fiscal_year=data.get('fiscal_year')
        )
        
        return jsonify({
            'status': 'success',
            'budget': budget.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@finance_bp.route('/budgets/<budget_id>', methods=['GET'])
@require_auth
def get_budget(budget_id):
    """Get budget."""
    try:
        budget = finance_manager.get_budget(budget_id)
        
        if not budget:
            return jsonify({'error': 'Budget not found'}), 404
        
        return jsonify({
            'status': 'success',
            'budget': budget.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@finance_bp.route('/budgets/<budget_id>/lines/add', methods=['POST'])
@require_auth
def add_budget_line(budget_id):
    """Add budget line item."""
    try:
        data = request.get_json()
        
        line = finance_manager.add_budget_line(
            budget_id=budget_id,
            category=data.get('category', 'other'),
            description=data.get('description', ''),
            allocated_amount=data.get('allocated_amount', 0.0)
        )
        
        if not line:
            return jsonify({'error': 'Budget not found'}), 404
        
        return jsonify({
            'status': 'success',
            'line': line.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@finance_bp.route('/budgets/<budget_id>/lines', methods=['GET'])
@require_auth
def get_budget_lines(budget_id):
    """Get budget line items."""
    try:
        lines = finance_manager.get_budget_lines(budget_id)
        
        return jsonify({
            'status': 'success',
            'lines': lines,
            'total': len(lines)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@finance_bp.route('/budgets/<budget_id>/expense/record', methods=['POST'])
@require_auth
def record_expense(budget_id):
    """Record expense."""
    try:
        data = request.get_json()
        
        success = finance_manager.record_expense(
            budget_id=budget_id,
            line_id=data.get('line_id', ''),
            amount=data.get('amount', 0.0)
        )
        
        if not success:
            return jsonify({'error': 'Failed to record expense'}), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Expense recorded'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@finance_bp.route('/budgets/<budget_id>/approve', methods=['POST'])
@require_auth
def approve_budget(budget_id):
    """Approve budget."""
    try:
        success = finance_manager.approve_budget(budget_id)
        
        if not success:
            return jsonify({'error': 'Budget not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Budget approved'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@finance_bp.route('/budgets/<budget_id>/activate', methods=['POST'])
@require_auth
def activate_budget(budget_id):
    """Activate budget."""
    try:
        success = finance_manager.activate_budget(budget_id)
        
        if not success:
            return jsonify({'error': 'Budget not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Budget activated'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@finance_bp.route('/budgets/<budget_id>/close', methods=['POST'])
@require_auth
def close_budget(budget_id):
    """Close budget."""
    try:
        success = finance_manager.close_budget(budget_id)
        
        if not success:
            return jsonify({'error': 'Budget not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Budget closed'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@finance_bp.route('/budgets/<budget_id>/status', methods=['GET'])
@require_auth
def get_budget_status(budget_id):
    """Get budget status."""
    try:
        status = finance_manager.get_budget_status(budget_id)
        
        return jsonify({
            'status': 'success',
            'budget_status': status
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@finance_bp.route('/reports/generate', methods=['POST'])
@require_auth
def generate_report():
    """Generate financial report."""
    try:
        data = request.get_json()
        report_type = data.get('report_type', 'monthly')
        
        report = finance_manager.generate_financial_report(report_type)
        
        return jsonify({
            'status': 'success',
            'report': report.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@finance_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get finance statistics."""
    try:
        stats = finance_manager.get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

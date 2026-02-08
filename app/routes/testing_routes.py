# app/routes/testing_routes.py
"""
QA & Testing Module API Routes
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from app.testing.qa_module import qa_manager


def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


testing_bp = Blueprint('testing', __name__, url_prefix='/api/v1/testing')


@testing_bp.route('/cases/create', methods=['POST'])
@require_auth
def create_test_case():
    """Create test case."""
    try:
        data = request.get_json()
        
        test_case = qa_manager.create_test_case(
            name=data.get('name', ''),
            description=data.get('description', ''),
            test_type=data.get('test_type', 'functional')
        )
        
        return jsonify({
            'status': 'success',
            'test_case': test_case.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@testing_bp.route('/cases/<case_id>', methods=['GET'])
@require_auth
def get_test_case(case_id):
    """Get test case."""
    try:
        test_case = qa_manager.get_test_case(case_id)
        
        if not test_case:
            return jsonify({'error': 'Test case not found'}), 404
        
        return jsonify({
            'status': 'success',
            'test_case': test_case.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@testing_bp.route('/cases/<case_id>/steps', methods=['POST'])
@require_auth
def add_steps(case_id):
    """Add test steps."""
    try:
        data = request.get_json()
        success = qa_manager.add_test_steps(case_id, data.get('steps', []))
        
        if not success:
            return jsonify({'error': 'Test case not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Steps added'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@testing_bp.route('/executions/execute', methods=['POST'])
@require_auth
def execute_test():
    """Execute test case."""
    try:
        data = request.get_json()
        
        execution = qa_manager.execute_test(
            case_id=data.get('case_id', ''),
            executed_by=data.get('executed_by', '')
        )
        
        if not execution:
            return jsonify({'error': 'Test case not found'}), 404
        
        return jsonify({
            'status': 'success',
            'execution': execution.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@testing_bp.route('/executions/<exec_id>/complete', methods=['POST'])
@require_auth
def complete_execution(exec_id):
    """Complete test execution."""
    try:
        data = request.get_json()
        success = qa_manager.complete_execution(
            exec_id=exec_id,
            status=data.get('status', 'passed'),
            notes=data.get('notes', '')
        )
        
        if not success:
            return jsonify({'error': 'Execution not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Execution completed'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@testing_bp.route('/bugs/create', methods=['POST'])
@require_auth
def create_bug():
    """Create bug report."""
    try:
        data = request.get_json()
        
        bug = qa_manager.create_bug(
            title=data.get('title', ''),
            description=data.get('description', ''),
            severity=data.get('severity', 'medium'),
            reported_by=data.get('reported_by', '')
        )
        
        return jsonify({
            'status': 'success',
            'bug': bug.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@testing_bp.route('/bugs/<bug_id>', methods=['GET'])
@require_auth
def get_bug(bug_id):
    """Get bug report."""
    try:
        bug = qa_manager.get_bug(bug_id)
        
        if not bug:
            return jsonify({'error': 'Bug not found'}), 404
        
        return jsonify({
            'status': 'success',
            'bug': bug.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@testing_bp.route('/bugs/<bug_id>/assign', methods=['POST'])
@require_auth
def assign_bug(bug_id):
    """Assign bug."""
    try:
        data = request.get_json()
        success = qa_manager.assign_bug(bug_id, data.get('assigned_to', ''))
        
        if not success:
            return jsonify({'error': 'Bug not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Bug assigned'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@testing_bp.route('/suites/create', methods=['POST'])
@require_auth
def create_suite():
    """Create test suite."""
    try:
        data = request.get_json()
        
        suite = qa_manager.create_test_suite(
            name=data.get('name', ''),
            description=data.get('description', '')
        )
        
        return jsonify({
            'status': 'success',
            'suite': suite.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@testing_bp.route('/coverage', methods=['GET'])
@require_auth
def get_coverage():
    """Get test coverage metrics."""
    try:
        coverage = qa_manager.get_test_coverage()
        
        return jsonify({
            'status': 'success',
            'coverage': coverage
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@testing_bp.route('/bugs/metrics', methods=['GET'])
@require_auth
def get_bug_metrics():
    """Get bug metrics."""
    try:
        metrics = qa_manager.get_bug_metrics()
        
        return jsonify({
            'status': 'success',
            'metrics': metrics
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

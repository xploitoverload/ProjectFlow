"""Workflow Automation Routes - Manage and execute workflows"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime
import logging
import uuid

from app.automation.workflow import (
    workflow_engine,
    Trigger,
    Action,
    TriggerType,
    ActionType,
)

logger = logging.getLogger(__name__)

automation_bp = Blueprint('automation', __name__, url_prefix='/api/v1/automation')


def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# Workflow Management Endpoints
# ============================================================================

@automation_bp.route('/workflows', methods=['GET'])
@require_auth
def list_workflows():
    """List all workflows"""
    try:
        workflows = workflow_engine.get_workflows()
        
        return jsonify({
            'status': 'success',
            'total': len(workflows),
            'workflows': [w.to_dict() for w in workflows],
        }), 200
    except Exception as e:
        logger.error(f"List workflows error: {e}")
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/workflows/<workflow_id>', methods=['GET'])
@require_auth
def get_workflow(workflow_id):
    """Get specific workflow"""
    try:
        workflow = workflow_engine.get_workflow(workflow_id)
        
        if not workflow:
            return jsonify({'error': 'Workflow not found'}), 404
        
        return jsonify({
            'status': 'success',
            'workflow': workflow.to_dict(),
        }), 200
    except Exception as e:
        logger.error(f"Get workflow error: {e}")
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/workflows', methods=['POST'])
@require_auth
def create_workflow():
    """Create new workflow"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        trigger_data = data.get('trigger', {})
        actions_data = data.get('actions', [])
        
        if not name or not trigger_data or not actions_data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create trigger
        trigger = Trigger(
            id=str(uuid.uuid4()),
            type=TriggerType(trigger_data.get('type')),
            conditions=trigger_data.get('conditions', {}),
        )
        
        # Create actions
        actions = []
        for action_data in actions_data:
            action = Action(
                id=str(uuid.uuid4()),
                type=ActionType(action_data.get('type')),
                params=action_data.get('params', {}),
            )
            actions.append(action)
        
        # Create workflow
        workflow = workflow_engine.create_workflow(name, description, trigger, actions)
        
        return jsonify({
            'status': 'success',
            'workflow': workflow.to_dict(),
        }), 201
    except Exception as e:
        logger.error(f"Create workflow error: {e}")
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/workflows/<workflow_id>/enable', methods=['POST'])
@require_auth
def enable_workflow(workflow_id):
    """Enable workflow"""
    try:
        success = workflow_engine.enable_workflow(workflow_id)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'enabled': success,
        }), 200 if success else 404
    except Exception as e:
        logger.error(f"Enable workflow error: {e}")
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/workflows/<workflow_id>/disable', methods=['POST'])
@require_auth
def disable_workflow(workflow_id):
    """Disable workflow"""
    try:
        success = workflow_engine.disable_workflow(workflow_id)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'disabled': success,
        }), 200 if success else 404
    except Exception as e:
        logger.error(f"Disable workflow error: {e}")
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/workflows/<workflow_id>', methods=['DELETE'])
@require_auth
def delete_workflow(workflow_id):
    """Delete workflow"""
    try:
        success = workflow_engine.delete_workflow(workflow_id)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'deleted': success,
        }), 200 if success else 404
    except Exception as e:
        logger.error(f"Delete workflow error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Workflow Execution Endpoints
# ============================================================================

@automation_bp.route('/workflows/trigger', methods=['POST'])
@require_auth
def trigger_workflow():
    """Manually trigger workflow"""
    try:
        data = request.get_json()
        
        trigger_type = data.get('trigger_type')
        event_data = data.get('event_data', {})
        
        if not trigger_type:
            return jsonify({'error': 'Missing trigger_type'}), 400
        
        trigger_type_enum = TriggerType(trigger_type)
        results = workflow_engine.trigger_workflow(trigger_type_enum, event_data)
        
        return jsonify({
            'status': 'success',
            'triggered': len(results),
            'results': results,
        }), 200
    except Exception as e:
        logger.error(f"Trigger workflow error: {e}")
        return jsonify({'error': str(e)}), 500


@automation_bp.route('/workflows/history', methods=['GET'])
@require_auth
def get_execution_history():
    """Get workflow execution history"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        history = workflow_engine.get_execution_history(limit)
        
        return jsonify({
            'status': 'success',
            'total': len(history),
            'history': history,
        }), 200
    except Exception as e:
        logger.error(f"Get history error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Workflow Templates Endpoints
# ============================================================================

@automation_bp.route('/templates', methods=['GET'])
@require_auth
def get_templates():
    """Get workflow templates"""
    try:
        templates = workflow_engine.get_workflow_templates()
        
        return jsonify({
            'status': 'success',
            'total': len(templates),
            'templates': templates,
        }), 200
    except Exception as e:
        logger.error(f"Get templates error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Trigger Types Endpoints
# ============================================================================

@automation_bp.route('/triggers', methods=['GET'])
@require_auth
def list_triggers():
    """List available trigger types"""
    try:
        triggers = [t.value for t in TriggerType]
        
        return jsonify({
            'status': 'success',
            'triggers': triggers,
        }), 200
    except Exception as e:
        logger.error(f"List triggers error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Action Types Endpoints
# ============================================================================

@automation_bp.route('/actions', methods=['GET'])
@require_auth
def list_actions():
    """List available action types"""
    try:
        actions = [a.value for a in ActionType]
        
        return jsonify({
            'status': 'success',
            'actions': actions,
        }), 200
    except Exception as e:
        logger.error(f"List actions error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Health Check
# ============================================================================

@automation_bp.route('/health', methods=['GET'])
def automation_health():
    """Automation system health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'components': {
                'workflow_engine': 'ready',
                'trigger_validator': 'ready',
                'action_executor': 'ready',
            },
            'timestamp': datetime.now().isoformat(),
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

"""Workflow Automation Engine - Drag-drop automation with triggers and actions"""

import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of automation triggers"""
    ISSUE_CREATED = "issue_created"
    ISSUE_STATUS_CHANGED = "issue_status_changed"
    ISSUE_ASSIGNED = "issue_assigned"
    COMMENT_ADDED = "comment_added"
    DEADLINE_APPROACHING = "deadline_approaching"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class ActionType(Enum):
    """Types of automation actions"""
    SEND_NOTIFICATION = "send_notification"
    ASSIGN_TO_USER = "assign_to_user"
    CHANGE_STATUS = "change_status"
    ADD_LABEL = "add_label"
    CREATE_SUBTASK = "create_subtask"
    SEND_EMAIL = "send_email"
    WEBHOOK_CALL = "webhook_call"
    ESCALATE = "escalate"


@dataclass
class Trigger:
    """Workflow trigger"""
    id: str
    type: TriggerType
    conditions: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['type'] = self.type.value
        return data


@dataclass
class Action:
    """Workflow action"""
    id: str
    type: ActionType
    params: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['type'] = self.type.value
        return data


@dataclass
class Workflow:
    """Automation workflow"""
    id: str
    name: str
    description: str
    trigger: Trigger
    actions: List[Action]
    is_enabled: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'trigger': self.trigger.to_dict(),
            'actions': [a.to_dict() for a in self.actions],
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class TriggerValidator:
    """Validate trigger conditions"""
    
    @staticmethod
    def validate_issue_status_condition(issue: Dict, condition: Dict) -> bool:
        """Check if issue status matches condition"""
        expected_status = condition.get('status')
        actual_status = issue.get('status')
        return actual_status == expected_status
    
    @staticmethod
    def validate_priority_condition(issue: Dict, condition: Dict) -> bool:
        """Check if issue priority matches condition"""
        expected_priority = condition.get('priority')
        actual_priority = issue.get('priority')
        
        if condition.get('is_higher_than', False):
            priority_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            return priority_order.get(actual_priority, 0) >= priority_order.get(expected_priority, 0)
        
        return actual_priority == expected_priority
    
    @staticmethod
    def validate_time_condition(issue: Dict, condition: Dict) -> bool:
        """Check if time-based condition matches"""
        created_at = datetime.fromisoformat(issue['created_at']) if isinstance(issue['created_at'], str) else issue['created_at']
        days_open = (datetime.now() - created_at).days
        
        threshold_days = condition.get('days', 0)
        return days_open >= threshold_days
    
    @staticmethod
    def validate_assignment_condition(issue: Dict, condition: Dict) -> bool:
        """Check if assignment matches condition"""
        assignees = set(issue.get('assignees', []))
        
        if condition.get('is_unassigned', False):
            return len(assignees) == 0
        
        required_user = condition.get('assigned_to')
        if required_user:
            return required_user in assignees
        
        return True
    
    @staticmethod
    def validate_trigger(trigger: Trigger, event_data: Dict) -> bool:
        """Check if trigger conditions are met"""
        conditions = trigger.conditions
        
        for condition_key, condition_value in conditions.items():
            if condition_key == 'status':
                if not TriggerValidator.validate_issue_status_condition(event_data, {'status': condition_value}):
                    return False
            elif condition_key == 'priority':
                if not TriggerValidator.validate_priority_condition(event_data, {'priority': condition_value}):
                    return False
            elif condition_key == 'days_open':
                if not TriggerValidator.validate_time_condition(event_data, {'days': condition_value}):
                    return False
        
        return True


class ActionExecutor:
    """Execute workflow actions"""
    
    def __init__(self):
        self.handlers: Dict[ActionType, Callable] = {
            ActionType.SEND_NOTIFICATION: self._send_notification,
            ActionType.ASSIGN_TO_USER: self._assign_to_user,
            ActionType.CHANGE_STATUS: self._change_status,
            ActionType.ADD_LABEL: self._add_label,
            ActionType.CREATE_SUBTASK: self._create_subtask,
            ActionType.SEND_EMAIL: self._send_email,
            ActionType.WEBHOOK_CALL: self._webhook_call,
            ActionType.ESCALATE: self._escalate,
        }
    
    def execute(self, action: Action, context: Dict) -> Dict:
        """Execute an action"""
        handler = self.handlers.get(action.type)
        
        if not handler:
            return {
                'success': False,
                'error': f'Unknown action type: {action.type}',
            }
        
        try:
            result = handler(action.params, context)
            return {
                'success': True,
                'action_id': action.id,
                'result': result,
            }
        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return {
                'success': False,
                'action_id': action.id,
                'error': str(e),
            }
    
    @staticmethod
    def _send_notification(params: Dict, context: Dict) -> Dict:
        """Send notification"""
        return {
            'message': f"Notification sent: {params.get('message', '')}",
            'recipients': params.get('recipients', []),
        }
    
    @staticmethod
    def _assign_to_user(params: Dict, context: Dict) -> Dict:
        """Assign issue to user"""
        return {
            'action': 'assign',
            'user_id': params.get('user_id'),
            'issue_id': context.get('issue_id'),
        }
    
    @staticmethod
    def _change_status(params: Dict, context: Dict) -> Dict:
        """Change issue status"""
        return {
            'action': 'status_change',
            'new_status': params.get('status'),
            'issue_id': context.get('issue_id'),
        }
    
    @staticmethod
    def _add_label(params: Dict, context: Dict) -> Dict:
        """Add label to issue"""
        return {
            'action': 'add_label',
            'label': params.get('label'),
            'issue_id': context.get('issue_id'),
        }
    
    @staticmethod
    def _create_subtask(params: Dict, context: Dict) -> Dict:
        """Create subtask"""
        return {
            'action': 'create_subtask',
            'title': params.get('title'),
            'parent_issue_id': context.get('issue_id'),
        }
    
    @staticmethod
    def _send_email(params: Dict, context: Dict) -> Dict:
        """Send email"""
        return {
            'action': 'send_email',
            'to': params.get('to'),
            'subject': params.get('subject'),
        }
    
    @staticmethod
    def _webhook_call(params: Dict, context: Dict) -> Dict:
        """Call webhook"""
        return {
            'action': 'webhook_call',
            'url': params.get('url'),
            'method': params.get('method', 'POST'),
        }
    
    @staticmethod
    def _escalate(params: Dict, context: Dict) -> Dict:
        """Escalate issue"""
        return {
            'action': 'escalate',
            'escalate_to': params.get('escalate_to'),
            'reason': params.get('reason'),
        }


class WorkflowEngine:
    """Main workflow automation engine"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.trigger_validator = TriggerValidator()
        self.action_executor = ActionExecutor()
        self.execution_history: List[Dict] = []
    
    def create_workflow(self, name: str, description: str, trigger: Trigger, 
                       actions: List[Action]) -> Workflow:
        """Create a new workflow"""
        import uuid
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            trigger=trigger,
            actions=actions,
        )
        
        self.workflows[workflow.id] = workflow
        logger.info(f"Workflow created: {workflow.id} - {name}")
        
        return workflow
    
    def enable_workflow(self, workflow_id: str) -> bool:
        """Enable a workflow"""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].is_enabled = True
            return True
        return False
    
    def disable_workflow(self, workflow_id: str) -> bool:
        """Disable a workflow"""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].is_enabled = False
            return True
        return False
    
    def trigger_workflow(self, trigger_type: TriggerType, event_data: Dict) -> List[Dict]:
        """Trigger matching workflows"""
        results = []
        
        for workflow in self.workflows.values():
            if not workflow.is_enabled:
                continue
            
            if workflow.trigger.type != trigger_type:
                continue
            
            # Check if trigger conditions match
            if not self.trigger_validator.validate_trigger(workflow.trigger, event_data):
                continue
            
            # Execute workflow actions
            execution = self._execute_workflow(workflow, event_data)
            results.append(execution)
        
        return results
    
    def _execute_workflow(self, workflow: Workflow, context: Dict) -> Dict:
        """Execute a workflow"""
        execution = {
            'workflow_id': workflow.id,
            'workflow_name': workflow.name,
            'triggered_at': datetime.now().isoformat(),
            'actions_executed': [],
            'success': True,
        }
        
        for action in workflow.actions:
            result = self.action_executor.execute(action, context)
            execution['actions_executed'].append(result)
            
            if not result.get('success'):
                execution['success'] = False
        
        self.execution_history.append(execution)
        logger.info(f"Workflow executed: {workflow.id}")
        
        return execution
    
    def get_workflows(self) -> List[Workflow]:
        """Get all workflows"""
        return list(self.workflows.values())
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get specific workflow"""
        return self.workflows.get(workflow_id)
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            return True
        return False
    
    def get_execution_history(self, limit: int = 100) -> List[Dict]:
        """Get workflow execution history"""
        return self.execution_history[-limit:]
    
    def get_workflow_templates(self) -> List[Dict]:
        """Get predefined workflow templates"""
        return [
            {
                'name': 'Auto-assign high priority',
                'description': 'Automatically assign high priority issues to senior dev',
                'trigger': {
                    'type': 'issue_created',
                    'conditions': {'priority': 'high'}
                },
                'actions': [
                    {
                        'type': 'assign_to_user',
                        'params': {'user_id': 'senior_dev_id'}
                    }
                ]
            },
            {
                'name': 'Escalate overdue issues',
                'description': 'Escalate issues open for more than 7 days',
                'trigger': {
                    'type': 'scheduled',
                    'conditions': {'check_daily': True}
                },
                'actions': [
                    {
                        'type': 'escalate',
                        'params': {'escalate_to': 'manager'}
                    }
                ]
            },
            {
                'name': 'Notify on assignment',
                'description': 'Send notification when issue is assigned',
                'trigger': {
                    'type': 'issue_assigned',
                    'conditions': {}
                },
                'actions': [
                    {
                        'type': 'send_notification',
                        'params': {'message': 'You have been assigned a new issue'}
                    }
                ]
            },
        ]


# Global workflow engine instance
workflow_engine = WorkflowEngine()

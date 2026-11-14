# tests/test_automation_engine.py
"""
Tests for Workflow Automation Engine and Event-Driven Rules:
Triggers, Actions, Rule Execution, and Automation REST APIs.
"""

import pytest
import uuid
from app.automation.workflow import (
    WorkflowEngine,
    TriggerValidator,
    ActionExecutor,
    Trigger,
    Action,
    TriggerType,
    ActionType
)


class TestWorkflowEngineCore:
    """Test core automation engine primitives."""
    
    def test_trigger_validator_conditions(self):
        """Test trigger conditions matching."""
        # Status condition
        assert TriggerValidator.validate_issue_status_condition(
            {'status': 'todo'}, {'status': 'todo'}
        ) is True
        assert TriggerValidator.validate_issue_status_condition(
            {'status': 'done'}, {'status': 'todo'}
        ) is False
        
        # Priority condition with is_higher_than
        assert TriggerValidator.validate_priority_condition(
            {'priority': 'critical'}, {'priority': 'medium', 'is_higher_than': True}
        ) is True
        assert TriggerValidator.validate_priority_condition(
            {'priority': 'low'}, {'priority': 'high', 'is_higher_than': True}
        ) is False
        
        # Assignment condition
        assert TriggerValidator.validate_assignment_condition(
            {'assignees': ['alice']}, {'assigned_to': 'alice'}
        ) is True
        assert TriggerValidator.validate_assignment_condition(
            {'assignees': []}, {'is_unassigned': True}
        ) is True
    
    def test_workflow_lifecycle_and_execution(self):
        """Test creating, executing, and managing an automation rule."""
        engine = WorkflowEngine()
        
        trigger = Trigger(
            id=str(uuid.uuid4()),
            type=TriggerType.ISSUE_CREATED,
            conditions={'priority': 'critical'}
        )
        action = Action(
            id=str(uuid.uuid4()),
            type=ActionType.CHANGE_STATUS,
            params={'status': 'in_progress'}
        )
        
        wf = engine.create_workflow(
            name='Auto Escalate Critical',
            description='Escalate critical issues immediately',
            trigger=trigger,
            actions=[action]
        )
        assert wf.id in engine.workflows
        assert wf.is_enabled is True
        
        # Trigger matching event
        results = engine.trigger_workflow(
            TriggerType.ISSUE_CREATED,
            {'id': 'ISSUE-1', 'priority': 'critical', 'status': 'todo'}
        )
        assert len(results) == 1
        assert results[0]['success'] is True
        assert len(results[0]['actions_executed']) == 1
        assert results[0]['actions_executed'][0]['success'] is True
        
        # Disable workflow
        assert engine.disable_workflow(wf.id) is True
        assert engine.get_workflow(wf.id).is_enabled is False
        
        # Trigger when disabled should not run
        disabled_results = engine.trigger_workflow(
            TriggerType.ISSUE_CREATED,
            {'id': 'ISSUE-2', 'priority': 'critical', 'status': 'todo'}
        )
        assert len(disabled_results) == 0
        
        # Delete workflow
        assert engine.delete_workflow(wf.id) is True
        assert engine.get_workflow(wf.id) is None


class TestAutomationRESTEndpoints:
    """Test Automation REST API endpoints."""
    
    def test_automation_health_public(self, client):
        """Test automation health endpoint (public)."""
        res = client.get('/api/v1/automation/health')
        assert res.status_code == 200
        data = res.get_json()
        assert data['status'] == 'healthy'
        assert data['components']['workflow_engine'] == 'ready'
    
    def test_list_triggers_and_actions(self, client, auth_headers):
        """Test listing available triggers and actions."""
        res_trig = client.get('/api/v1/automation/triggers', headers=auth_headers)
        assert res_trig.status_code == 200
        data_trig = res_trig.get_json()
        assert 'issue_created' in data_trig['triggers']
        assert 'issue_status_changed' in data_trig['triggers']
        
        res_act = client.get('/api/v1/automation/actions', headers=auth_headers)
        assert res_act.status_code == 200
        data_act = res_act.get_json()
        assert 'change_status' in data_act['actions']
        assert 'send_notification' in data_act['actions']
    
    def test_workflow_templates_and_create(self, client, auth_headers):
        """Test getting workflow templates and creating a workflow via API."""
        # Get templates
        tpl_res = client.get('/api/v1/automation/templates', headers=auth_headers)
        assert tpl_res.status_code == 200
        tpl_data = tpl_res.get_json()
        assert len(tpl_data['templates']) >= 1
        
        # Create workflow
        payload = {
            'name': 'API Test Rule',
            'description': 'Notify on high priority',
            'trigger': {
                'type': 'issue_created',
                'conditions': {'priority': 'high'}
            },
            'actions': [
                {
                    'type': 'send_notification',
                    'params': {'message': 'High priority issue created'}
                }
            ]
        }
        create_res = client.post('/api/v1/automation/workflows', json=payload, headers=auth_headers)
        assert create_res.status_code == 201
        create_data = create_res.get_json()
        assert create_data['status'] == 'success'
        wf_id = create_data['workflow']['id']
        
        # List workflows
        list_res = client.get('/api/v1/automation/workflows', headers=auth_headers)
        assert list_res.status_code == 200
        
        # Disable
        dis_res = client.post(f'/api/v1/automation/workflows/{wf_id}/disable', headers=auth_headers)
        assert dis_res.status_code == 200
        
        # Delete
        del_res = client.delete(f'/api/v1/automation/workflows/{wf_id}', headers=auth_headers)
        assert del_res.status_code == 200

# tests/test_api_v1.py
"""
Tests for ProjectFlow RESTful API (v1):
Cryptographic Bearer token auth, Projects, Issues, Sprints, Epics,
Audit Ledger verification, and Agile analytics.
"""

import pytest
import json
from app.models import db, User, Team, Project, Sprint, Epic, Issue


class TestAuthAndTokenAPI:
    """Test cryptographic Bearer API token generation and verification."""
    
    def test_obtain_token_with_credentials(self, client, auth_user):
        """Test getting bearer token with valid username and password."""
        res = client.post('/api/v1/auth/token', json={
            'username': 'testuser',
            'password': 'SecurePass123!'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert 'token' in data
        assert data['token_type'] == 'Bearer'
        assert data['user']['username'] == 'testuser'
    
    def test_obtain_token_invalid_credentials(self, client):
        """Test rejection of invalid credentials."""
        res = client.post('/api/v1/auth/token', json={
            'username': 'testuser',
            'password': 'WrongPassword123!'
        })
        assert res.status_code == 401
        data = res.get_json()
        assert data['success'] is False
    
    def test_protected_endpoint_without_token(self, client):
        """Test that calling API without token returns 401."""
        res = client.get('/api/v1/projects')
        assert res.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test that calling API with invalid bearer token returns 401."""
        res = client.get('/api/v1/projects', headers={
            'Authorization': 'Bearer invalid.forged.signature'
        })
        assert res.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self, client, auth_headers):
        """Test that calling API with valid bearer token succeeds."""
        res = client.get('/api/v1/projects', headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True


class TestProjectsAndIssuesAPI:
    """Test RESTful project and issue lifecycle operations via API."""
    
    def test_create_and_get_project_api(self, client, auth_headers):
        """Test creating a project via API and retrieving it."""
        payload = {
            'name': 'Kernel Hypervisor Module',
            'key': 'KHM',
            'description': 'Type-1 bare-metal hypervisor tracking',
            'status': 'Active',
            'workflow_type': 'agile'
        }
        create_res = client.post('/api/v1/projects', json=payload, headers=auth_headers)
        assert create_res.status_code == 201
        create_data = create_res.get_json()
        assert create_data['success'] is True
        project_id = create_data['data']['id']
        assert create_data['data']['key'] == 'KHM'
        
        # Get project details
        get_res = client.get(f'/api/v1/project/{project_id}', headers=auth_headers)
        assert get_res.status_code == 200
        get_data = get_res.get_json()
        assert get_data['data']['name'] == 'Kernel Hypervisor Module'
    
    def test_create_and_list_issues_api(self, client, auth_headers, test_project, auth_user):
        """Test creating an issue in a project and listing issues."""
        issue_payload = {
            'title': 'Audit VMCS memory layout',
            'description': 'Ensure strict EPT protection and no guest memory leaks',
            'issue_type': 'story',
            'priority': 'high',
            'status': 'todo',
            'story_points': 5,
            'assignee_id': auth_user.id
        }
        create_res = client.post(
            f'/api/v1/project/{test_project.id}/issues',
            json=issue_payload,
            headers=auth_headers
        )
        assert create_res.status_code == 201
        issue_data = create_res.get_json()
        assert issue_data['success'] is True
        assert issue_data['data']['title'] == 'Audit VMCS memory layout'
        assert issue_data['data']['story_points'] == 5
        
        # List issues for project
        list_res = client.get(f'/api/v1/project/{test_project.id}/issues', headers=auth_headers)
        assert list_res.status_code == 200
        list_data = list_res.get_json()
        assert len(list_data['data']) >= 1
    
    def test_update_issue_status_api(self, client, auth_headers, test_project, test_issue):
        """Test updating issue status via API."""
        update_res = client.post(
            f'/api/v1/project/{test_project.id}/issue/{test_issue.id}/update_status',
            json={'status': 'in_progress', 'comment': 'Work started on issue'},
            headers=auth_headers
        )
        assert update_res.status_code == 200
        update_data = update_res.get_json()
        assert update_data['success'] is True
        assert update_data['data']['new_status'] == 'in_progress'
    
    def test_add_issue_comment_api(self, client, auth_headers, test_project, test_issue):
        """Test posting an encrypted comment to an issue via API."""
        comment_res = client.post(
            f'/api/v1/project/{test_project.id}/issue/{test_issue.id}/comment',
            json={'text': 'Ring 0 memory isolation verified with hardware counters.'},
            headers=auth_headers
        )
        assert comment_res.status_code == 201
        comment_data = comment_res.get_json()
        assert comment_data['success'] is True
        assert 'Ring 0 memory isolation' in comment_data['data']['text']


class TestSprintsAndEpicsAPI:
    """Test Agile Sprints and Epics endpoints."""
    
    def test_manage_sprints_api(self, client, auth_headers, test_project):
        """Test creating and retrieving sprints via API."""
        sprint_payload = {
            'name': 'Sprint 42 - Memory Safety',
            'goal': 'Zero out-of-bounds array indexing in kernel drivers',
            'status': 'active'
        }
        create_res = client.post(
            f'/api/v1/project/{test_project.id}/sprints',
            json=sprint_payload,
            headers=auth_headers
        )
        assert create_res.status_code == 201
        data = create_res.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'Sprint 42 - Memory Safety'
        
        # Get sprints list
        get_res = client.get(f'/api/v1/project/{test_project.id}/sprints', headers=auth_headers)
        assert get_res.status_code == 200
        sprints_data = get_res.get_json()
        assert len(sprints_data['data']) >= 1
    
    def test_manage_epics_api(self, client, auth_headers, test_project):
        """Test creating and retrieving epics via API."""
        epic_payload = {
            'name': 'Formal Verification Suite',
            'description': 'SMT-based invariants check',
            'color': '#3b82f6',
            'status': 'active'
        }
        create_res = client.post(
            f'/api/v1/project/{test_project.id}/epics',
            json=epic_payload,
            headers=auth_headers
        )
        assert create_res.status_code == 201
        data = create_res.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'Formal Verification Suite'
        
        # Get epics list
        get_res = client.get(f'/api/v1/project/{test_project.id}/epics', headers=auth_headers)
        assert get_res.status_code == 200
        epics_data = get_res.get_json()
        assert len(epics_data['data']) >= 1


class TestAuditLedgerAndAnalyticsAPI:
    """Test cryptographic SHA-256 ledger integrity verification and analytics."""
    
    def test_verify_audit_ledger_endpoint(self, client, auth_headers):
        """Test cryptographic SHA-256 audit ledger verification endpoint."""
        res = client.get('/api/v1/audit/ledger/verify', headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['verified'] is True
        assert 'total_records' in data
        assert 'latency_ms' in data
        assert data['latency_ms'] >= 0
    
    def test_agile_burndown_and_velocity_analytics(self, client, auth_headers, test_project):
        """Test burndown and velocity endpoints."""
        # Create an active sprint first
        client.post(
            f'/api/v1/project/{test_project.id}/sprints',
            json={'name': 'Sprint Alpha', 'status': 'active'},
            headers=auth_headers
        )
        
        # Burndown
        bd_res = client.get(f'/api/v1/analytics/burndown/{test_project.id}', headers=auth_headers)
        assert bd_res.status_code == 200
        bd_data = bd_res.get_json()
        assert bd_data['success'] is True
        assert 'total_story_points' in bd_data['data']
        
        # Velocity
        vel_res = client.get(f'/api/v1/analytics/velocity/{test_project.id}', headers=auth_headers)
        assert vel_res.status_code == 200
        vel_data = vel_res.get_json()
        assert vel_data['success'] is True
        assert 'average_velocity' in vel_data['data']

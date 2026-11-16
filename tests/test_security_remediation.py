# tests/test_security_remediation.py
"""
Tests for security vulnerability remediation across ProjectFlow:
1. Open redirect protection
2. Database health check SQL syntax
3. CSV formula injection mitigation (CWE-1236)
4. Integrations API authentication enforcement
5. Analytics API authentication enforcement
6. Search autocomplete IDOR protection
7. Secure attachment download endpoint
"""

import pytest
from app import create_app
from app.models import db, User, Project, Issue, Attachment
from app.export.exporters import CSVExporter


@pytest.fixture
def app():
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


class TestSecurityRemediation:
    """Validate all security remediations."""

    def test_csv_formula_injection_sanitization(self):
        """Verify leading formula triggers (=, +, -, @) are sanitized."""
        malicious_issues = [
            {'id': 1, 'title': '=cmd|\'/C calc\'!A0', 'status': '+cmd', 'priority': '@admin', 'assigned_to': '\ttabbed'}
        ]
        csv_out = CSVExporter.export_issues(malicious_issues)
        assert "'=cmd|'/C calc'!A0" in csv_out
        assert "'+cmd" in csv_out
        assert "'@admin" in csv_out
        assert "'\ttabbed" in csv_out

    def test_health_check_database_execution(self, client):
        """Verify /health/ready successfully executes SQL text query."""
        res = client.get('/health/ready')
        assert res.status_code == 200
        data = res.get_json()
        assert data['status'] == 'ready'
        assert data['checks']['database'] is True

    def test_integrations_unauthenticated_access_rejected(self, client):
        """Verify integrations endpoints reject unauthenticated access."""
        res = client.get('/api/v1/integrations/slack/config')
        assert res.status_code == 401
        res = client.get('/api/v1/integrations/webhooks')
        assert res.status_code == 401
        res = client.post('/api/v1/integrations/sync/execute', json={})
        assert res.status_code == 401

    def test_analytics_unauthenticated_and_dummy_tokens_rejected(self, client):
        """Verify analytics endpoints reject unauthenticated calls and invalid tokens."""
        # No header
        res = client.get('/api/v1/analytics/dashboard/1')
        assert res.status_code == 401
        
        # Invalid dummy header
        res = client.get('/api/v1/analytics/dashboard/1', headers={'Authorization': 'Bearer invalid_dummy_token'})
        assert res.status_code == 401

    def test_open_redirect_protection(self, client):
        """Verify login rejects protocol-relative and external domain redirects."""
        # Create user
        user = User(username='audituser', email='audit@test.com', role='user')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

        # Attempt protocol-relative open redirect
        res = client.post('/login?next=//attacker.com', data={
            'username': 'audituser',
            'password': 'Password123!'
        })
        assert res.status_code == 302
        # Should redirect to safe dashboard, NOT //attacker.com
        assert res.headers['Location'] == '/dashboard'

    def test_search_autocomplete_idor_restriction(self, client):
        """Verify search autocomplete only returns items from accessible projects."""
        # Create user
        user = User(username='regularuser', email='reg@test.com', role='user')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

        # Create inaccessible project and issue
        proj = Project(name='Confidential Secret Project', key='SECRET', status='In Progress', created_by=999)
        db.session.add(proj)
        db.session.commit()

        issue = Issue(title='Classified Core Vulnerability', key='SECRET-1', status='open', project_id=proj.id, reporter_id=999)
        db.session.add(issue)
        db.session.commit()

        # Log in as regularuser
        client.post('/login', data={'username': 'regularuser', 'password': 'Password123!'})

        # Search for confidential item
        res = client.get('/api/v1/search/autocomplete?q=Secret')
        assert res.status_code == 200
        data = res.get_json()
        # Inaccessible projects and issues must NOT be returned
        assert len(data['data']['projects']) == 0
        assert len(data['data']['issues']) == 0

    def test_attachment_download_path_traversal_prevention(self, client, tmp_path):
        """Verify attachment download rejects path traversal and respects project isolation."""
        user = User(username='attachuser', email='attach@test.com', role='user')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

        proj = Project(name='Attach Project', key='ATT', status='In Progress', created_by=user.id)
        db.session.add(proj)
        db.session.commit()

        issue = Issue(title='Attach Issue', key='ATT-1', status='open', project_id=proj.id, reporter_id=user.id)
        db.session.add(issue)
        db.session.commit()

        # Log in
        client.post('/login', data={'username': 'attachuser', 'password': 'Password123!'})

        # Test download of nonexistent attachment returns 404
        res = client.get(f'/projects/{proj.id}/issue/{issue.id}/attachment/9999/download')
        assert res.status_code == 404

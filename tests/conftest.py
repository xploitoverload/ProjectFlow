# tests/conftest.py
"""
Pytest configuration and fixtures for test suite.
"""

import pytest
import os
from app import create_app
from app.models import db, User, Project, Issue, Team, Sprint, Epic


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    """Test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def auth_user(app):
    """Create and return a test user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            role='employee'
        )
        user.set_password('SecurePass123!')
        db.session.add(user)
        db.session.commit()
        # Expunge or return detached object
        db.session.refresh(user)
        return user


@pytest.fixture
def admin_user(app):
    """Create and return a test admin user."""
    with app.app_context():
        user = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        user.set_password('AdminPass123!')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def auth_headers(app, auth_user):
    """Get auth headers with signed bearer token."""
    with app.app_context():
        from app.services.auth_service import AuthService
        token = AuthService.generate_bearer_token(auth_user)
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }


@pytest.fixture
def admin_headers(app, admin_user):
    """Get admin auth headers with signed bearer token."""
    with app.app_context():
        from app.services.auth_service import AuthService
        token = AuthService.generate_bearer_token(admin_user)
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }


@pytest.fixture
def test_project(app, auth_user):
    """Create and return a test project."""
    with app.app_context():
        project = Project(
            name='Test Project',
            key='TST',
            description='Test Description',
            created_by=auth_user.id,
            lead_id=auth_user.id,
            status='active'
        )
        db.session.add(project)
        db.session.commit()
        db.session.refresh(project)
        return project


@pytest.fixture
def test_issue(app, test_project, auth_user):
    """Create and return a test issue."""
    with app.app_context():
        issue = Issue(
            key='TST-1',
            title='Test Issue',
            description='Test Issue Description',
            project_id=test_project.id,
            status='todo',
            priority='high',
            reporter_id=auth_user.id,
            assignee_id=auth_user.id
        )
        db.session.add(issue)
        db.session.commit()
        db.session.refresh(issue)
        return issue

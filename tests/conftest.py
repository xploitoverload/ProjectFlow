# tests/conftest.py
"""
Pytest configuration and fixtures for test suite.
"""

import pytest
import os
import tempfile
from app import create_app
from app.models import db, User, Project, Issue
from datetime import datetime


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    # Create a temporary database in temp directory
    db_dir = tempfile.gettempdir()
    db_path = os.path.join(db_dir, 'test_pm_db.db')
    
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    # Clean up
    try:
        os.unlink(db_path)
    except:
        pass


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
        return user


@pytest.fixture
def auth_headers(client, auth_user):
    """Get auth headers by logging in."""
    response = client.post(
        '/login',
        data={'username': 'testuser', 'password': 'SecurePass123!'},
        follow_redirects=True
    )
    return {'Authorization': f'Bearer {response.get_json().get("token")}'}


@pytest.fixture
def test_project(app, auth_user):
    """Create and return a test project."""
    with app.app_context():
        project = Project(
            name='Test Project',
            description='Test Description',
            owner_id=auth_user.id,
            status='active'
        )
        db.session.add(project)
        db.session.commit()
        return project


@pytest.fixture
def test_issue(app, test_project, auth_user):
    """Create and return a test issue."""
    with app.app_context():
        issue = Issue(
            title='Test Issue',
            description='Test Issue Description',
            project_id=test_project.id,
            status='pending',
            priority='high',
            created_by=auth_user.id,
            assignee_id=auth_user.id
        )
        db.session.add(issue)
        db.session.commit()
        return issue

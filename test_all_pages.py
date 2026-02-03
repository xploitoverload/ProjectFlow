#!/usr/bin/env python
"""
Comprehensive page testing script to identify all errors and crashes.
Tests all user and admin pages recursively.
"""

import os
import sys
from app import create_app, db
from app.models import User, Team, Project, Issue, Label, Sprint, Epic
from flask import session

app = create_app('development')

def create_test_data():
    """Create sample data for testing."""
    with app.app_context():
        db.create_all()
        
        # Clear existing data
        User.query.delete()
        Team.query.delete()
        Project.query.delete()
        Issue.query.delete()
        Label.query.delete()
        
        # Create test team
        team = Team(name='Test Team', description='Test team')
        db.session.add(team)
        db.session.commit()
        
        # Create test users
        admin_user = User(
            username='admin',
            email='admin@test.com',
            full_name='Admin User',
            role='admin',
            team_id=team.id
        )
        admin_user.set_password('admin123')
        
        user1 = User(
            username='user1',
            email='user1@test.com',
            full_name='User One',
            role='user',
            team_id=team.id
        )
        user1.set_password('user123')
        
        user2 = User(
            username='user2',
            email='user2@test.com',
            full_name='User Two',
            role='user',
            team_id=team.id
        )
        user2.set_password('user123')
        
        db.session.add_all([admin_user, user1, user2])
        db.session.commit()
        
        # Create test projects
        project1 = Project(
            name='Test Project 1',
            key='TP1',
            description='Test project 1',
            team_id=team.id,
            status='Active',
            created_by=admin_user.id
        )
        
        project2 = Project(
            name='Test Project 2',
            key='TP2',
            description='Test project 2',
            team_id=team.id,
            status='Planning',
            created_by=admin_user.id
        )
        
        db.session.add_all([project1, project2])
        db.session.commit()
        
        # Create test issues
        issue1 = Issue(
            key='TP1-1',
            title='Test Issue 1',
            description='Test issue 1 description',
            project_id=project1.id,
            status='open',
            priority='high',
            issue_type='bug',
            reporter_id=user1.id,
            assignee_id=user2.id
        )
        
        issue2 = Issue(
            key='TP1-2',
            title='Test Issue 2',
            description='Test issue 2 description',
            project_id=project1.id,
            status='todo',
            priority='medium',
            issue_type='task',
            reporter_id=user2.id,
            assignee_id=user1.id
        )
        
        db.session.add_all([issue1, issue2])
        db.session.commit()
        
        # Create test labels
        label = Label(
            name='Bug',
            color='#ff0000',
            project_id=project1.id
        )
        db.session.add(label)
        db.session.commit()
        
        print("✓ Test data created successfully")
        return admin_user, user1, user2, project1, project2, issue1, issue2

def test_pages():
    """Test all pages for errors."""
    # Create and test data inline to avoid session issues
    with app.app_context():
        admin_user, user1, user2, project1, project2, issue1, issue2 = create_test_data()
        
        # Get the IDs before session closes
        admin_id = admin_user.id
        user1_id = user1.id
        user2_id = user2.id
        project1_id = project1.id
        project2_id = project2.id
        issue1_id = issue1.id
        issue2_id = issue2.id
    
    test_results = {
        'passed': [],
        'failed': [],
        'errors': []
    }
    
    with app.test_client() as client:
        print("\n" + "="*80)
        print("TESTING USER PAGES")
        print("="*80)
        
        # Login as user1
        response = client.post('/auth/login', data={
            'username': 'user1',
            'password': 'user123'
        }, follow_redirects=True)
        
        pages_to_test = [
            ('/', 'home'),
            ('/dashboard', 'dashboard'),
            ('/profile', 'profile'),
            ('/settings', 'settings'),
            ('/issues', 'issues'),
            ('/reports', 'reports'),
            (f'/projects/{project1_id}', 'project_detail'),
            (f'/projects/{project1_id}/kanban', 'kanban'),
            (f'/projects/{project1_id}/issue/{issue1_id}', 'issue_detail'),
            ('/calendar', 'calendar'),
            ('/gantt', 'gantt'),
        ]
        
        for route, name in pages_to_test:
            try:
                response = client.get(route, follow_redirects=True)
                if response.status_code == 200:
                    print(f"✓ {name.upper():20} - {route}")
                    test_results['passed'].append(name)
                else:
                    print(f"✗ {name.upper():20} - {route} (Status: {response.status_code})")
                    test_results['failed'].append((name, response.status_code))
            except Exception as e:
                print(f"✗ {name.upper():20} - {route} (ERROR: {str(e)})")
                test_results['errors'].append((name, str(e)))
        
        print("\n" + "="*80)
        print("TESTING ADMIN PAGES")
        print("="*80)
        
        # Login as admin
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        admin_pages = [
            ('/admin/', 'admin_dashboard'),
            ('/admin/users', 'admin_users'),
            ('/admin/teams', 'admin_teams'),
            ('/admin/projects', 'admin_projects'),
            ('/admin/audit', 'admin_audit'),
        ]
        
        for route, name in admin_pages:
            try:
                response = client.get(route, follow_redirects=True)
                if response.status_code == 200:
                    print(f"✓ {name.upper():20} - {route}")
                    test_results['passed'].append(name)
                else:
                    print(f"✗ {name.upper():20} - {route} (Status: {response.status_code})")
                    test_results['failed'].append((name, response.status_code))
            except Exception as e:
                print(f"✗ {name.upper():20} - {route} (ERROR: {str(e)})")
                test_results['errors'].append((name, str(e)))
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Passed: {len(test_results['passed'])}")
    print(f"Failed: {len(test_results['failed'])}")
    print(f"Errors: {len(test_results['errors'])}")
    
    if test_results['failed']:
        print("\nFailed pages:")
        for name, code in test_results['failed']:
            print(f"  - {name}: {code}")
    
    if test_results['errors']:
        print("\nError pages:")
        for name, error in test_results['errors']:
            print(f"  - {name}: {error}")
    
    return test_results

if __name__ == '__main__':
    results = test_pages()
    sys.exit(0 if not (results['failed'] or results['errors']) else 1)

#!/usr/bin/env python3
"""Direct test of CSRF preservation fix in auth service."""

import sys
import os
sys.path.insert(0, os.getcwd())

from app import create_app, db
from app.models import User, Project, Issue
from flask import session

app = create_app()

with app.app_context():
    # Find a user with password123 that has project access
    user = User.query.filter_by(username='john_doe').first()
    if not user:
        print("User not found")
        exit(1)
    
    # Simulate login: set up a session like the login route does
    with app.test_client() as client:
        print("[1] Get login page...")
        resp = client.get('/login')
        print(f"    Status: {resp.status_code}")
        
        # Extract CSRF token from login form
        import re
        csrf_match = re.search(r'name=["\']csrf_token["\'][^>]+value=["\']([^"\']+)["\']', resp.get_data(as_text=True))
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"    CSRF token: {csrf_token[:20]}...")
        else:
            print("    No CSRF token found!")
            exit(1)
        
        print("\n[2] Log in...")
        resp = client.post('/login', data={
            'username': 'john_doe',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        print(f"    Status: {resp.status_code}")
        print(f"    Response contains 'Welcome': {'Welcome' in resp.get_data(as_text=True)}")
        print(f"    Response contains 'dashboard': {'dashboard' in resp.get_data(as_text=True)}")
        
        # Get a project page
        print("\n[3] Get project/1/...")
        resp = client.get('/project/1/', follow_redirects=False)
        print(f"    Status: {resp.status_code}")
        if resp.status_code == 403:
            print("    403 Forbidden - user doesn't have access")
            # Try project/2 instead
            print("\n[3b] Get project/2/...")
            resp = client.get('/project/2/', follow_redirects=False)
            print(f"    Status: {resp.status_code}")
        
        # Select which project to use
        project_id = 1 if resp.status_code == 200 else 2
        csrf_match = re.search(r'name=["\']csrf_token["\'][^>]+value=["\']([^"\']+)["\']', resp.get_data(as_text=True))
        if csrf_match:
            csrf_token_project = csrf_match.group(1)
            print(f"    CSRF token on project: {csrf_token_project[:20]}...")
        else:
            print("    No CSRF token found on project!")
        
        print("\n[4] Create issue...")
        resp = client.post(f'/project/{project_id}/issue/add', data={
            'title': 'Test Issue',
            'description': 'Test description',
            'priority': 'high',
            'status': 'open',
            'csrf_token': csrf_token_project
        }, follow_redirects=False)
        print(f"    Status: {resp.status_code}")
        if resp.status_code == 302:
            print(f"    Redirect: {resp.headers.get('Location')}")
            if '/login' in resp.headers.get('Location', ''):
                print("    ❌ User was redirected to login (session lost)")
            else:
                print("    ✅ Redirect to project kanban (success)")
        elif resp.status_code == 200:
            print("    Form response 200 - checking for issue...")
            if 'Test Issue' in resp.get_data(as_text=True):
                print("    ✅ Issue found in response")
        else:
            print(f"    ❌ Unexpected status {resp.status_code}")
        
        print("\n[5] Verify issue was created...")
        issue = Issue.query.filter_by(title='Test Issue').first()
        if issue:
            print(f"    ✅ Issue created in database!")
            print(f"       ID: {issue.id}, Key: {issue.key}, Status: {issue.status}")
        else:
            print("    ❌ Issue not found in database")

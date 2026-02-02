#!/usr/bin/env python3
"""Proper CSRF testing - use Flask-WTF's test utilities."""

import sys, os
sys.path.insert(0, os.getcwd())

from app import create_app, db
from app.models import Issue
from flask_wtf.csrf import generate_csrf

app = create_app()

def test_issue_creation():
    """Test issue creation with proper CSRF handling."""
    with app.test_client() as client:
        print("=" * 60)
        print("Testing Issue Creation - Proper CSRF Handling")
        print("=" * 60)
        
        # Step 1: Get login page - this initializes session with CSRF token
        print("\n[1] Getting login page...")
        resp = client.get('/login')
        print(f"    Status: {resp.status_code}")
        print(f"    ✓ Session initialized")
        
        # Step 2: Log in with CSRF token from session
        print("\n[2] Logging in...")
        # Get CSRF token from the session context
        with client.session_transaction() as sess:
            csrf = generate_csrf(sess)
            print(f"    CSRF token from session: {csrf[:30]}...")
        
        # Post login with CSRF
        resp = client.post('/login', data={
            'username': 'john_doe',
            'password': 'password123',
            'csrf_token': csrf
        }, follow_redirects=False)
        
        print(f"    Login response: {resp.status_code}")
        if resp.status_code == 302:
            print(f"    ✓ Redirected to: {resp.headers.get('Location')}")
        
        # Get the CSRF token for the next request
        with client.session_transaction() as sess:
            csrf_post_login = generate_csrf(sess)
            print(f"    CSRF after login: {csrf_post_login[:30]}...")
        
        # Step 3: Get project page
        print("\n[3] Getting project page...")
        resp = client.get('/project/1')
        print(f"    Status: {resp.status_code}")
        
        # Get CSRF token for form submission
        with client.session_transaction() as sess:
            csrf_project = generate_csrf(sess)
            print(f"    CSRF on project page: {csrf_project[:30]}...")
        
        # Step 4: Submit issue creation form
        print("\n[4] Submitting issue form...")
        resp = client.post('/project/1/issue/add', data={
            'title': 'Proper CSRF Test Issue',
            'description': 'Testing with proper CSRF handling',
            'priority': 'medium',
            'issue_type': 'task',
            'status': 'open',
            'csrf_token': csrf_project
        }, follow_redirects=False)
        
        print(f"    Status: {resp.status_code}")
        if resp.status_code == 302:
            print(f"    ✓ Redirected to: {resp.headers.get('Location')}")
        else:
            print(f"    Response: {resp.get_data(as_text=True)[:200]}")
        
        # Step 5: Check database
        print("\n[5] Checking database...")
        with app.app_context():
            issue = Issue.query.filter_by(title='Proper CSRF Test Issue').first()
            if issue:
                print(f"    ✓ ISSUE CREATED: {issue.key}")
                return True
            else:
                print(f"    ✗ Issue not found")
                # Show recent issues
                recent = Issue.query.order_by(Issue.id.desc()).limit(3).all()
                print(f"    Recent issues: {[i.key for i in recent]}")
                return False

if __name__ == '__main__':
    success = test_issue_creation()
    print("\n" + "=" * 60)
    print(f"Result: {'✓ SUCCESS' if success else '✗ FAILED'}")
    print("=" * 60)
    sys.exit(0 if success else 1)

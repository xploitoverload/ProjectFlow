#!/usr/bin/env python3
"""Debug issue creation with full logging."""

import sys, os
sys.path.insert(0, os.getcwd())

from app import create_app, db
from app.models import Issue
from flask_wtf.csrf import generate_csrf
import logging

# Configure logging to see all messages
logging.basicConfig(level=logging.DEBUG, format='[%(name)s] %(levelname)s: %(message)s')

# Also set up Flask app logging
import warnings
logging.getLogger('werkzeug').setLevel(logging.ERROR)  # Suppress werkzeug logs
logging.getLogger('sqlalchemy').setLevel(logging.INFO)

app = create_app()

def test_issue_creation():
    """Test issue creation with debugging."""
    with app.test_client() as client:
        print("=" * 60)
        print("Testing Issue Creation - Debug Mode")
        print("=" * 60)
        
        # Login
        print("\n[1] Logging in...")
        client.get('/login')
        with client.session_transaction() as sess:
            csrf = generate_csrf(sess)
        
        resp = client.post('/login', data={
            'username': 'john_doe',
            'password': 'password123',
            'csrf_token': csrf
        }, follow_redirects=False)
        print(f"    ✓ Login: {resp.status_code}")
        
        # Get project page
        print("\n[2] Getting project page...")
        resp = client.get('/project/1')
        print(f"    Status: {resp.status_code}")
        
        with client.session_transaction() as sess:
            csrf_project = generate_csrf(sess)
        
        # Now test the actual submission
        print("\n[3] Submitting issue form with debugging...")
        print("    Form data:")
        form_data = {
            'title': 'Debug Issue',
            'description': 'Debug test',
            'priority': 'medium',
            'issue_type': 'task',
            'status': 'open',
            'csrf_token': csrf_project
        }
        for k, v in form_data.items():
            print(f"      {k}: {v}")
        
        # Capture the response
        resp = client.post('/project/1/issue/add', data=form_data, follow_redirects=False)
        print(f"\n    Response Status: {resp.status_code}")
        if resp.status_code != 302:
            print(f"    Response Body:\n{resp.get_data(as_text=True)}")
        else:
            print(f"    ✓ Redirected to: {resp.headers.get('Location')}")
        
        # Check if issue exists
        print("\n[4] Checking database...")
        with app.app_context():
            issue = Issue.query.filter_by(title='Debug Issue').first()
            print(f"    Query result: {issue}")
            if issue:
                print(f"    ✓ Issue created: {issue.key}")
                print(f"    Issue details: title={issue.title}, project_id={issue.project_id}, reporter_id={issue.reporter_id}")
            else:
                print(f"    ✗ Issue not found")
                # Check all issues for the project
                all_issues = Issue.query.filter_by(project_id=1).all()
                print(f"    All issues in project 1: {[i.key for i in all_issues]}")

if __name__ == '__main__':
    test_issue_creation()

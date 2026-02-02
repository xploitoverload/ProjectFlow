#!/usr/bin/env python3
"""
Real-world simulation: User workflow test
Simulates a real user logging in and creating multiple issues.
"""

import sys, os
sys.path.insert(0, os.getcwd())

from app import create_app, db
from app.models import Issue, User
from flask_wtf.csrf import generate_csrf

app = create_app()

def simulate_user_workflow():
    """Simulate a typical user workflow."""
    with app.test_client() as client:
        print("\n" + "=" * 70)
        print("REAL-WORLD SIMULATION: User Workflow Test")
        print("=" * 70)
        
        # User 1: john_doe
        print("\n[USER 1] John Doe logging in...")
        client.get('/login')
        with client.session_transaction() as sess:
            csrf = generate_csrf(sess)
        
        resp = client.post('/login', data={
            'username': 'john_doe',
            'password': 'password123',
            'csrf_token': csrf
        }, follow_redirects=False)
        
        assert resp.status_code == 302, "Login failed"
        print("    ✓ Login successful")
        
        # John creates several issues
        issues_created = []
        test_issues = [
            ('User Feature Request One', 'low', 'task'),
            ('User Feature Request Two', 'medium', 'bug'),
            ('User Feature Request Three', 'high', 'feature'),
        ]
        
        for i, (title, priority, issue_type) in enumerate(test_issues, 1):
            print(f"\n  [ISSUE {i}] Creating: {title}...")
            
            # Navigate to project
            client.get('/project/1')
            
            with client.session_transaction() as sess:
                csrf = generate_csrf(sess)
            
            # Create issue
            resp = client.post('/project/1/issue/add', data={
                'title': title,
                'description': f'Description for {title}',
                'priority': priority,
                'issue_type': issue_type,
                'status': 'open',
                'csrf_token': csrf
            }, follow_redirects=False)
            
            assert resp.status_code == 302, f"Issue creation failed: {resp.status_code}"
            
            # Verify it was created
            with app.app_context():
                issue = Issue.query.filter_by(title=title, project_id=1).first()
                assert issue, f"Issue not found in database: {title}"
                issues_created.append(issue.key)
                print(f"    ✓ Created: {issue.key} - {issue.title}")
        
        # Logout (simulate session end)
        client.get('/logout')
        print("\n  [LOGOUT] User logged out")
        
        return issues_created

if __name__ == '__main__':
    try:
        issues = simulate_user_workflow()
        
        print("\n" + "=" * 70)
        print(f"WORKFLOW COMPLETE")
        print("=" * 70)
        print(f"\nIssues created in this session:")
        for i, issue_key in enumerate(issues, 1):
            print(f"  {i}. {issue_key}")
        
        print(f"\nTotal issues in project 1:")
        with app.app_context():
            count = Issue.query.filter_by(project_id=1).count()
            print(f"  {count} issues (including previously created)")
        
        print("\n" + "=" * 70)
        print("✓ WORKFLOW SIMULATION SUCCESSFUL")
        print("✓ All user operations completed without errors")
        print("=" * 70 + "\n")
        
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n✗ WORKFLOW FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

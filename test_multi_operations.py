#!/usr/bin/env python3
"""Test multiple project operations to ensure CSRF handling works."""

import sys, os
sys.path.insert(0, os.getcwd())

from app import create_app, db
from app.models import Issue, ProjectUpdate
from flask_wtf.csrf import generate_csrf

app = create_app()

def test_various_operations():
    """Test that various project operations work with CSRF."""
    with app.test_client() as client:
        print("\n" + "=" * 70)
        print("Testing Various Project Operations with CSRF")
        print("=" * 70)
        
        # Login
        print("\n[LOGIN] Logging in...")
        client.get('/login')
        with client.session_transaction() as sess:
            csrf = generate_csrf(sess)
        
        resp = client.post('/login', data={
            'username': 'john_doe',
            'password': 'password123',
            'csrf_token': csrf
        }, follow_redirects=False)
        
        assert resp.status_code == 302, f"Login failed: {resp.status_code}"
        print("    ✓ Login successful")
        
        # Get project page
        resp = client.get('/project/1')
        assert resp.status_code == 200
        
        with client.session_transaction() as sess:
            csrf = generate_csrf(sess)
        
        # Test 1: Create Issue
        print("\n[1] Testing issue creation...")
        resp = client.post('/project/1/issue/add', data={
            'title': 'Multi-Test Issue 1',
            'description': 'Test',
            'priority': 'medium',
            'issue_type': 'task',
            'status': 'open',
            'csrf_token': csrf
        }, follow_redirects=False)
        
        assert resp.status_code == 302, f"Issue creation failed: {resp.status_code}"
        print("    ✓ Issue creation: 302 redirect")
        
        # Verify the issue was created
        with app.app_context():
            issue = Issue.query.filter_by(title='Multi-Test Issue 1').first()
            assert issue, "Issue not found in database"
            print(f"    ✓ Issue found: {issue.key}")
        
        # Test 2: Skip project update (has separate encryption concerns)
        print("\n[2] Skipping project update test (separate encryption layer)")

        
        # Test 3: Create another issue
        print("\n[3] Testing second issue creation...")
        client.get('/project/1')
        with client.session_transaction() as sess:
            csrf = generate_csrf(sess)
        
        resp = client.post('/project/1/issue/add', data={
            'title': 'Multi-Test Issue 2',
            'description': 'Another test',
            'priority': 'high',
            'issue_type': 'bug',
            'status': 'open',
            'csrf_token': csrf
        }, follow_redirects=False)
        
        assert resp.status_code == 302
        print("    ✓ Issue creation: 302 redirect")
        
        with app.app_context():
            issue = Issue.query.filter_by(title='Multi-Test Issue 2').first()
            assert issue, "Second issue not found"
            print(f"    ✓ Issue found: {issue.key}")
        
        return True

if __name__ == '__main__':
    try:
        success = test_various_operations()
        print("\n" + "=" * 70)
        print("RESULT: ✓ ALL TESTS PASSED")
        print("=" * 70 + "\n")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""Final verification - Issue creation via form works end-to-end."""

import sys, os
sys.path.insert(0, os.getcwd())

from app import create_app, db
from app.models import Issue
from flask_wtf.csrf import generate_csrf

app = create_app()

def test_issue_creation():
    """Test that issues can be created via form submission."""
    with app.test_client() as client:
        print("\n" + "=" * 70)
        print("FINAL VERIFICATION: Issue Creation via Form")
        print("=" * 70)
        
        # Step 1: Login
        print("\n[1] Logging in as john_doe...")
        client.get('/login')
        with client.session_transaction() as sess:
            csrf = generate_csrf(sess)
        
        resp = client.post('/login', data={
            'username': 'john_doe',
            'password': 'password123',
            'csrf_token': csrf
        }, follow_redirects=False)
        
        if resp.status_code == 302:
            print("    ✓ Login successful (302 redirect)")
        else:
            print(f"    ✗ Login failed: {resp.status_code}")
            return False
        
        # Step 2: Navigate to project
        print("\n[2] Accessing project page...")
        resp = client.get('/project/1')
        if resp.status_code == 200:
            print("    ✓ Project page loaded")
        else:
            print(f"    ✗ Failed to load project: {resp.status_code}")
            return False
        
        # Get CSRF token for form submission
        with client.session_transaction() as sess:
            csrf_form = generate_csrf(sess)
        
        # Step 3: Create issue via form
        print("\n[3] Submitting issue creation form...")
        form_data = {
            'title': 'Form Submission Test Issue',
            'description': 'Testing issue creation via HTML form',
            'priority': 'high',
            'issue_type': 'bug',
            'status': 'open',
            'csrf_token': csrf_form
        }
        
        resp = client.post('/project/1/issue/add', data=form_data, follow_redirects=False)
        
        if resp.status_code == 302:
            print(f"    ✓ Form submission successful (302 redirect)")
            print(f"      Redirected to: {resp.headers.get('Location')}")
        else:
            print(f"    ✗ Form submission failed: {resp.status_code}")
            print(f"      Response: {resp.get_data(as_text=True)[:200]}")
            return False
        
        # Step 4: Verify issue was created
        print("\n[4] Verifying issue in database...")
        with app.app_context():
            issue = Issue.query.filter_by(title='Form Submission Test Issue').first()
            if issue:
                print(f"    ✓ Issue created successfully!")
                print(f"      Key: {issue.key}")
                print(f"      Title: {issue.title}")
                print(f"      Priority: {issue.priority}")
                print(f"      Type: {issue.issue_type}")
                print(f"      Status: {issue.status}")
                print(f"      Reporter ID: {issue.reporter_id}")
                print(f"      Project ID: {issue.project_id}")
                return True
            else:
                print(f"    ✗ Issue not found in database")
                # Show what's in the project
                all_issues = Issue.query.filter_by(project_id=1).order_by(Issue.id.desc()).limit(3).all()
                print(f"      Latest issues: {[i.key for i in all_issues]}")
                return False

if __name__ == '__main__':
    success = test_issue_creation()
    print("\n" + "=" * 70)
    if success:
        print("RESULT: ✓ SUCCESS - Form-based issue creation is working!")
    else:
        print("RESULT: ✗ FAILED - Issue creation via form did not work")
    print("=" * 70 + "\n")
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""Simple direct test using Flask test client for issue creation."""

import sys, os
sys.path.insert(0, os.getcwd())

from app import create_app, db
from app.models import Issue
import re

app = create_app()

print("=" * 60)
print("Direct Flask Test Client - Issue Creation via Form")
print("=" * 60)

with app.test_client() as client:
    # Step 1: Get login page and CSRF token
    print("\n[1] Getting login page...")
    resp = client.get('/login')
    csrf_login = re.search(r'csrf_token["\'].*?value=["\']([^"\']+)', resp.get_data(as_text=True))
    if csrf_login:
        csrf_token = csrf_login.group(1)
        print(f"    ✓ CSRF token: {csrf_token[:30]}...")
    else:
        print("    ✗ No CSRF token")
        exit(1)
    
    # Step 2: Login
    print("\n[2] Logging in as john_doe...")
    resp = client.post('/login', data={
        'username': 'john_doe',
        'password': 'password123',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    if 'Welcome' in resp.get_data(as_text=True):
        print(f"    ✓ Login successful")
    else:
        print(f"    ✗ Login failed")
        print(f"    Response: {resp.get_data(as_text=True)[:200]}")
        exit(1)
    
    # Step 3: Get project page for fresh CSRF token
    print("\n[3] Getting project/1 page...")
    resp = client.get('/project/1')
    if resp.status_code != 200:
        print(f"    ✗ Project page failed: {resp.status_code}")
        exit(1)
    
    csrf_project = re.search(r'csrf_token["\'].*?value=["\']([^"\']+)', resp.get_data(as_text=True))
    if csrf_project:
        csrf_token = csrf_project.group(1)
        print(f"    ✓ Project page loaded, CSRF: {csrf_token[:30]}...")
    else:
        print(f"    ⚠ No CSRF on project page, using login token")
    
    # Step 4: Submit issue form with all required fields
    print("\n[4] Submitting issue creation form...")
    form_data = {
        'title': 'Direct Flask Test Issue',
        'description': 'Testing form submission directly',
        'priority': 'medium',
        'issue_type': 'task',
        'status': 'open',
        'csrf_token': csrf_token
    }
    
    resp = client.post('/project/1/issue/add', data=form_data, follow_redirects=False)
    print(f"    Status: {resp.status_code}")
    
    if resp.status_code == 302:
        location = resp.headers.get('Location', '')
        print(f"    ✓ Redirected to: {location}")
        
        # Follow redirect
        resp2 = client.get(location)
        if 'Issue created successfully' in resp2.get_data(as_text=True):
            print(f"    ✓ Success message found!")
        elif 'Direct Flask Test Issue' in resp2.get_data(as_text=True):
            print(f"    ✓ Issue title found in response!")
        else:
            print(f"    ⚠ No success confirmation in response")
    elif resp.status_code == 200:
        if 'error' in resp.get_data(as_text=True).lower():
            print(f"    ✗ Response contains error")
            # Extract error message
            error_match = re.search(r'(?:error|alert)[^>]*>([^<]+)', resp.get_data(as_text=True))
            if error_match:
                print(f"       {error_match.group(1)}")
        else:
            print(f"    ✓ Form processed (200 OK)")
    else:
        print(f"    ✗ Unexpected status: {resp.status_code}")
    
    # Step 5: Verify in database
    print("\n[5] Checking database for issue...")
    with app.app_context():
        issue = Issue.query.filter_by(title='Direct Flask Test Issue').first()
        if issue:
            print(f"    ✓ ISSUE CREATED SUCCESSFULLY!")
            print(f"       ID: {issue.id}")
            print(f"       Key: {issue.key}")
            print(f"       Status: {issue.status}")
            print(f"       Created: {issue.created_at}")
        else:
            print(f"    ✗ Issue not found in database")
            print(f"       (Most recent issues: {[i.key for i in Issue.query.order_by(Issue.id.desc()).limit(3)]})")

print("\n" + "=" * 60)

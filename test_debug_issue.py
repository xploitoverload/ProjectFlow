#!/usr/bin/env python3
"""Debug issue creation - capture actual error."""

import sys, os
sys.path.insert(0, os.getcwd())

from app import create_app, db
from app.models import Issue
import logging

# Enable SQL logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = create_app()

with app.test_client() as client:
    print("=" * 60)
    print("Testing Issue Creation - Debug Mode")
    print("=" * 60)
    
    # Step 1: Login
    print("\n[1] Logging in...")
    import re
    resp = client.get('/login')
    csrf_match = re.search(r'csrf_token["\'].*?value=["\']([^"\']+)', resp.get_data(as_text=True))
    csrf = csrf_match.group(1) if csrf_match else 'test_csrf'
    
    resp = client.post('/login', data={
        'username': 'john_doe',
        'password': 'password123',
        'csrf_token': csrf
    }, follow_redirects=True)
    print("    ✓ Login complete")
    
    # Step 2: Get project page to refresh CSRF
    print("\n[2] Getting project page...")
    resp = client.get('/project/1')
    if resp.status_code != 200:
        print(f"    ✗ Failed: {resp.status_code}")
        exit(1)
    
    csrf_match = re.search(r'csrf_token["\'].*?value=["\']([^"\']+)', resp.get_data(as_text=True))
    csrf = csrf_match.group(1) if csrf_match else csrf
    print(f"    ✓ Project page loaded, using CSRF: {csrf[:20]}...")
    
    # Step 3: Submit form with detailed output
    print("\n[3] Submitting form...")
    form_data = {
        'title': 'Debug Test Issue',
        'description': 'Testing',
        'priority': 'medium',
        'issue_type': 'task',
        'status': 'open',
        'csrf_token': csrf
    }
    
    # Make request WITHOUT following redirects to see exact response
    resp = client.post('/project/1/issue/add', data=form_data, follow_redirects=False)
    print(f"    Status: {resp.status_code}")
    print(f"    Headers: {dict(resp.headers)}")
    
    if resp.status_code == 302:
        print(f"    ✓ Redirected to: {resp.headers.get('Location')}")
    else:
        print(f"    Response (first 500): {resp.get_data(as_text=True)[:500]}")
    
    # Step 4: Check database
    print("\n[4] Checking database...")
    with app.app_context():
        issue = Issue.query.filter_by(title='Debug Test Issue').first()
        if issue:
            print(f"    ✓ ISSUE CREATED: {issue.key}")
        else:
            print(f"    ✗ Issue not found")
            # Show all recent issues
            recent = Issue.query.order_by(Issue.id.desc()).limit(3).all()
            print(f"    Recent issues: {[i.key for i in recent]}")

print("\n" + "=" * 60)

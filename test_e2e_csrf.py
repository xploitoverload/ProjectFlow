#!/usr/bin/env python3
"""
Comprehensive End-to-End Test for CSRF Fix
Tests the complete flow: Login → Navigate → Create Issue
"""

import re
import json
from requests import Session
from urllib.parse import urljoin

BASE_URL = 'http://127.0.0.1:5000'

def extract_csrf_token(html):
    """Extract CSRF token from HTML."""
    match = re.search(r'<input[^>]+name=["\']csrf_token["\'][^>]+value=["\']([^"\']+)["\']', html)
    if match:
        return match.group(1)
    return None

def test_csrf_fix():
    """Run comprehensive CSRF fix test."""
    session = Session()
    results = {
        'login': False,
        'dashboard_access': False,
        'project_access': False,
        'issue_created': False,
        'csrf_preserved': False
    }
    
    print("=" * 70)
    print("COMPREHENSIVE CSRF FIX VERIFICATION TEST")
    print("=" * 70)
    
    # Step 1: Get login page
    print("\n[STEP 1] Getting login page...")
    resp = session.get(f'{BASE_URL}/login')
    if resp.status_code != 200:
        print(f"  ✗ Failed to load login page: {resp.status_code}")
        return results
    
    csrf_token_login = extract_csrf_token(resp.text)
    if not csrf_token_login:
        print("  ✗ No CSRF token on login page")
        return results
    print(f"  ✓ Login page loaded")
    print(f"  ✓ CSRF token obtained: {csrf_token_login[:30]}...")
    
    # Step 2: Login
    print("\n[STEP 2] Logging in as john_doe...")
    login_data = {
        'username': 'john_doe',
        'password': 'password123',
        'csrf_token': csrf_token_login
    }
    resp = session.post(f'{BASE_URL}/login', data=login_data, allow_redirects=True)
    
    if resp.status_code == 200 and 'Welcome' in resp.text:
        print(f"  ✓ Login successful")
        results['login'] = True
    elif 'Invalid credentials' in resp.text:
        print(f"  ✗ Invalid credentials")
        return results
    else:
        print(f"  ✗ Login failed: {resp.status_code}")
        return results
    
    # Step 3: Access dashboard
    print("\n[STEP 3] Verifying dashboard access...")
    if 'dashboard' in resp.text.lower():
        print(f"  ✓ Dashboard accessible")
        results['dashboard_access'] = True
    
    # Step 4: Check if CSRF token was preserved during login
    print("\n[STEP 4] Verifying CSRF token preservation...")
    csrf_token_session = extract_csrf_token(resp.text)
    if csrf_token_session:
        print(f"  ✓ CSRF token present in session after login")
        print(f"  ✓ Token: {csrf_token_session[:30]}...")
        results['csrf_preserved'] = True
    else:
        print(f"  ⚠ CSRF token not found in current response")
        # This might be OK if it's on the next page
    
    # Step 5: Try to access a project (might fail due to permissions)
    print("\n[STEP 5] Attempting project access...")
    resp = session.get(f'{BASE_URL}/project/1', allow_redirects=False)
    if resp.status_code == 200:
        print(f"  ✓ Project page accessible")
        results['project_access'] = True
        csrf_project = extract_csrf_token(resp.text)
        if csrf_project:
            print(f"  ✓ CSRF token on project page: {csrf_project[:30]}...")
    elif resp.status_code == 403:
        print(f"  ⚠ Project access denied (403) - user may lack permissions")
        print(f"    This is expected for non-admin users")
    elif resp.status_code == 404:
        print(f"  ⚠ Project not found (404)")
    else:
        print(f"  ⚠ Unexpected status: {resp.status_code}")
    
    # Step 6: Try to create issue via API (more reliable test)
    print("\n[STEP 6] Testing issue creation via API...")
    
    # First, get a CSRF token from dashboard
    resp = session.get(f'{BASE_URL}/dashboard')
    csrf_for_api = extract_csrf_token(resp.text)
    if not csrf_for_api:
        print(f"  ⚠ Could not get CSRF token from dashboard")
        # Try with login CSRF token
        csrf_for_api = csrf_token_login
    
    print(f"  Using CSRF token: {csrf_for_api[:30]}...")
    
    # Try to create issue
    issue_data = {
        'title': 'E2E Test Issue - CSRF Fix Verification',
        'description': 'Testing form submission after CSRF token fix',
        'priority': 'high',
        'status': 'open',
        'csrf_token': csrf_for_api
    }
    
    resp = session.post(f'{BASE_URL}/project/1/issue/add', 
                       data=issue_data, 
                       allow_redirects=False)
    
    if resp.status_code == 302:
        location = resp.headers.get('Location', '')
        if '/login' in location:
            print(f"  ⚠ Redirected to login: {location}")
            print(f"    This suggests session/auth issue (not CSRF)")
        elif 'issue' in location or 'kanban' in location:
            print(f"  ✓ Redirected to: {location}")
            print(f"  ✓ Issue creation likely successful!")
            results['issue_created'] = True
        else:
            print(f"  ⚠ Unexpected redirect: {location}")
    elif resp.status_code == 200:
        if 'Issue created successfully' in resp.text or 'E2E Test Issue' in resp.text:
            print(f"  ✓ Issue creation response contains success message")
            results['issue_created'] = True
        else:
            print(f"  ⚠ Form processed but unclear if successful")
    else:
        print(f"  ✗ Unexpected response: {resp.status_code}")
        if 'CSRF' in resp.text:
            print(f"    Response contains 'CSRF' error!")
        print(f"    First 200 chars: {resp.text[:200]}")
    
    # Step 7: Verify in database
    print("\n[STEP 7] Verifying issue in database...")
    import sys, os
    sys.path.insert(0, os.getcwd())
    from app import create_app
    from app.models import Issue
    
    app = create_app()
    with app.app_context():
        issue = Issue.query.filter_by(title='E2E Test Issue - CSRF Fix Verification').first()
        if issue:
            print(f"  ✓ Issue found in database!")
            print(f"    ID: {issue.id}")
            print(f"    Key: {issue.key}")
            print(f"    Status: {issue.status}")
            print(f"    Created: {issue.created_at}")
            results['issue_created'] = True
        else:
            print(f"  ⚠ Issue not found in database")
    
    return results

# Run test
if __name__ == '__main__':
    results = test_csrf_fix()
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_status in results.items():
        status = "✓ PASS" if passed_status else "✗ FAIL"
        print(f"  {status:8} - {test_name.replace('_', ' ').title()}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if results['csrf_preserved'] and results['issue_created']:
        print("\n✅ CSRF FIX VERIFIED - Issue creation works!")
    elif results['csrf_preserved']:
        print("\n⚠️  CSRF token is preserved, but issue creation test inconclusive")
    else:
        print("\n❌ CSRF token preservation may not be working")
    
    print("=" * 70)

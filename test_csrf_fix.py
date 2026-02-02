#!/usr/bin/env python3
"""Test script to verify CSRF token fix for form submission."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
from requests import Session

BASE_URL = 'http://127.0.0.1:5000'

def extract_csrf_token(html):
    """Extract CSRF token from HTML."""
    match = re.search(r'<input[^>]+name=["\']csrf_token["\'][^>]+value=["\']([^"\']+)["\']', html)
    if match:
        return match.group(1)
    return None

def test_issue_creation():
    """Test creating an issue via form submission."""
    session = Session()
    
    print("[1] Getting login page...")
    resp = session.get(f'{BASE_URL}/login')
    assert resp.status_code == 200, f"Login page failed: {resp.status_code}"
    csrf_token_login = extract_csrf_token(resp.text)
    print(f"    ✓ CSRF token from login: {csrf_token_login[:20]}..." if csrf_token_login else "    ✗ No CSRF token!")
    
    print("\n[2] Logging in as test user...")
    data = {
        'username': 'test',
        'password': 'password123',
        'csrf_token': csrf_token_login
    }
    resp = session.post(f'{BASE_URL}/login', data=data, allow_redirects=True)
    print(f"    Status: {resp.status_code}")
    
    # Check if login was successful
    if 'user_id' in session.cookies:
        print("    ✓ Session cookie created")
    else:
        print("    ✗ No session cookie!")
    
    if 'Welcome back' in resp.text or 'dashboard' in resp.text:
        print("    ✓ Redirect to dashboard successful")
    else:
        print(f"    ✗ Did not reach dashboard")
        print("Response:", resp.text[:500])
        return False
    
    print("\n[3] Getting kanban board (project/1)...")
    resp = session.get(f'{BASE_URL}/project/1/')
    if resp.status_code == 200:
        print("    ✓ Kanban board accessed")
        csrf_token_kanban = extract_csrf_token(resp.text)
        print(f"    CSRF token from kanban: {csrf_token_kanban[:20]}..." if csrf_token_kanban else "    ✗ No CSRF token in kanban!")
    else:
        print(f"    ✗ Kanban board failed: {resp.status_code}")
        if resp.status_code == 302:
            print(f"    Redirect to: {resp.headers.get('Location')}")
        return False
    
    print("\n[4] Creating issue via form...")
    data = {
        'title': 'Test Issue CSRF Fix',
        'description': 'Testing CSRF token preservation',
        'priority': 'high',
        'status': 'open',
        'csrf_token': csrf_token_kanban or csrf_token_login
    }
    resp = session.post(f'{BASE_URL}/project/1/issue/add', data=data, allow_redirects=True)
    print(f"    Status: {resp.status_code}")
    
    if resp.status_code == 200:
        if 'created' in resp.text.lower() or 'Test Issue CSRF' in resp.text:
            print("    ✓ Issue created successfully!")
            return True
        else:
            print("    ✗ Form submitted but issue not found in response")
            print("Response:", resp.text[:500])
            return False
    elif resp.status_code == 302:
        print(f"    Redirect to: {resp.headers.get('Location')}")
        print("    ✓ Issue likely created (302 redirect is expected)")
        return True
    else:
        print(f"    ✗ Issue creation failed")
        print("Response:", resp.text[:500])
        return False

if __name__ == '__main__':
    success = test_issue_creation()
    if success:
        print("\n✅ CSRF fix verified - issue creation works!")
        sys.exit(0)
    else:
        print("\n❌ Issue creation still failing")
        sys.exit(1)

#!/usr/bin/env python3
"""Test issue creation via form submission after CSRF fix."""

import re
from requests import Session

BASE_URL = 'http://127.0.0.1:5000'

def extract_csrf_token(html):
    """Extract CSRF token from HTML."""
    match = re.search(r'<input[^>]+name=["\']csrf_token["\'][^>]+value=["\']([^"\']+)["\']', html)
    if match:
        return match.group(1)
    return None

session = Session()

print("=" * 60)
print("Testing Issue Creation with CSRF Token Fix")
print("=" * 60)

print("\n[1] Getting login page...")
resp = session.get(f'{BASE_URL}/login')
csrf_token = extract_csrf_token(resp.text)
print(f"    ✓ CSRF token obtained: {csrf_token[:20]}...")

print("\n[2] Logging in as admin user...")
data = {
    'username': 'admin',
    'password': 'password123',
    'csrf_token': csrf_token
}
resp = session.post(f'{BASE_URL}/login', data=data, allow_redirects=False)
print(f"    Status: {resp.status_code}")
if resp.status_code == 302:
    print(f"    ✓ Redirected to: {resp.headers.get('Location')}")

# Follow redirect manually
dashboard_resp = session.get(f'{BASE_URL}{resp.headers.get("Location")}')
print(f"    Dashboard loaded: {dashboard_resp.status_code == 200}")

print("\n[3] Getting project/1 (Lunar Rover)...")
resp = session.get(f'{BASE_URL}/project/1')
if resp.status_code == 200:
    csrf_token = extract_csrf_token(resp.text)
    print(f"    ✓ Project loaded successfully")
    print(f"    CSRF token from project: {csrf_token[:20] if csrf_token else 'NOT FOUND'}...")
else:
    print(f"    ✗ Failed to load project: {resp.status_code}")
    print(f"    Response: {resp.text[:200]}")
    exit(1)

print("\n[4] Creating issue via form...")
data = {
    'title': 'CSRF Test Issue',
    'description': 'Testing CSRF token fix for issue creation',
    'priority': 'high',
    'status': 'open',
    'csrf_token': csrf_token or extract_csrf_token(dashboard_resp.text)
}

resp = session.post(f'{BASE_URL}/project/1/issue/add', data=data, allow_redirects=False)
print(f"    Status: {resp.status_code}")

if resp.status_code == 302:
    print(f"    ✓ Redirect: {resp.headers.get('Location')}")
    print(f"    ✅ ISSUE CREATION SUCCESSFUL!")
elif resp.status_code == 200:
    if 'error' in resp.text.lower():
        print(f"    ✗ Error in response:")
        # Extract error from flash
        error_match = re.search(r'class="alert[^>]*>([^<]+)<', resp.text)
        if error_match:
            print(f"      {error_match.group(1)}")
    else:
        print(f"    ✓ Form processed")
        if 'CSRF Test Issue' in resp.text:
            print(f"    ✅ ISSUE CREATION SUCCESSFUL!")
else:
    print(f"    ✗ Unexpected status: {resp.status_code}")
    print(f"    Response: {resp.text[:500]}")

print("\n" + "=" * 60)

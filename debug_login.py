#!/usr/bin/env python3
"""Debug login process."""

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

print("[1] Getting login page...")
resp = session.get(f'{BASE_URL}/login')
print(f"Status: {resp.status_code}")
print(f"Cookies: {session.cookies}")
csrf = extract_csrf_token(resp.text)
print(f"CSRF token: {csrf}")

print("\n[2] Logging in...")
data = {
    'username': 'test',
    'password': 'password123',
    'csrf_token': csrf
}
resp = session.post(f'{BASE_URL}/login', data=data, allow_redirects=False)
print(f"Status: {resp.status_code}")
print(f"Location: {resp.headers.get('Location')}")
print(f"Cookies after login: {session.cookies}")
print(f"Response text (first 500 chars): {resp.text[:500]}")

# Check if login failed
if 'Invalid credentials' in resp.text:
    print("\n❌ Login failed - invalid credentials")
else:
    print("\n[3] Following redirect...")
    resp2 = session.get(f'{BASE_URL}{resp.headers.get("Location")}')
    print(f"Status: {resp2.status_code}")
    print(f"Cookies: {session.cookies}")
    print(f"Response contains 'Welcome': {'Welcome' in resp2.text}")
    print(f"Response contains 'dashboard': {'dashboard' in resp2.text}")


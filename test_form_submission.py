#!/usr/bin/env python3
"""Test form-based issue creation via HTTP POST."""

import requests
from http.cookies import SimpleCookie
import sys

# Session to maintain cookies
session = requests.Session()

# Step 1: Login
print("[1] Logging in...")
login_response = session.post(
    'http://127.0.0.1:5000/login',
    data={
        'username': 'admin',
        'password': 'admin123'
    },
    allow_redirects=True
)

if login_response.status_code != 200:
    print(f"✗ Login failed: {login_response.status_code}")
    sys.exit(1)

print(f"✓ Login successful")

# Step 2: Get kanban page to extract CSRF token
print("[2] Getting kanban page...")
kanban_response = session.get('http://127.0.0.1:5000/project/1/kanban')

if kanban_response.status_code != 200:
    print(f"✗ Kanban page failed: {kanban_response.status_code}")
    sys.exit(1)

# Extract CSRF token from the HTML
import re
csrf_match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"', kanban_response.text)
csrf_token = csrf_match.group(1) if csrf_match else None

if not csrf_token:
    print("✗ CSRF token not found in kanban page")
    sys.exit(1)

print(f"✓ Got CSRF token: {csrf_token[:20]}...")

# Step 3: Submit the create issue form
print("[3] Submitting create issue form...")
form_data = {
    'csrf_token': csrf_token,
    'title': 'Test Issue from Form Submission',
    'description': 'Testing direct form submission',
    'priority': 'high',
    'issue_type': 'bug',
    'status': 'todo',
    'assignee_id': ''
}

submit_response = session.post(
    'http://127.0.0.1:5000/project/1/issue/add',
    data=form_data,
    allow_redirects=False
)

print(f"Response status: {submit_response.status_code}")
print(f"Response location: {submit_response.headers.get('Location', 'No redirect')}")

if submit_response.status_code in [302, 200]:
    print("✓ Form submitted successfully!")
else:
    print(f"✗ Form submission failed: {submit_response.status_code}")
    print(f"Response: {submit_response.text[:500]}")
    sys.exit(1)

# Step 4: Verify issue was created
print("[4] Verifying issue in database...")
sys.path.insert(0, '/home/KALPESH/Stuffs/Project Management')
from app import create_app
from app.models import Issue

app = create_app()
with app.app_context():
    issues = Issue.query.filter_by(project_id=1).order_by(Issue.created_at.desc()).limit(1).all()
    if issues and 'Form Submission' in issues[0].title:
        print(f"✓ Issue created successfully: {issues[0].key} - {issues[0].title}")
        print(f"  Status: {issues[0].status}, Priority: {issues[0].priority}, Type: {issues[0].issue_type}")
    else:
        print(f"✗ Issue not found in database")
        sys.exit(1)

print("\n" + "="*60)
print("SUCCESS! Create Issue Form is Working! ✓")
print("="*60)

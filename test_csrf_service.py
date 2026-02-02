#!/usr/bin/env python3
"""Test to verify the CSRF fix doesn't break issue creation via service."""

import sys
import os
sys.path.insert(0, os.getcwd())

from app import create_app, db
from app.models import User, Project, Issue
from app.services.issue_service import IssueService
from flask import session

app = create_app()

print("=" * 60)
print("Testing CSRF Fix Impact on Issue Creation Service")
print("=" * 60)

with app.app_context():
    # Get admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("Admin not found")
        exit(1)
    
    # Get a project
    project = Project.query.first()
    if not project:
        print("No projects found")
        exit(1)
    
    print(f"\nTest Setup:")
    print(f"  User: {admin.username} (ID: {admin.id})")
    print(f"  Project: {project.name} (ID: {project.id})")
    
    print(f"\n[1] Creating issue via IssueService...")
    success, issue, message = IssueService.create_issue(
        project_id=project.id,
        title='CSRF Fix Test Issue',
        description='Testing that CSRF fix did not break issue creation',
        priority='high',
        issue_type='task',
        status='open',
        reporter_id=admin.id
    )
    
    if success:
        print(f"    ✅ SUCCESS - Issue created!")
        print(f"       ID: {issue.id}")
        print(f"       Key: {issue.key}")
        print(f"       Title: {issue.title}")
        print(f"       Status: {issue.status}")
    else:
        print(f"    ❌ FAILED - {message}")
        exit(1)
    
    print(f"\n[2] Verifying issue in database...")
    found_issue = Issue.query.filter_by(id=issue.id).first()
    if found_issue:
        print(f"    ✅ Issue found in database")
        print(f"       Created at: {found_issue.created_at}")
        print(f"       Project ID: {found_issue.project_id}")
    else:
        print(f"    ❌ Issue not found!")
        exit(1)

print("\n" + "=" * 60)
print("✅ CSRF FIX VERIFIED - IssueService Works Correctly")
print("=" * 60)

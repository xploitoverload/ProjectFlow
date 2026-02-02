#!/usr/bin/env python3
"""Test script to create an issue and verify it works."""

import sys
sys.path.insert(0, '.')

from app import create_app
from app.models import db, Issue
from app.services import IssueService

# Create app context
app = create_app()

with app.app_context():
    # Create a test issue using the service (proper way)
    success, issue, message = IssueService.create_issue(
        project_id=1,
        title="Test Issue - From Service",
        description="Testing issue creation via service",
        priority="high",
        issue_type="bug",
        status="open",
        reporter_id=1
    )
    
    if success:
        print(f"✓ Issue created successfully: ID={issue.id}, Key={issue.key}, Title={issue.title}")
    else:
        print(f"✗ Failed to create issue: {message}")
        sys.exit(1)
    
    # Verify it was created
    count = Issue.query.filter_by(project_id=1).count()
    print(f"✓ Total issues for project 1: {count}")
    
    # Get all issues for this project
    issues = Issue.query.filter_by(project_id=1).all()
    for iss in issues:
        print(f"  - [{iss.key}] {iss.title} (Status: {iss.status})")

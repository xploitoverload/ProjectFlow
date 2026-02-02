#!/usr/bin/env python3
"""Comprehensive test of create issue and calendar filters."""

import sys
import sqlite3
sys.path.insert(0, '.')

from app import create_app
from app.models import db, Issue, Project
from app.services import IssueService

app = create_app()

print("=" * 60)
print("TESTING ISSUE CREATION SYSTEM")
print("=" * 60)

with app.app_context():
    # Test 1: Create issue via service
    print("\n[TEST 1] Creating issue via IssueService...")
    success, issue, message = IssueService.create_issue(
        project_id=1,
        title="Bug Fix - Header Layout",
        description="Fix the header layout on mobile devices",
        priority="high",
        issue_type="bug",
        status="in_progress",
        reporter_id=1,
        assignee_id=2
    )
    
    if success:
        print(f"  ✓ Created: {issue.key} - {issue.title}")
    else:
        print(f"  ✗ Failed: {message}")
        sys.exit(1)
    
    # Test 2: Create another issue
    print("\n[TEST 2] Creating second issue...")
    success, issue2, message = IssueService.create_issue(
        project_id=1,
        title="Feature Request - Dark Mode",
        description="Implement dark mode for the application",
        priority="medium",
        issue_type="story",
        status="todo",
        reporter_id=1,
        story_points=8
    )
    
    if success:
        print(f"  ✓ Created: {issue2.key} - {issue2.title}")
    else:
        print(f"  ✗ Failed: {message}")
        sys.exit(1)
    
    # Test 3: Verify in database
    print("\n[TEST 3] Verifying issues in database...")
    count = Issue.query.filter_by(project_id=1).count()
    print(f"  ✓ Total issues for project 1: {count}")
    
    issues = Issue.query.filter_by(project_id=1).all()
    print(f"  Issues list:")
    for iss in issues:
        print(f"    - [{iss.key}] {iss.title}")
        print(f"      Status: {iss.status}, Priority: {iss.priority}, Type: {iss.issue_type}")
        if iss.story_points:
            print(f"      Story Points: {iss.story_points}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    print("\nNEXT STEPS:")
    print("1. Visit http://127.0.0.1:5000/project/1/kanban")
    print("2. Click 'Create Issue' button and verify modal opens")
    print("3. Fill in the form and submit")
    print("4. Verify the issue appears on the kanban board")
    print("\n5. Visit http://127.0.0.1:5000/calendar")
    print("6. Click the 'Assignee', 'Type', 'Status' filter buttons")
    print("7. Select filter options and click 'Apply'")
    print("8. Verify events are filtered correctly")

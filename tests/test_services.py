# tests/test_services.py
"""
Tests for Core Service Layer:
ProjectService, IssueService, NotificationService, and UserService.
"""

import pytest
from app.models import db, User, Project, Issue, Team, Notification
from app.services.project_service import ProjectService
from app.services.issue_service import IssueService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService


class TestProjectService:
    """Test ProjectService domain operations."""
    
    def test_create_and_fetch_project(self, app, auth_user):
        """Test creating, retrieving, and validating project."""
        with app.app_context():
            success, project, msg = ProjectService.create_project(
                name='Firmware Secure Boot',
                key='FSB',
                description='UEFI measured boot enforcement',
                created_by=auth_user.id
            )
            assert success is True
            assert project is not None
            assert project.key == 'FSB'
            
            # Fetch by ID and Key
            by_id = ProjectService.get_project_by_id(project.id)
            assert by_id.name == 'Firmware Secure Boot'
            
            by_key = ProjectService.get_project_by_key('FSB')
            assert by_key.id == project.id
            
            # Duplicate key error
            dup_success, _, dup_msg = ProjectService.create_project(
                name='Another Project',
                key='FSB',
                created_by=auth_user.id
            )
            assert dup_success is False
            assert 'already exists' in dup_msg
    
    def test_update_and_stats_project(self, app, auth_user):
        """Test updating project details and computing statistics."""
        with app.app_context():
            success, project, _ = ProjectService.create_project(
                name='Stats Project',
                created_by=auth_user.id
            )
            assert success is True
            
            up_success, updated, _ = ProjectService.update_project(
                project.id,
                {'description': 'Updated systems description'},
                updated_by=auth_user.id
            )
            assert up_success is True
            assert updated.description == 'Updated systems description'
            
            stats = ProjectService.get_project_statistics(project.id)
            assert stats['total_issues'] == 0


class TestIssueService:
    """Test IssueService issue management, linking, and filters."""
    
    def test_issue_crud_and_links(self, app, auth_user, test_project):
        """Test creating, linking, and deleting issues."""
        with app.app_context():
            # Create primary issue
            s1, issue1, _ = IssueService.create_issue(
                project_id=test_project.id,
                title='PCIe AER Error Handling',
                description='Inspect advanced error reporting registers',
                issue_type='bug',
                priority='critical',
                reporter_id=auth_user.id
            )
            assert s1 is True
            assert issue1.key.startswith('TST-')
            
            # Create secondary issue
            s2, issue2, _ = IssueService.create_issue(
                project_id=test_project.id,
                title='Root Complex Register Dump',
                issue_type='task',
                reporter_id=auth_user.id
            )
            assert s2 is True
            
            # Link issues
            link_success, link, _ = IssueService.link_issues(
                source_id=issue1.id,
                target_id=issue2.id,
                link_type='blocks',
                created_by=auth_user.id
            )
            assert link_success is True
            assert link.source_issue_id == issue1.id
            assert link.target_issue_id == issue2.id
            
            # Filter issues
            bugs = IssueService.get_issues_by_project(test_project.id, {'issue_type': 'bug'})
            assert len(bugs) == 1
            assert bugs[0].title == 'PCIe AER Error Handling'
            
            # Delete issue
            del_success, _ = IssueService.delete_issue(issue2.id, deleted_by=auth_user.id)
            assert del_success is True
            assert IssueService.get_issue_by_id(issue2.id) is None


class TestNotificationService:
    """Test NotificationService creation, unread counts, and reading."""
    
    def test_notification_lifecycle(self, app, auth_user):
        """Test sending notifications and marking them as read."""
        with app.app_context():
            notif = NotificationService.create_notification(
                user_id=auth_user.id,
                notification_type='security_alert',
                title='Critical Security Patch Landed',
                message='Commit 968f2b9 applied cleanly to net/ieee802154.',
                link='/project/1'
            )
            assert notif.id is not None
            assert notif.is_read is False
            
            unread = NotificationService.get_unread_count(auth_user.id)
            assert unread == 1
            
            # Fetch notifications
            notifs = NotificationService.get_notifications(auth_user.id)
            assert len(notifs) >= 1
            assert notifs[0].title == 'Critical Security Patch Landed'
            
            # Mark as read
            mark_success = NotificationService.mark_as_read(notif.id, auth_user.id)
            assert mark_success is True
            assert NotificationService.get_unread_count(auth_user.id) == 0


class TestUserService:
    """Test UserService user provisioning and search."""
    
    def test_user_creation_and_search(self, app, admin_user):
        """Test creating user and searching user directory."""
        with app.app_context():
            success, user, _ = UserService.create_user(
                username='kerneldev',
                email='kerneldev@kernel.org',
                password='SecurePass456!',
                role='employee',
                created_by=admin_user.id
            )
            assert success is True
            assert user.username == 'kerneldev'
            assert user.check_password('SecurePass456!') is True
            
            # Search
            results = UserService.search_users('kerneldev')
            assert len(results) == 1
            assert results[0].username == 'kerneldev'

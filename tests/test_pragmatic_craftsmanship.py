# tests/test_pragmatic_craftsmanship.py
"""
Pragmatic Programmer & Linus Torvalds Craftsmanship Verification Tests:
- DRY: Single authoritative project access policy (multi-team project_teams)
- Data Structures & Relational Integrity: Composite indexes, constraints
- Defensive Programming & IDOR Elimination: Cross-project resource isolation
- Dead Programs Tell No Lies: Cryptographic audit ledger tamper detection
- Ergonomic Contracts: Case-insensitive lookups, model aliases, ownership
"""

import os
from app.models import db, User, Team, Project, Issue, Comment, Attachment
from app.services.project_service import ProjectService
from app.services.issue_service import IssueService
from app.services.audit_service import AuditService
from app.security.authorization import check_ownership


class TestPragmaticCraftsmanship:
    """Certifies Linus Torvalds & Pragmatic Programmer quality standards."""

    def test_multi_team_project_access_and_dry_policy(self, app):
        """
        Verify DRY: Multi-team project assignments via project_teams
        are fully honored by ProjectService.user_has_access.
        """
        with app.app_context():
            team_primary = Team(
                name='Kernel Team Alpha', department='software'
            )
            team_secondary = Team(
                name='Kernel Team Beta', department='software'
            )
            team_unrelated = Team(
                name='External Team Gamma', department='marketing'
            )
            db.session.add_all(
                [team_primary, team_secondary, team_unrelated]
            )
            db.session.commit()

            user_primary = User(
                username='dev_alpha', role='developer',
                team_id=team_primary.id
            )
            user_primary.email = 'alpha@kernel.org'
            user_primary.set_password('Pass123!Alpha')

            user_secondary = User(
                username='dev_beta', role='developer',
                team_id=team_secondary.id
            )
            user_secondary.email = 'beta@kernel.org'
            user_secondary.set_password('Pass123!Beta')

            user_unrelated = User(
                username='dev_gamma', role='developer',
                team_id=team_unrelated.id
            )
            user_unrelated.email = 'gamma@kernel.org'
            user_unrelated.set_password('Pass123!Gamma')

            db.session.add_all([user_primary, user_secondary, user_unrelated])
            db.session.commit()

            project = Project(
                name='Hypervisor Microkernel',
                key='HYP',
                status='Active',
                team_id=team_primary.id
            )
            # Assign secondary team via many-to-many relationship
            project.teams.append(team_secondary)
            db.session.add(project)
            db.session.commit()

            # Verify single authoritative access contract
            assert ProjectService.user_has_access(user_primary, project)
            assert ProjectService.user_has_access(user_secondary, project)
            assert not ProjectService.user_has_access(user_unrelated, project)

            # Verify query list retrieval
            accessible_beta = ProjectService.get_user_accessible_projects(
                user_secondary
            )
            assert project in accessible_beta

            accessible_gamma = ProjectService.get_user_accessible_projects(
                user_unrelated
            )
            assert project not in accessible_gamma

    def test_cross_project_issue_delete_idor_prevention(self, app, client):
        """
        Verify Defensive Programming: Attempts to delete an issue using another
        project's URL route are rejected with 404.
        """
        with app.app_context():
            lead = User(username='security_lead', role='admin')
            lead.email = 'sec@kernel.org'
            lead.set_password('SecAdmin123!')
            db.session.add(lead)
            db.session.commit()
            lead_id = lead.id

            p1 = Project(
                name='Project One', key='PONE', status='Active',
                created_by=lead_id
            )
            p2 = Project(
                name='Project Two', key='PTWO', status='Active',
                created_by=lead_id
            )
            db.session.add_all([p1, p2])
            db.session.commit()
            p1_id = p1.id

            issue_p2 = Issue(
                title='Classified P2 Bug', key='PTWO-1',
                project_id=p2.id, status='open'
            )
            db.session.add(issue_p2)
            db.session.commit()
            issue_id = issue_p2.id

        # Authenticate as lead
        with client.session_transaction() as sess:
            sess['user_id'] = lead_id
            sess['username'] = 'security_lead'
            sess['role'] = 'admin'
            sess['_fresh'] = True

        # Attempt to delete issue_p2 via p1's URL route
        res = client.post(f'/projects/{p1_id}/issue/{issue_id}/delete')
        assert res.status_code == 404

        # Verify the issue still exists in database
        with app.app_context():
            assert Issue.query.get(issue_id) is not None

    def test_comment_author_ownership_and_property_aliases(self, app):
        """
        Verify Design by Contract: Comment author_id/content aliases and
        ownership resolution.
        """
        with app.app_context():
            user = User(username='committer', role='developer')
            user.email = 'com@kernel.org'
            user.set_password('Pass123!Com')
            db.session.add(user)
            db.session.commit()

            project = Project(
                name='Compiler Optimizer', key='OPT', status='Active'
            )
            db.session.add(project)
            db.session.commit()

            issue = Issue(
                title='LLVM IR Lowering', key='OPT-1', project_id=project.id
            )
            db.session.add(issue)
            db.session.commit()

            comment = Comment(issue_id=issue.id, user_id=user.id)
            comment.content = 'Refactored SSA form to dominance frontiers'
            db.session.add(comment)
            db.session.commit()

            # Verify property aliases work both ways
            assert comment.text == 'Refactored SSA form to dominance frontiers'
            assert (
                comment.content == 'Refactored SSA form to dominance frontiers'
            )
            assert comment.author_id == user.id
            assert comment.user_id == user.id

            # Verify resilient check_ownership works on both instance and class
            with app.test_request_context():
                from flask import session
                session['user_id'] = user.id
                assert check_ownership(comment, owner_field='user_id') is True
                assert check_ownership(
                    Comment, comment.id, owner_field='user_id'
                ) is True

    def test_attachment_file_path_alias_and_safe_cleanup(self, app):
        """
        Verify Linus Torvalds zero-breakage ABI:
        Attachment filepath alias works and file is safely handled.
        """
        test_file = '/tmp/projectflow_test_attachment.log'
        with open(test_file, 'w') as f:
            f.write('Antigravity Ring 0 Audit Log Payload')

        with app.app_context():
            user = User(username='uploader', role='developer')
            user.email = 'upload@kernel.org'
            user.set_password('Pass123!Up')
            db.session.add(user)
            db.session.commit()

            project = Project(
                name='Storage Engine', key='STR', status='Active'
            )
            db.session.add(project)
            db.session.commit()

            issue = Issue(
                title='IO Ring Driver', key='STR-1', project_id=project.id
            )
            db.session.add(issue)
            db.session.commit()

            attachment = Attachment(
                issue_id=issue.id,
                user_id=user.id,
                filename='test.log',
                file_path=test_file
            )
            db.session.add(attachment)
            db.session.commit()

            # Verify alias
            assert attachment.filepath == test_file
            assert attachment.file_path == test_file

        if os.path.exists(test_file):
            os.remove(test_file)

    def test_audit_ledger_merkle_tamper_detection(self, app):
        """
        Verify Dead Programs Tell No Lies (Pragmatic Programmer):
        Audit ledger detects any unauthorized alteration in the hash chain.
        """
        with app.app_context():
            AuditService.log_event('INIT_KERNEL', details='System initialized')
            log2 = AuditService.log_event(
                'CONFIG_SET', details='Argon2id enabled'
            )
            AuditService.log_event('USER_ENROLLED', details='Admin enrolled')
            AuditService.log_event('LEDGER_SEALED', details='Genesis verified')

            # Verify ledger is 100% valid initially
            is_valid, broken_id, msg = AuditService.verify_ledger_integrity()
            assert is_valid is True
            assert broken_id is None
            assert 'intact' in msg.lower()

            # Simulate malicious direct-database tampering with log2
            log2.details_encrypted = 'MALICIOUS_TAMPERED_DATA'
            db.session.commit()

            # Audit verification must fail and pinpoint log2
            res_valid, res_id, res_msg = (
                AuditService.verify_ledger_integrity()
            )
            assert res_valid is False
            assert res_id == log2.id
            assert (
                'hash mismatch' in res_msg.lower() or
                'broken chain' in res_msg.lower()
            )

    def test_case_insensitive_issue_key_retrieval(self, app):
        """
        Verify Pragmatic Ergonomics:
        Case-insensitive issue key matching handles mixed case and whitespace.
        """
        with app.app_context():
            p = Project(name='Networking Stack', key='NET', status='Active')
            db.session.add(p)
            db.session.commit()

            issue = Issue(
                title='TCP BBR Congestion Control', key='NET-42',
                project_id=p.id
            )
            db.session.add(issue)
            db.session.commit()

            # Exact uppercase
            assert IssueService.get_issue_by_key('NET-42').id == issue.id
            # Lowercase
            assert IssueService.get_issue_by_key('net-42').id == issue.id
            # Mixed case with whitespace
            assert IssueService.get_issue_by_key('   Net-42   ').id == issue.id
            # Non-existent
            assert IssueService.get_issue_by_key('NET-9999') is None

    def test_database_composite_indexes_exist(self, app):
        """
        Verify Linus Torvalds Taste in Data Structures:
        Composite indexes are present on the Issue table.
        """
        with app.app_context():
            index_names = [idx.name for idx in Issue.__table__.indexes]
            assert 'ix_issue_project_status_pos' in index_names
            assert 'ix_issue_sprint_status' in index_names
            assert 'ix_issue_assignee_status' in index_names

    def test_user_find_by_email_with_field_encryption(self, app):
        """
        Verify Design by Contract & Relational Encryption:
        User.find_by_email reliably locates records despite non-deterministic
        Fernet ciphertext, supporting case-insensitivity and whitespace.
        """
        with app.app_context():
            user = User(
                username='cryptouser',
                role='employee'
            )
            user.email = 'Linus.Torvalds@LinuxFoundation.org'
            user.set_password('KernelSecurity123!')
            db.session.add(user)
            db.session.commit()

            # Exact match
            found = User.find_by_email('Linus.Torvalds@LinuxFoundation.org')
            assert found is not None
            assert found.id == user.id

            # Case-insensitivity & whitespace trimming
            found_lower = User.find_by_email(
                '  linus.torvalds@linuxfoundation.org  '
            )
            assert found_lower is not None
            assert found_lower.id == user.id

            # Non-existent email
            assert User.find_by_email('missing@linuxfoundation.org') is None

    def test_cryptographic_password_reset_and_replay_protection(self, app):
        """
        Verify Defensive Security:
        Password reset tokens are HMAC-signed, stateful against hash changes,
        and prevented from replay attacks once used.
        """
        from app.services.auth_service import AuthService
        with app.app_context():
            user = User(
                username='resettester',
                role='employee'
            )
            user.email = 'reset@kernel.org'
            user.set_password('InitialSecret123!')
            db.session.add(user)
            db.session.commit()

            # Generate token
            ok, token, msg = AuthService.generate_password_reset_token(
                'reset@kernel.org'
            )
            assert ok is True
            assert token is not None

            # Verify token
            verified_user = AuthService.verify_password_reset_token(token)
            assert verified_user is not None
            assert verified_user.id == user.id

            # Tampered token fails
            assert AuthService.verify_password_reset_token(
                token + 'tamper'
            ) is None

            # Replay protection: user changes password, token invalidates
            user.set_password('NewUpdatedSecret456!')
            db.session.commit()

            assert AuthService.verify_password_reset_token(token) is None

    def test_project_get_members_aggregates_teams(self, app):
        """
        Verify DRY: Project.get_members and ProjectService.get_project_members
        aggregate active members from primary and secondary teams while
        excluding inactive accounts.
        """
        with app.app_context():
            t1 = Team(name='Core Team 1', department='software')
            t2 = Team(name='Core Team 2', department='software')
            db.session.add_all([t1, t2])
            db.session.commit()

            u1 = User(
                username='u1_active', role='employee',
                team_id=t1.id, is_active=True
            )
            u1.email = 'u1@kernel.org'
            u1.set_password('Pass123!')

            u2 = User(
                username='u2_secondary', role='employee',
                team_id=t2.id, is_active=True
            )
            u2.email = 'u2@kernel.org'
            u2.set_password('Pass123!')

            u3_inactive = User(
                username='u3_inactive', role='employee',
                team_id=t1.id, is_active=False
            )
            u3_inactive.email = 'u3@kernel.org'
            u3_inactive.set_password('Pass123!')

            db.session.add_all([u1, u2, u3_inactive])
            db.session.commit()

            proj = Project(
                name='Firmware Engine', key='FW',
                status='Active', team_id=t1.id
            )
            proj.teams.append(t2)
            db.session.add(proj)
            db.session.commit()

            members = ProjectService.get_project_members(proj)
            member_ids = [m.id for m in members]

            assert u1.id in member_ids
            assert u2.id in member_ids
            assert u3_inactive.id not in member_ids

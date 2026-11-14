# tests/test_audit_ledger.py
"""
Ring 0 Security Tests - Argon2id Password Hashing & Tamper-Evident Audit Ledger
"""

import pytest
from app.models import User, AuditLog, db
from app.services.audit_service import AuditService
from werkzeug.security import generate_password_hash


class TestArgon2Security:
    """Test Argon2id memory-hard password hashing & migration."""
    
    def test_argon2id_hashing_and_verification(self, app):
        """Verify user passwords use modern Argon2id by default."""
        with app.app_context():
            user = User(username='ring0_user', email='ring0@kernel.org', role='admin')
            user.set_password('KernelSecurity123!')
            db.session.add(user)
            db.session.commit()
            
            # Check password format is Argon2id
            assert user.password.startswith('$argon2id$')
            
            # Check verification succeeds with correct password
            assert user.check_password('KernelSecurity123!') is True
            
            # Check verification fails with wrong password
            assert user.check_password('WrongPassword!') is False

    def test_legacy_pbkdf2_migration(self, app):
        """Verify seamless backward-compatible upgrade from PBKDF2 to Argon2id."""
        with app.app_context():
            user = User(username='legacy_user', email='legacy@kernel.org', role='employee')
            # Manually assign legacy PBKDF2 hash
            legacy_hash = generate_password_hash('LegacyPassword123!', method='pbkdf2:sha256:600000')
            user.password = legacy_hash
            db.session.add(user)
            db.session.commit()
            
            assert user.password.startswith('pbkdf2:sha256:')
            
            # Check verification transparently succeeds and migrates to Argon2id
            assert user.check_password('LegacyPassword123!') is True
            assert user.password.startswith('$argon2id$')


class TestTamperEvidentAuditLedger:
    """Test cryptographic SHA-256 hash chaining on audit records."""
    
    def test_hash_chain_creation_and_integrity(self, app):
        """Verify that sequential audit entries form an unbroken cryptographic chain."""
        with app.app_context():
            # Clear any initial logs
            AuditLog.query.delete()
            db.session.commit()
            
            # Log sequential events
            e1 = AuditService.log_event('LOGIN', user_id=1, details='First login event')
            e2 = AuditService.log_event('PROJECT_CREATE', user_id=1, details='Created Project Flow')
            e3 = AuditService.log_event('ISSUE_CREATE', user_id=1, details='Created Ring0 Task')
            
            assert e1 is not None and e2 is not None and e3 is not None
            
            # First entry links from genesis
            assert e1.prev_hash == "0" * 64
            assert len(e1.record_hash) == 64
            
            # Second entry links to first entry's hash
            assert e2.prev_hash == e1.record_hash
            
            # Third entry links to second entry's hash
            assert e3.prev_hash == e2.record_hash
            
            # Ledger integrity check passes
            is_valid, broken_id, msg = AuditService.verify_ledger_integrity()
            assert is_valid is True
            assert broken_id is None

    def test_tamper_detection(self, app):
        """Verify that tampering with an audit record breaks cryptographic verification."""
        with app.app_context():
            AuditLog.query.delete()
            db.session.commit()
            
            e1 = AuditService.log_event('ACTION_1', user_id=1, details='Legit event 1')
            e2 = AuditService.log_event('ACTION_2', user_id=1, details='Legit event 2')
            e3 = AuditService.log_event('ACTION_3', user_id=1, details='Legit event 3')
            
            # Malicious attacker directly modifies database record e2
            e2.action = 'TAMPERED_ACTION'
            db.session.commit()
            
            # Integrity check MUST detect the corruption immediately
            is_valid, broken_id, msg = AuditService.verify_ledger_integrity()
            assert is_valid is False
            assert broken_id == e2.id

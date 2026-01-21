#!/usr/bin/env python
"""
Security Testing Script
Tests all security features of the Project Management System
Run this after setting up the application to verify security measures
"""

import sys
from app import app
from models import db, User, Team, Project
from security import (
    validate_username, validate_email, validate_password_strength,
    validate_sql_input, sanitize_input
)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if details:
        print(f"      {details}")

def test_password_security():
    """Test password hashing and validation"""
    print_header("PASSWORD SECURITY TESTS")
    
    # Test 1: Weak password rejection
    weak_passwords = ["123", "password", "abc123", "test"]
    all_rejected = True
    for pwd in weak_passwords:
        is_strong, msg = validate_password_strength(pwd)
        if is_strong:
            all_rejected = False
            break
    print_test("Weak passwords rejected", all_rejected)
    
    # Test 2: Strong password acceptance
    strong_pwd = "MyStr0ng!Pass@123"
    is_strong, msg = validate_password_strength(strong_pwd)
    print_test("Strong password accepted", is_strong, msg)
    
    # Test 3: Password hashing
    with app.app_context():
        test_user = User(username='test_hash_user', role='employee')
        test_user.email = 'test@test.com'
        test_user.set_password('TestPass@123')
        
        # Check password is hashed
        is_hashed = test_user.password != 'TestPass@123' and len(test_user.password) > 50
        print_test("Password is hashed", is_hashed)
        
        # Check password verification works
        correct_verify = test_user.check_password('TestPass@123')
        print_test("Correct password verifies", correct_verify)
        
        # Check wrong password fails
        wrong_verify = not test_user.check_password('WrongPass@123')
        print_test("Wrong password rejected", wrong_verify)

def test_encryption():
    """Test field-level encryption"""
    print_header("ENCRYPTION TESTS")
    
    with app.app_context():
        # Test 1: Email encryption
        test_user = User(username='test_encrypt', role='employee')
        test_email = 'encrypt@test.com'
        test_user.email = test_email
        
        # Check email is encrypted in database field
        is_encrypted = test_user.email_encrypted != test_email
        print_test("Email is encrypted in storage", is_encrypted)
        
        # Check email decrypts correctly
        decrypts_correctly = test_user.email == test_email
        print_test("Email decrypts correctly", decrypts_correctly)
        
        # Test 2: Project description encryption
        test_project = Project(
            name='Test Encryption Project',
            status='Not Started',
            created_by=1
        )
        test_desc = 'This is a confidential project description'
        test_project.description = test_desc
        
        is_encrypted = test_project.description_encrypted != test_desc
        print_test("Project description encrypted", is_encrypted)
        
        decrypts_correctly = test_project.description == test_desc
        print_test("Project description decrypts correctly", decrypts_correctly)

def test_sql_injection():
    """Test SQL injection prevention"""
    print_header("SQL INJECTION PREVENTION TESTS")
    
    sql_attacks = [
        "admin' OR '1'='1",
        "'; DROP TABLE users; --",
        "admin'--",
        "' UNION SELECT * FROM users--",
        "1' OR '1' = '1",
    ]
    
    all_blocked = True
    for attack in sql_attacks:
        if validate_sql_input(attack):
            all_blocked = False
            print_test(f"SQL injection blocked: {attack[:30]}", False)
        else:
            print_test(f"SQL injection blocked: {attack[:30]}", True)
    
    # Test normal input passes
    normal_input = "john_doe"
    passes = validate_sql_input(normal_input)
    print_test("Normal input accepted", passes)

def test_xss_prevention():
    """Test XSS attack prevention"""
    print_header("XSS PREVENTION TESTS")
    
    xss_attacks = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='evil.com'></iframe>",
    ]
    
    for attack in xss_attacks:
        sanitized = sanitize_input(attack)
        is_safe = '<script>' not in sanitized and 'javascript:' not in sanitized.lower()
        print_test(f"XSS sanitized: {attack[:30]}", is_safe)
    
    # Test normal content preserved
    normal = "This is a normal message"
    sanitized = sanitize_input(normal)
    preserved = sanitized == normal
    print_test("Normal content preserved", preserved, sanitized)

def test_input_validation():
    """Test input validation"""
    print_header("INPUT VALIDATION TESTS")
    
    # Username validation
    invalid_usernames = [
        "ab",  # too short
        "a" * 21,  # too long
        "user name",  # space
        "user@name",  # special char
        "user.name",  # dot
    ]
    
    all_rejected = all(not validate_username(u) for u in invalid_usernames)
    print_test("Invalid usernames rejected", all_rejected)
    
    valid_username = "valid_user123"
    print_test("Valid username accepted", validate_username(valid_username))
    
    # Email validation
    invalid_emails = [
        "notanemail",
        "@example.com",
        "user@",
        "user @example.com",
    ]
    
    all_rejected = all(not validate_email(e) for e in invalid_emails)
    print_test("Invalid emails rejected", all_rejected)
    
    valid_email = "user@example.com"
    print_test("Valid email accepted", validate_email(valid_email))

def test_session_security():
    """Test session configuration"""
    print_header("SESSION SECURITY TESTS")
    
    print_test("Session cookie HTTPOnly", 
               app.config.get('SESSION_COOKIE_HTTPONLY', False))
    
    print_test("Session cookie SameSite", 
               app.config.get('SESSION_COOKIE_SAMESITE') == 'Lax')
    
    print_test("Session timeout configured", 
               'PERMANENT_SESSION_LIFETIME' in app.config)

def test_database_security():
    """Test database security measures"""
    print_header("DATABASE SECURITY TESTS")
    
    with app.app_context():
        # Test parameterized queries
        try:
            # This should work - parameterized query
            user = User.query.filter_by(username='admin').first()
            print_test("Parameterized queries work", user is not None)
        except Exception as e:
            print_test("Parameterized queries work", False, str(e))
        
        # Test that direct SQL injection would fail
        try:
            # SQLAlchemy should prevent this type of injection
            malicious = "admin' OR '1'='1"
            user = User.query.filter_by(username=malicious).first()
            # Even if query succeeds, it shouldn't find a user with that exact username
            print_test("SQL injection via ORM prevented", user is None)
        except Exception as e:
            print_test("SQL injection via ORM prevented", True, "Query failed as expected")

def test_encryption_key():
    """Test encryption key security"""
    print_header("ENCRYPTION KEY TESTS")
    
    import os
    
    # Check encryption key exists
    key_exists = os.path.exists('encryption.key')
    print_test("Encryption key file exists", key_exists)
    
    # Check .gitignore includes encryption key
    gitignore_exists = os.path.exists('.gitignore')
    if gitignore_exists:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            key_ignored = 'encryption.key' in gitignore_content
            print_test("Encryption key in .gitignore", key_ignored)
    else:
        print_test(".gitignore exists", False, "Create .gitignore file!")
    
    # Check key file permissions (Unix-like systems)
    if os.name != 'nt':  # Not Windows
        import stat
        key_perms = os.stat('encryption.key').st_mode
        is_secure = not (key_perms & stat.S_IRWXG) and not (key_perms & stat.S_IRWXO)
        print_test("Encryption key has secure permissions", is_secure,
                  "Should be readable only by owner")

def run_all_tests():
    """Run all security tests"""
    print(f"\n{Colors.YELLOW}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          SECURITY TESTING SUITE - PROJECT MANAGEMENT SYSTEM       ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    try:
        test_password_security()
        test_encryption()
        test_sql_injection()
        test_xss_prevention()
        test_input_validation()
        test_session_security()
        test_database_security()
        test_encryption_key()
        
        print_header("TEST SUITE COMPLETED")
        print(f"{Colors.GREEN}All security tests completed!{Colors.END}")
        print(f"{Colors.YELLOW}Review any failures above and fix before deployment.{Colors.END}\n")
        
    except Exception as e:
        print(f"\n{Colors.RED}ERROR: Test suite failed with exception:{Colors.END}")
        print(f"{Colors.RED}{str(e)}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_all_tests()
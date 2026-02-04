# Password Manager - User Credentials Management Script

A standalone command-line tool for managing user passwords and account status in your Project Management System.

## Overview

The `password_manager.py` script provides a secure way to manage user credentials without needing to access the database directly. It's designed for administrators only.

## Installation

No additional installation required - the script uses the same dependencies as the main application.

## Commands

### 1. List All Users

Display all users in the system with their details.

```bash
python password_manager.py list-users
```

**Output includes:**
- User ID
- Username
- Email address
- Role (admin, developer, designer, manager, user)
- Department (if assigned)
- Account status (Active/Inactive)

### 2. Reset User Password

Change a user's password. The user can then login with the new password.

```bash
python password_manager.py reset-password
```

**Interactive prompts:**
- Username: Enter the username
- New Password: Enter new password (hidden, will confirm)

**What it does:**
- Updates the user's password with secure hashing (Argon2id)
- Resets failed login attempts to 0
- Unlocks the account if it was locked

**Example:**
```bash
$ python password_manager.py reset-password
Username: john_doe
New Password: ••••••••••
Repeat for confirmation: ••••••••••

✓ Password reset successful for user 'john_doe'
  • Failed login attempts reset to 0
  • Account unlocked if previously locked
  • User can now login with new password
```

### 3. Create New User

Add a new user account to the system.

```bash
python password_manager.py create-user
```

**Interactive prompts:**
- Username: Unique username for the account
- Email: Email address
- Password: Initial password (hidden, will confirm)
- Role: Choose from admin, developer, designer, manager, user

**What it does:**
- Creates a new user account
- Sets initial password
- Assigns a role
- Account is immediately active and ready to login

**Example:**
```bash
$ python password_manager.py create-user
Username: alice_johnson
Email: alice@example.com
Password: ••••••••••
Repeat for confirmation: ••••••••••
Role [user]: developer

✓ User created successfully!
  • Username: alice_johnson
  • Email: alice@example.com
  • Role: developer
  • Status: Active
  • Can login immediately
```

### 4. Check User Details

View complete information about a specific user.

```bash
python password_manager.py check-user
```

**Interactive prompt:**
- Username: Enter the username to check

**Shows:**
- User ID
- Username
- Email
- Full name (if set)
- Role
- Department
- Account status
- Failed login attempts count
- Account creation date
- Last login date/time

**Special alerts:**
- If account is locked (5+ failed attempts), shows unlock instructions

**Example:**
```bash
$ python password_manager.py check-user
Username: john_doe

============================================================
USER DETAILS: john_doe
============================================================
ID:                    2
Username:              john_doe
Email:                 john@example.com
Full Name:             John Doe
Role:                  developer
Department:            Software
Status:                🟢 Active
Failed Login Attempts: 0/5
Created At:            2026-02-03 08:00:00
Last Login:            2026-02-03 12:30:00
============================================================
```

### 5. Deactivate User

Prevent a user from logging in without deleting their account.

```bash
python password_manager.py deactivate-user
```

**Interactive prompt:**
- Username: Enter the username to deactivate

**What it does:**
- Sets the account to inactive
- User cannot login
- Account data is preserved
- Can be reactivated later

### 6. Activate User

Reactivate a deactivated user account.

```bash
python password_manager.py activate-user
```

**Interactive prompt:**
- Username: Enter the username to activate

**What it does:**
- Sets the account to active
- User can login again
- Resets failed login attempts

### 7. Unlock All Locked Accounts

Unlock all accounts that are locked due to failed login attempts (5+ attempts).

```bash
python password_manager.py unlock-all
```

**Shows:**
- List of currently locked accounts
- Number of failed attempts for each
- Asks for confirmation before unlocking

**What it does:**
- Resets failed login attempts to 0 for all locked accounts
- All accounts can immediately login again

**Example:**
```bash
$ python password_manager.py unlock-all

Found 2 locked account(s):
  • john_doe (5 failed attempts)
  • jane_smith (7 failed attempts)

Unlock all accounts? [y/N]: y

✓ Successfully unlocked 2 account(s)
```

### 8. Reset All Passwords to Default

⚠️ **DANGEROUS OPERATION** - Reset all user passwords to the default "password123".

```bash
python password_manager.py reset-all-passwords
```

**What it does:**
- Resets ALL user passwords to: `password123`
- Unlocks all accounts
- Confirmation required twice

**Use case:**
- Initial demo/test setup
- Emergency access when all users are locked out
- Mass password reset before deployment

**Example:**
```bash
$ python password_manager.py reset-all-passwords

⚠️  WARNING: This will reset 5 user(s) to default password!
   Users will be reset to: password123

Are you absolutely sure? (type yes to confirm): yes

✓ Reset 5 user(s) to default password
  • Default password: password123
  • All accounts unlocked
```

## Current Test Users

All passwords: `password123`

| Username | Role | Email |
|----------|------|-------|
| admin | admin | admin@example.com |
| john_doe | developer | john@example.com |
| jane_smith | developer | jane@example.com |
| bob_wilson | designer | bob@example.com |

## Security Notes

1. **Never share passwords** - Always reset passwords privately
2. **Keep passwords strong** - Minimum 6 characters required
3. **Account lockout** - After 5 failed login attempts, account locks for 30 minutes
4. **Password hashing** - All passwords are hashed with Argon2id (industry standard)
5. **No plaintext storage** - Passwords are never stored in plaintext
6. **Limited access** - Only run this script as an administrator

## Account Lockout Recovery

If a user's account is locked after 5 failed login attempts:

**Option 1: Reset their password**
```bash
python password_manager.py reset-password --username john_doe
```

**Option 2: Unlock all accounts**
```bash
python password_manager.py unlock-all
```

## Password Requirements

- **Minimum length:** 6 characters
- **Allowed characters:** Any (letters, numbers, symbols)
- **No expiration:** Passwords don't expire by default
- **Hashing:** Argon2id with secure parameters

## Troubleshooting

### Script not found
```bash
# Make sure you're in the project directory
cd "/home/KALPESH/Stuffs/Project Management"

# Or use full path
/home/KALPESH/Stuffs/Project\ Management/password_manager.py list-users
```

### ModuleNotFoundError
The script requires the main `app` module. Make sure:
1. You're in the project directory
2. All dependencies are installed
3. Python 3.7+ is being used

### Database locked error
- Close any other database connections
- Check if Flask app is running
- Try again after a few seconds

## Quick Reference

```bash
# List all users
python password_manager.py list-users

# Reset a password
python password_manager.py reset-password

# Create new user
python password_manager.py create-user

# Check user details
python password_manager.py check-user

# Deactivate account
python password_manager.py deactivate-user

# Activate account
python password_manager.py activate-user

# Unlock all locked accounts
python password_manager.py unlock-all

# Emergency: Reset all passwords
python password_manager.py reset-all-passwords
```

## Help Command

Get help for any command:

```bash
python password_manager.py --help
python password_manager.py reset-password --help
```

---

**Created for:** Project Management System  
**Admin Use Only**  
**For Secure Password and Account Management**

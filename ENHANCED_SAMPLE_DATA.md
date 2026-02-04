# 🚀 ENHANCED SAMPLE DATA & PASSWORD MANAGER SETUP

**Date:** February 3, 2026  
**Status:** ✅ Complete & Ready to Use  

---

## 📋 What's New

### 1. **Enhanced Sample Data** (Updated)
- ✅ Expanded from 1 project to **4 complete projects**
- ✅ Expanded from 15 issues to **24 comprehensive issues**
- ✅ Added 4 complete sprints (one per project)
- ✅ Added 4 epics (one per project)
- ✅ Expanded labels from 4 to **13 labels** (color-coded)
- ✅ All projects linked with sprints, epics, and team members

### 2. **Password Manager Script** (New)
- ✅ Complete user credential management tool
- ✅ Reset passwords for individual users
- ✅ Create new user accounts
- ✅ Check user account status
- ✅ Deactivate/reactivate accounts
- ✅ Unlock locked accounts (after failed attempts)
- ✅ Emergency mass password reset

---

## 📊 System Statistics

```
📈 CURRENT DATA:
├─ Users: 4
├─ Teams: 1
├─ Projects: 4
├─ Issues: 24
├─ Sprints: 4
├─ Epics: 4
└─ Labels: 13
```

### Projects Created

| Project | Key | Status | Issues | Sprint |
|---------|-----|--------|--------|--------|
| Lunar Rover | NUC | Active | 15 | Sprint 1 |
| E-Commerce Platform | SHOP | Active | 3 | Sprint 1 |
| Mobile App Redesign | MOBILE | Planning | 3 | Sprint Planning |
| Infrastructure Upgrade | INFRA | In Progress | 3 | Phase 1 |

### Sample Project Detail: Lunar Rover (NUC)

**Kanban Board Status Distribution:**
- 📋 To Do: 4 issues
- ⚙️ In Progress: 5 issues
- 👀 Code Review: 2 issues
- ✅ Done: 4 issues

---

## 🔐 Password Manager Usage

### Quick Commands

```bash
# List all users
python password_manager.py list-users

# Reset a password (interactive)
python password_manager.py reset-password

# Create new user (interactive)
python password_manager.py create-user

# Check user details
python password_manager.py check-user

# Deactivate user
python password_manager.py deactivate-user

# Activate user
python password_manager.py activate-user

# Unlock all locked accounts
python password_manager.py unlock-all

# Emergency: Reset all passwords to password123
python password_manager.py reset-all-passwords
```

### Example: Reset Admin Password

```bash
$ python password_manager.py reset-password
Username: admin
New Password: ••••••••••
Repeat for confirmation: ••••••••••

✓ Password reset successful for user 'admin'
  • Failed login attempts reset to 0
  • Account unlocked if previously locked
  • User can now login with new password
```

### Example: Check User Status

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

---

## 👥 Test Users

All test users have password: **`password123`**

| Username | Role | Email | Team |
|----------|------|-------|------|
| admin | Admin | admin@example.com | Beyond Gravity |
| john_doe | Developer | john@example.com | Beyond Gravity |
| jane_smith | Developer | jane@example.com | Beyond Gravity |
| bob_wilson | Designer | bob@example.com | Beyond Gravity |

---

## 🎯 Key Features

### Sample Data Scripts

#### `create_sample_data.py`
- Generates all 4 projects with related data
- Creates 24 issues across all projects
- Sets up proper sprint/epic relationships
- Assigns users to projects
- Configures labels and workflows
- Can be re-run anytime to reset data

**Usage:**
```bash
python create_sample_data.py
```

#### `password_manager.py`
- Interactive CLI tool for credential management
- Safe password reset without database access
- Account status monitoring
- Account lockout recovery
- Create new user accounts on the fly

**Documentation:** See [PASSWORD_MANAGER_README.md](PASSWORD_MANAGER_README.md)

---

## 🚀 Quick Start Guide

### 1. Start the Application
```bash
# From the project directory
python app.py
# or
flask run
```

### 2. Login
```
Username: admin
Password: password123
```

### 3. Explore Projects
- Navigate to Projects/Issues dashboard
- View Lunar Rover (NUC) with 15 issues
- Browse E-Commerce (SHOP), Mobile (MOBILE), Infrastructure (INFRA)
- Check sprints and epics

### 4. Manage Users
```bash
# List all users
python password_manager.py list-users

# Check a user
python password_manager.py check-user

# Reset password if needed
python password_manager.py reset-password

# Create new user
python password_manager.py create-user
```

---

## 📁 Project Structure

```
Project Management/
├── app.py                      # Main Flask application
├── models.py                   # Database models
├── create_sample_data.py       # Sample data generator (UPDATED)
├── password_manager.py         # Password management tool (NEW)
├── PASSWORD_MANAGER_README.md  # Password manager docs (NEW)
├── ENHANCED_SAMPLE_DATA.md     # This file
├── migrations/
│   └── add_department_support.py
├── app/
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── utils/
└── database.db                 # SQLite database
```

---

## 🔒 Security Features

- ✅ Passwords hashed with Argon2id (industry standard)
- ✅ Account lockout after 5 failed attempts
- ✅ Automatic password rehashing on login (legacy PBKDF2 → Argon2)
- ✅ Failed login attempt tracking
- ✅ Session management with Flask-Login
- ✅ CSRF protection with Flask-WTF
- ✅ No plaintext passwords in database

---

## 📝 Sample Data Details

### Lunar Rover Project (NUC)
**Type:** Agile, Active  
**Team:** Beyond Gravity (4 members)  
**Description:** Space exploration mission software

**Issues Distribution:**
- **TO DO (4):** NUC-344, NUC-360, NUC-339, NUC-341
- **IN PROGRESS (5):** NUC-342, NUC-338, NUC-336, NUC-346, NUC-343
- **CODE REVIEW (2):** NUC-387, NUC-349
- **DONE (4):** NUC-345, NUC-350, NUC-351, NUC-352

**Labels:** ACCOUNTS, BILLING, FORMS, FEEDBACK (color-coded)

### E-Commerce Platform Project (SHOP)
**Type:** Agile, Active  
**Team:** Beyond Gravity  
**Description:** Next-generation online shopping platform

**Issues:** SHOP-101, SHOP-102, SHOP-103  
**Labels:** BUG, FEATURE, ENHANCEMENT

### Mobile App Redesign Project (MOBILE)
**Type:** Agile, Planning  
**Team:** Beyond Gravity  
**Description:** Complete redesign of mobile application

**Issues:** MOBILE-201, MOBILE-202, MOBILE-203  
**Labels:** UI, ANDROID, IOS

### Infrastructure Upgrade Project (INFRA)
**Type:** Agile, In Progress  
**Team:** Beyond Gravity  
**Description:** Cloud infrastructure modernization

**Issues:** INFRA-301, INFRA-302, INFRA-303  
**Labels:** AWS, SECURITY, PERFORMANCE

---

## ⚙️ Configuration

### Database
- **Type:** SQLite
- **Location:** `database.db`
- **Encryption:** Fernet (sensitive fields)

### Environment
- **Mode:** Development
- **Flask Debug:** True
- **Secret Key:** Configured in config.py

### Security
- **Login Attempts:** Max 5 before lockout
- **Lockout Duration:** 30 minutes
- **Password Hashing:** Argon2id (cost=3, memory=64MB)

---

## 🐛 Troubleshooting

### Password Manager Not Running
```bash
# Make sure you're in the project directory
cd "/home/KALPESH/Stuffs/Project Management"

# Verify Python 3.7+
python3 --version

# Test basic command
python3 password_manager.py --help
```

### Can't Login
```bash
# Reset password to default
python password_manager.py reset-password
# Use: password123

# Or unlock all accounts
python password_manager.py unlock-all
```

### Database Issues
```bash
# Recreate all sample data
python create_sample_data.py

# This will reset the database completely
```

### User Locked Out
```bash
# Method 1: Unlock all
python password_manager.py unlock-all

# Method 2: Reset specific password
python password_manager.py reset-password --username john_doe
```

---

## 📞 Support Information

**For Password Management:**
- See [PASSWORD_MANAGER_README.md](PASSWORD_MANAGER_README.md)
- Run: `python password_manager.py --help`

**For Sample Data:**
- Re-run: `python create_sample_data.py`
- Check models.py for data structure

**For Application Issues:**
- Check app.py for configuration
- Review logs in console output
- Verify database.db exists

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Database created successfully
- [ ] 4 projects exist (NUC, SHOP, MOBILE, INFRA)
- [ ] 24 total issues created
- [ ] 4 test users can login
- [ ] Password manager script works
- [ ] Admin dashboard loads
- [ ] All projects visible in UI
- [ ] Issues display in kanban board

---

## 🎓 Learning Resources

The system demonstrates:
- ✅ Agile project management (sprints, epics, kanban)
- ✅ User authentication and authorization
- ✅ Database relationships (many-to-many, foreign keys)
- ✅ Password security best practices
- ✅ CLI tool development with Click
- ✅ Flask application structure

---

## 📅 Last Updated

**Date:** February 3, 2026  
**Changes:** 
- Added 3 new projects (SHOP, MOBILE, INFRA)
- Expanded issues from 15 to 24
- Created password_manager.py tool
- Updated documentation

---

## 📜 Files Modified/Created

**Modified:**
- `create_sample_data.py` - Expanded with 4 projects, 24 issues, 13 labels

**Created:**
- `password_manager.py` - Complete password management tool
- `PASSWORD_MANAGER_README.md` - Comprehensive password manager documentation
- `ENHANCED_SAMPLE_DATA.md` - This file (overview and guide)

---

**System Status:** ✅ **READY FOR USE**

All data is loaded and the application is ready for testing, demonstration, and development!

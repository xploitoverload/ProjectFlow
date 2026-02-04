# 📚 Complete Application Manual - Project Management System

**Last Updated**: February 3, 2026  
**Version**: 1.0  
**For**: All Users (Employee, Manager, Admin)

---

## 📑 Table of Contents

1. [Quick Start](#quick-start)
2. [System Architecture](#system-architecture)
3. [File Structure & Purposes](#file-structure--purposes)
4. [Complete User Roles](#complete-user-roles)
5. [All Features & How to Use](#all-features--how-to-use)
6. [All Routes & Endpoints](#all-routes--endpoints)
7. [Database Reference](#database-reference)
8. [Forms & Input Validation](#forms--input-validation)
9. [Visual Workflows](#visual-workflows)
10. [Admin Manual](#admin-manual)
11. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### For Employees
```
1. Go to: http://localhost:5000/login
2. Enter credentials (username/password)
3. Click "Dashboard" in sidebar
4. Start using features
```

### For Admins
```
Same as employees BUT you get additional:
- Admin Panel (Navbar)
- Project Management
- User Management
- Report Approval
- Statistics Dashboard
```

### For Managers
```
- View team progress
- Approve/Review updates
- See team statistics
```

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                    PROJECT MANAGEMENT SYSTEM                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  FRONTEND LAYER (HTML/CSS/JavaScript)                              │
│  ├─ base.html                (Main layout, navigation)              │
│  ├─ progress/                (7 templates for progress updates)     │
│  ├─ admin/                   (Admin dashboard templates)            │
│  ├─ projects/                (Project management templates)         │
│  └─ auth/                    (Login, registration)                  │
│                                                                     │
│  ↓ ROUTING LAYER (Flask Blueprints)                                │
│                                                                     │
│  ROUTE LAYER (Python)                                              │
│  ├─ auth.py     (5 routes)   Login, Logout, Register               │
│  ├─ main.py     (6 routes)   Dashboard, Reports                    │
│  ├─ admin.py    (8 routes)   Admin functions                       │
│  ├─ projects.py (12 routes)  Project CRUD                          │
│  ├─ api.py      (4 routes)   API endpoints                         │
│  └─ progress.py (10 routes)  Progress tracking                     │
│                                                                     │
│  ↓ BUSINESS LOGIC (Services, Repositories)                         │
│                                                                     │
│  MODEL LAYER (SQLAlchemy ORM)                                      │
│  ├─ User              (Authentication, roles)                      │
│  ├─ Project           (Project management)                         │
│  ├─ Issue             (Issue tracking)                             │
│  ├─ ProgressUpdate    (Progress reporting)                         │
│  └─ Report            (Report generation)                          │
│                                                                     │
│  ↓ ENCRYPTION LAYER (Fernet Symmetric)                             │
│                                                                     │
│  DATABASE LAYER (SQLite)                                           │
│  ├─ user              (5 tables)                                   │
│  ├─ project           (Projects table)                             │
│  ├─ issue             (Issues table)                               │
│  ├─ progress_update   (27 columns)                                 │
│  └─ report            (Reports table)                              │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## 📂 File Structure & Purposes

### ROOT LEVEL FILES

```
/home/KALPESH/Stuffs/Project Management/
├── app.py                           ← Main Flask app (DEPRECATED - use run.py)
├── run.py                           ← Launch point (USE THIS to start)
├── config.py                        ← Configuration (Database, Keys, etc.)
├── models.py                        ← All database models
├── requirements.txt                 ← Python dependencies
│
├── 🔑 PASSWORD MANAGEMENT
├── password_manager.py              ← Reset/create user passwords
├── fix_user_passwords.py            ← Emergency password fix
├── reset_user_passwords.py          ← Batch reset passwords
│
├── 💾 DATABASE INITIALIZATION
├── init_db.py                       ← Create empty database
├── init_reports.py                  ← Initialize reports
├── create_sample_data.py            ← Create sample projects/issues
├── migrate_db.py                    ← Database migration script
│
├── 🧪 TESTING & DEBUGGING
├── comprehensive_test.py            ← Full system test
├── test_routes.py                   ← Test all routes
├── test_functionality.py            ← Test features
├── debug_login.py                   ← Debug authentication
├── diagnose_app.py                  ← Diagnose problems
│
├── 📄 DOCUMENTATION (70+ files)
├── README.md                        ← Project overview
├── QUICK_START.md                   ← Getting started
├── PROGRESS_UPDATE_*.md             ← Progress feature docs
├── COMPLETE_JIRA_*.md               ← Project feature docs
└── ... (40+ more documentation files)
```

### APP DIRECTORY STRUCTURE

```
app/
├── __init__.py                      ← App factory (creates Flask app)
├── forms.py                         ← All form classes (validation)
│
├── 🛣️ ROUTES (6 Blueprint files)
├── routes/
│   ├── __init__.py
│   ├── auth.py                      ← Login/Register/Logout
│   ├── main.py                      ← Dashboard, Home, Reports
│   ├── projects.py                  ← Project CRUD operations
│   ├── admin.py                     ← Admin dashboard, user management
│   ├── api.py                       ← REST API endpoints
│   └── progress.py                  ← Progress update tracking
│
├── 🎨 TEMPLATES
├── templates/
│   ├── base.html                    ← Main layout (all pages extend this)
│   ├── index.html                   ← Home page
│   ├── dashboard.html               ← User dashboard
│   ├── auth/                        ← Login, Register pages
│   ├── progress/                    ← 7 Progress update templates
│   ├── projects/                    ← Project management templates
│   ├── admin/                       ← Admin dashboard templates
│   └── reports/                     ← Report templates
│
├── 🔒 SECURITY
├── security/
│   ├── __init__.py
│   ├── encryption.py                ← Encryption/Decryption
│   ├── validators.py                ← Input validation
│   └── decorators.py                ← @login_required, @admin_required
│
├── 📦 DATABASE MODELS
├── models/
│   ├── __init__.py
│   ├── user.py                      ← User model
│   ├── project.py                   ← Project model
│   ├── issue.py                     ← Issue model
│   └── report.py                    ← Report model
│
├── 🔧 SERVICES & UTILITIES
├── services/
│   ├── __init__.py
│   ├── project_service.py           ← Project business logic
│   ├── issue_service.py             ← Issue business logic
│   └── report_service.py            ← Report generation
│
├── 💾 REPOSITORIES
├── repositories/
│   ├── __init__.py
│   ├── project_repo.py              ← Query projects
│   ├── issue_repo.py                ← Query issues
│   └── user_repo.py                 ← Query users
│
├── 🌐 MIDDLEWARE & UTILITIES
├── middleware/
│   ├── __init__.py
│   └── auth_middleware.py           ← Authentication checks
│
├── ✅ SCHEMAS
├── schemas/
│   ├── __init__.py
│   ├── project_schema.py            ← API response formats
│   └── issue_schema.py              ← API response formats
│
└── 📊 STATIC FILES
static/
├── css/
│   ├── bootstrap.min.css            ← Bootstrap framework
│   ├── style.css                    ← Custom CSS
│   └── responsive.css               ← Mobile styles
│
├── js/
│   ├── bootstrap.bundle.min.js      ← Bootstrap JS
│   ├── main.js                      ← Global JavaScript
│   ├── form-validation.js           ← Form validation
│   └── progress-dates.js            ← Progress form logic
│
└── images/
    ├── logo.png                     ← Application logo
    └── favicon.ico                  ← Browser tab icon
```

---

## 👥 Complete User Roles

### 1️⃣ EMPLOYEE

**What they can do:**
```
✓ Submit progress updates
✓ View own progress history
✓ Edit pending updates (awaiting review)
✓ View dashboard with personal stats
✓ View assigned issues/tasks
✓ See feedback from managers
✓ View announcements
```

**What they CANNOT do:**
```
✗ See other employees' updates
✗ Approve/review updates
✗ Create new projects
✗ Delete anything
✗ Access admin panel
✗ Change system settings
```

**Access URLs:**
```
GET  /                              → Home page
GET  /dashboard                     → Personal dashboard
GET  /progress/submit               → Create new progress update
GET  /progress/my-updates           → View all own updates
GET  /progress/view/<id>            → View single update
GET  /progress/edit/<id>            → Edit pending update
POST /logout                        → Sign out
```

---

### 2️⃣ MANAGER

**What they can do:**
```
✓ Everything Employee can do
✓ View team progress updates
✓ Approve/reject progress updates
✓ Add feedback to updates
✓ View team statistics & reports
✓ Identify at-risk projects
✓ Create issues for team
✓ View project timeline
```

**What they CANNOT do:**
```
✗ Delete data permanently
✗ Manage other departments
✗ Change system settings
✗ Reset passwords
✗ Create new projects (only assigned ones)
```

**Access URLs:**
```
GET  /admin/pending                 → Reviews to do
GET  /admin/all                     → All updates with filters
GET  /admin/review/<id>             → Review interface
POST /admin/review/<id>             → Submit feedback
GET  /admin/stats                   → Team statistics
```

---

### 3️⃣ ADMIN (Full Access)

**What they can do:**
```
✓ Everything Manager can do
✓ Create/Edit/Delete projects
✓ Create/Edit/Delete users
✓ Create/Edit/Delete issues
✓ Reset user passwords
✓ View all system reports
✓ Configure system settings
✓ Manage user roles
✓ Access logs & analytics
✓ Create backup reports
```

**Admin URLs:**
```
GET  /admin                         → Admin dashboard
GET  /admin/projects                → Manage projects
POST /admin/projects/new            → Create project
GET  /admin/projects/<id>/edit      → Edit project
POST /admin/projects/<id>/delete    → Delete project

GET  /admin/users                   → Manage users
POST /admin/users/new               → Create user
GET  /admin/users/<id>/edit         → Edit user
POST /admin/users/<id>/delete       → Delete user

GET  /admin/issues                  → Manage issues
POST /admin/issues/new              → Create issue
GET  /admin/issues/<id>/edit        → Edit issue
```

---

## ⭐ All Features & How to Use

### FEATURE 1: Progress Update Tracking

**What is it?**
Employees submit weekly/daily/monthly progress updates. Managers review and approve.

**How to use (Employee):**

```
Step 1: Click "Progress Updates" → "Submit Update"
        ✓ You see the form with 13 sections

Step 2: Fill required fields
        • Reporting Period: Select Daily/Weekly/Monthly
        • Start/End Dates: Auto-fill or manual
        • Completed Work: What you finished
        • Work In Progress: What you're doing now
        • Hours Spent: 0-720 hours
        • Project Status: On Track / At Risk / Delayed
        • Next Priorities: What's next

Step 3: Fill optional sections
        • Blocked Tasks: What's blocking you
        • Challenges: What's difficult
        • Risks & Dependencies: What could go wrong
        • Notes: Additional info

Step 4: Click "Submit"
        ✓ Data saved to database
        ✓ Shows in "Pending" status
        ✓ Manager gets notification

Step 5: Manager reviews
        ✓ You get feedback
        ✓ Status changes to "Approved" or "Needs Revision"

Step 6: If needs revision
        • Click "Edit" button
        • Make changes
        • Resubmit
```

**How to use (Manager/Admin):**

```
Step 1: Click "Progress Reviews" → "Pending"
        ✓ See all awaiting your review

Step 2: Click on an update
        ✓ Left: Employee's submission
        ✓ Right: Your feedback form

Step 3: Read the submission carefully
        ✓ Check for blocked tasks (⚠️ warning)
        ✓ Check for escalations (🔴 red)
        ✓ Check status: on_track / at_risk / delayed

Step 4: Add feedback
        • Type in comment box
        • Use quick templates: [👍 Approve] or [⚠️ Needs Info]
        • Select status: Approved / Pending / Needs Revision

Step 5: Click "Submit Review"
        ✓ Feedback saved
        ✓ Employee gets notification
        ✓ Update moves to appropriate status
```

**Data Sections (25 fields total):**

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| reporting_period | Dropdown | Yes | daily/weekly/monthly |
| period_start_date | Date | Yes | When period starts |
| period_end_date | Date | Yes | When period ends |
| completed_work | Text (1000 chars) | Yes | What was done |
| work_in_progress | Text (1000 chars) | Yes | Current work |
| blocked_tasks | Text (500 chars) | No | What's blocked |
| blocked_reasons | Text (500 chars) | No | Why it's blocked |
| hours_spent | Number (0-720) | Yes | Hours worked |
| effort_level | Dropdown | Yes | low/medium/high |
| individual_contributions | Text (1000 chars) | Yes | Your contributions |
| team_work | Text (500 chars) | No | Team collaboration |
| features_worked | Text (500 chars) | No | Features developed |
| bugs_fixed | Text (500 chars) | No | Bugs resolved |
| improvements | Text (500 chars) | No | Improvements made |
| project_status | Dropdown | Yes | on_track/at_risk/delayed |
| risks_dependencies | Text (500 chars) | No | Risks & dependencies |
| challenges | Text (500 chars) | No | Challenges faced |
| next_priorities | Text (500 chars) | Yes | What's next |
| notes | Text (500 chars) | No | Additional notes |
| escalations | Text (500 chars) | No | Escalations needed |

---

### FEATURE 2: Project Management

**What is it?**
Create, organize, and track projects with issues/tasks.

**How to use (Employee):**

```
Step 1: Click "Projects" in sidebar
        ✓ See all active projects

Step 2: Click a project name
        ✓ View project details
        ✓ See all issues in project
        ✓ View team members

Step 3: View issues assigned to you
        ✓ Filter by status: Open, In Progress, Closed
        ✓ Sort by priority: High, Medium, Low
        ✓ See due dates

Step 4: Update issue status
        • Click issue
        • Change status (if permitted)
        • Add comments
```

**How to use (Admin):**

```
Step 1: Click Admin → Projects
        ✓ See all projects

Step 2: Create new project
        • Click "New Project"
        • Enter name, description, team members
        • Set status: Planning/Active/Completed/On Hold
        • Click "Create"

Step 3: Edit project
        • Click project name
        • Edit details
        • Add/remove team members
        • Click "Save"

Step 4: Delete project
        • Click project
        • Click "Delete" button
        ⚠️ WARNING: Deletes all issues too!
```

**Project Fields:**

| Field | Type | Example |
|-------|------|---------|
| name | Text | "Mobile App Redesign" |
| description | Text | "Redesign mobile UI for iOS and Android" |
| status | Dropdown | Planning / Active / Completed / On Hold |
| start_date | Date | 2026-02-01 |
| end_date | Date | 2026-05-31 |
| team_members | List | john_doe, jane_smith, bob_wilson |
| priority | Dropdown | Low / Medium / High / Critical |

---

### FEATURE 3: Issue Tracking

**What is it?**
Track tasks, bugs, and features within projects.

**How to use (Employee):**

```
Step 1: Click "Issues" in sidebar
        ✓ See issues assigned to you

Step 2: Filter issues
        • By project: Dropdown
        • By status: Open/In Progress/Done
        • By priority: High/Medium/Low
        • By assignee: Your name

Step 3: View issue details
        • Title: What needs to be done
        • Description: Details
        • Status: Current state
        • Priority: Urgency level
        • Assigned to: Who's working on it
        • Due date: When it's due
        • Comments: Discussion thread

Step 4: Add comment
        • Type in comment box
        • Click "Add Comment"
        • Visible to all team members
```

**How to use (Admin):**

```
Step 1: Click Admin → Issues
        ✓ See all issues

Step 2: Create new issue
        • Click "New Issue"
        • Select project
        • Enter title & description
        • Set priority: Low/Medium/High
        • Assign to: Team member
        • Set due date
        • Click "Create"

Step 3: Edit issue
        • Click issue
        • Change status: Open → In Progress → Done
        • Reassign to different person
        • Change due date
        • Click "Save"

Step 4: Delete issue
        • Click issue
        • Click "Delete"
        ⚠️ WARNING: Cannot undo!
```

**Issue Fields:**

| Field | Type | Values |
|-------|------|--------|
| title | Text | "Fix login bug" |
| description | Text | Detailed description |
| status | Dropdown | Open / In Progress / Closed |
| priority | Dropdown | Low / Medium / High |
| project_id | Foreign Key | Links to Project |
| assigned_to | User ID | Person responsible |
| due_date | Date | 2026-02-10 |
| created_by | User ID | Who created it |

---

### FEATURE 4: Reports & Analytics

**What is it?**
Generate progress reports and view team statistics.

**How to use (Employee):**

```
Step 1: Click "Reports" in sidebar
        ✓ See your personal reports

Step 2: View your statistics
        ✓ Total updates submitted
        ✓ Average hours per week
        ✓ Status breakdown (on track/at risk)
        ✓ Monthly trend graph

Step 3: Download report
        • Click "Download as PDF"
        • Save to computer
```

**How to use (Manager/Admin):**

```
Step 1: Click "Reports" or Admin → Stats
        ✓ See team/system statistics

Step 2: View team metrics
        ✓ Team progress summary
        ✓ Who submitted on time
        ✓ At-risk projects
        ✓ Total hours logged
        ✓ Effort distribution (low/medium/high)

Step 3: View individual employee stats
        • Click employee name
        • See their history
        • View trend over time

Step 4: Export data
        • Click "Download Report"
        • Choose format: PDF or CSV
        • Save for management use
```

---

### FEATURE 5: User Management (Admin Only)

**How to use:**

```
Step 1: Click Admin → Users
        ✓ See list of all users

Step 2: Create new user
        • Click "New User" button
        • Enter username (unique)
        • Enter email address
        • Set password (min 6 characters)
        • Select role: admin/manager/developer/designer/user
        • Click "Create User"

Step 3: Edit user
        • Click user's name
        • Change email
        • Change role
        • Change department
        • Click "Save"

Step 4: Reset password (if user locked out)
        • Click user's name
        • Click "Reset Password"
        • Enter new password
        • Click "Reset"
        ✓ User can now login with new password

Step 5: Delete user
        ⚠️ WARNING: Deletes all their data!
        • Click user
        • Click "Delete"
        • Confirm deletion

Alternative: Use password_manager.py script
        python password_manager.py reset-password
        → Follow prompts to reset
```

---

## 🛣️ All Routes & Endpoints

### AUTHENTICATION ROUTES (auth.py)

| Method | Route | Purpose | Access |
|--------|-------|---------|--------|
| GET/POST | `/login` | Login page and process | Public |
| POST | `/logout` | Sign out | Logged in |
| GET/POST | `/register` | Register new account | Public |
| GET | `/forgot-password` | Password recovery | Public |
| POST | `/reset-password/<token>` | Reset with token | Public |

**Examples:**

```bash
# Login
POST /login
Body: { "username": "john", "password": "secret123" }
Response: Redirect to /dashboard

# Register
POST /register
Body: { 
  "username": "newuser",
  "email": "new@email.com",
  "password": "pass123"
}
Response: Redirect to /login

# Logout
POST /logout
Response: Redirect to /
```

---

### MAIN ROUTES (main.py)

| Method | Route | Purpose | Access |
|--------|-------|---------|--------|
| GET | `/` | Home page | Public |
| GET | `/dashboard` | User dashboard | Logged in |
| GET | `/projects` | List all projects | Logged in |
| GET | `/projects/<id>` | View project details | Logged in |
| GET | `/issues` | List all issues | Logged in |
| GET | `/reports` | View reports | Logged in |

---

### PROGRESS ROUTES (progress.py - Main Feature)

| Method | Route | Purpose | Access | Data |
|--------|-------|---------|--------|------|
| GET | `/progress/submit` | Show submit form | Employee+ | Form object |
| POST | `/progress/submit` | Save new update | Employee+ | Form data |
| GET | `/progress/my-updates` | List own updates | Employee+ | Paginated list |
| GET | `/progress/view/<id>` | View single update | Employee+ | Update object |
| GET | `/progress/edit/<id>` | Edit form | Owner only | Pre-filled form |
| POST | `/progress/edit/<id>` | Save changes | Owner only | Form data |
| GET | `/progress/admin/pending` | Pending queue | Manager+ | Paginated list |
| GET | `/progress/admin/all` | All updates filtered | Manager+ | Paginated list |
| GET | `/progress/admin/review/<id>` | Review interface | Manager+ | Update + Form |
| POST | `/progress/admin/review/<id>` | Save review | Manager+ | Form data |
| GET | `/progress/admin/stats` | Statistics | Manager+ | Stats dict |

**Example API calls:**

```bash
# Submit new progress update
POST /progress/submit
Body: {
  "reporting_period": "weekly",
  "period_start_date": "2026-02-01",
  "period_end_date": "2026-02-07",
  "completed_work": "Fixed authentication bug...",
  "work_in_progress": "Working on API endpoints...",
  "hours_spent": 40,
  "effort_level": "high",
  "project_status": "on_track",
  ... (20 more fields)
}
Response: Redirect to /progress/my-updates

# View single update
GET /progress/view/123
Response: HTML page with update details

# Get pending reviews (Manager)
GET /progress/admin/pending?page=1
Response: HTML with paginated list (15 per page)

# Filter updates (Manager)
GET /progress/admin/all?status=approved&user_id=5&period=weekly&page=1
Response: HTML with filtered results

# Submit review
POST /progress/admin/review/123
Body: {
  "review_status": "approved",
  "admin_comments": "Great work! Keep it up."
}
Response: Redirect to /progress/admin/pending
```

---

### PROJECT ROUTES (projects.py)

| Method | Route | Purpose | Admin Only |
|--------|-------|---------|------------|
| GET | `/admin/projects` | List all projects | Yes |
| POST | `/admin/projects` | Create project | Yes |
| GET | `/admin/projects/<id>` | View project | Yes |
| POST | `/admin/projects/<id>` | Update project | Yes |
| POST | `/admin/projects/<id>/delete` | Delete project | Yes |
| GET | `/admin/projects/<id>/issues` | Project's issues | Yes |

---

### ADMIN ROUTES (admin.py)

| Method | Route | Purpose | Admin Only |
|--------|-------|---------|------------|
| GET | `/admin` | Admin dashboard | Yes |
| GET | `/admin/users` | List users | Yes |
| POST | `/admin/users` | Create user | Yes |
| GET | `/admin/users/<id>/edit` | Edit user form | Yes |
| POST | `/admin/users/<id>` | Update user | Yes |
| POST | `/admin/users/<id>/delete` | Delete user | Yes |
| POST | `/admin/users/<id>/reset-password` | Reset password | Yes |
| GET | `/admin/settings` | System settings | Yes |

---

### API ROUTES (api.py - For Mobile/External Apps)

| Method | Route | Purpose | Format |
|--------|-------|---------|--------|
| GET | `/api/projects` | Get all projects | JSON |
| GET | `/api/projects/<id>` | Get project details | JSON |
| GET | `/api/issues` | Get all issues | JSON |
| GET | `/api/issues/<id>` | Get issue details | JSON |

**Example API response:**

```json
GET /api/projects
Response: {
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Mobile App",
      "status": "active",
      "start_date": "2026-01-01",
      "team_members": ["john_doe", "jane_smith"]
    }
  ]
}
```

---

## 💾 Database Reference

### TABLE 1: `user` (User Accounts)

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,      -- Login name
    email_encrypted TEXT NOT NULL,             -- Encrypted email
    password_hash VARCHAR(255) NOT NULL,       -- Hashed password
    role VARCHAR(20) DEFAULT 'user',           -- admin/manager/developer/etc
    department VARCHAR(100),                   -- Which team
    full_name VARCHAR(120),                    -- Display name
    is_active BOOLEAN DEFAULT TRUE,            -- Account enabled?
    failed_login_attempts INT DEFAULT 0,       -- For lockout
    created_at TIMESTAMP DEFAULT NOW(),        -- When created
    last_login TIMESTAMP,                      -- Last login
    avatar_url VARCHAR(255),                   -- Profile picture
    phone_encrypted TEXT,                      -- Encrypted phone
    address_encrypted TEXT,                    -- Encrypted address
);

ENCRYPTED FIELDS: email, phone, address
USE: password_manager.py reset-password
```

---

### TABLE 2: `project` (Projects)

```sql
CREATE TABLE project (
    id INTEGER PRIMARY KEY,
    name VARCHAR(150) NOT NULL,                -- Project name
    description TEXT,                          -- Details
    status VARCHAR(20),                        -- planning/active/completed
    start_date DATE,                           -- Start date
    end_date DATE,                             -- End date
    priority VARCHAR(20),                      -- low/medium/high
    created_by INTEGER NOT NULL,               -- Creator ID
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    budget DECIMAL(10,2),                      -- Budget
    FOREIGN KEY (created_by) REFERENCES user(id)
);

USAGE: Admin creates projects, team members assigned
EMPLOYEES SEE: All projects, their assigned ones
```

---

### TABLE 3: `issue` (Tasks/Bugs)

```sql
CREATE TABLE issue (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,               -- Which project
    title VARCHAR(200) NOT NULL,               -- Issue title
    description TEXT,                          -- Details
    status VARCHAR(20) DEFAULT 'open',         -- open/in_progress/closed
    priority VARCHAR(20) DEFAULT 'medium',     -- low/medium/high
    assigned_to INTEGER,                       -- Assigned person
    created_by INTEGER NOT NULL,               -- Who created it
    due_date DATE,                             -- Due date
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (project_id) REFERENCES project(id),
    FOREIGN KEY (assigned_to) REFERENCES user(id),
    FOREIGN KEY (created_by) REFERENCES user(id)
);

USAGE: Track bugs, features, tasks
FILTER: By status, priority, assignee
```

---

### TABLE 4: `progress_update` (Progress Tracking) - 27 Columns

```sql
CREATE TABLE progress_update (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    
    -- REPORTING PERIOD
    reporting_period VARCHAR(20),              -- daily/weekly/monthly
    period_start_date DATE,
    period_end_date DATE,
    
    -- WORK COMPLETION (Encrypted)
    completed_work TEXT,                       -- ✓ ENCRYPTED
    work_in_progress TEXT,                     -- ✓ ENCRYPTED
    blocked_tasks TEXT,                        -- ✓ ENCRYPTED
    blocked_reasons TEXT,                      -- ✓ ENCRYPTED
    
    -- EFFORT & STATUS
    hours_spent INT (0-720),
    effort_level VARCHAR(20),                  -- low/medium/high
    
    -- CONTRIBUTIONS (Encrypted)
    individual_contributions TEXT,             -- ✓ ENCRYPTED
    team_work TEXT,                            -- ✓ ENCRYPTED
    features_worked TEXT,                      -- ✓ ENCRYPTED
    bugs_fixed TEXT,                           -- ✓ ENCRYPTED
    improvements TEXT,                         -- ✓ ENCRYPTED
    
    -- PROJECT STATUS
    project_status VARCHAR(20),                -- on_track/at_risk/delayed
    
    -- RISKS & CHALLENGES (Encrypted)
    risks_dependencies TEXT,                   -- ✓ ENCRYPTED
    challenges TEXT,                           -- ✓ ENCRYPTED
    
    -- FORWARD PLANNING (Encrypted)
    next_priorities TEXT,                      -- ✓ ENCRYPTED
    notes TEXT,                                -- ✓ ENCRYPTED
    escalations TEXT,                          -- ✓ ENCRYPTED
    
    -- REVIEW & ADMIN
    submitted_at TIMESTAMP,
    review_status VARCHAR(20),                 -- pending/approved/needs_revision
    reviewed_by INTEGER,
    reviewed_at TIMESTAMP,
    admin_comments TEXT,                       -- ✓ ENCRYPTED
    
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (reviewed_by) REFERENCES user(id)
);

ENCRYPTED FIELDS (15 total): completed_work, work_in_progress, blocked_tasks,
                              blocked_reasons, individual_contributions, team_work,
                              features_worked, bugs_fixed, improvements,
                              risks_dependencies, challenges, next_priorities,
                              notes, escalations, admin_comments

ENCRYPTION: Uses Fernet symmetric encryption (256-bit)
STORAGE: Encrypted in database, auto-decrypted when accessed
```

---

### TABLE 5: `report` (Generated Reports)

```sql
CREATE TABLE report (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200),                        -- Report name
    user_id INTEGER,                           -- For user reports
    report_type VARCHAR(50),                   -- daily/weekly/monthly
    period_start DATE,
    period_end DATE,
    content TEXT,                              -- Report content
    generated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

USAGE: Store generated reports for download
GENERATED BY: Employees, managers, admins
```

---

## 📋 Forms & Input Validation

### FORM 1: ProgressUpdateForm (25 Fields)

**Location**: `app/forms.py`

```python
# Required Fields
reporting_period = SelectField(
    'Reporting Period',
    choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
    validators=[DataRequired()]
)

period_start_date = DateField(
    'Period Start Date',
    validators=[DataRequired()]
)

period_end_date = DateField(
    'Period End Date',
    validators=[DataRequired()]
)

completed_work = TextAreaField(
    'Completed Work',
    validators=[DataRequired(), Length(min=10, max=1000)],
    render_kw={"rows": 4, "placeholder": "What did you complete this period..."}
)

work_in_progress = TextAreaField(
    'Work In Progress',
    validators=[DataRequired(), Length(min=10, max=1000)]
)

hours_spent = IntegerField(
    'Hours Spent',
    validators=[DataRequired(), NumberRange(min=0, max=720)]
)

effort_level = SelectField(
    'Effort Level',
    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
    validators=[DataRequired()]
)

project_status = SelectField(
    'Project Status',
    choices=[('on_track', 'On Track'), ('at_risk', 'At Risk'), ('delayed', 'Delayed')],
    validators=[DataRequired()]
)

next_priorities = TextAreaField(
    'Next Priorities',
    validators=[DataRequired(), Length(min=10, max=500)]
)

# Optional Fields
blocked_tasks = TextAreaField('Blocked Tasks', validators=[Optional(), Length(max=500)])
blocked_reasons = TextAreaField('Reasons for Blocking', validators=[Optional(), Length(max=500)])
individual_contributions = TextAreaField('Individual Contributions', validators=[Optional(), Length(max=1000)])
team_work = TextAreaField('Team Work', validators=[Optional(), Length(max=500)])
features_worked = TextAreaField('Features Worked On', validators=[Optional(), Length(max=500)])
bugs_fixed = TextAreaField('Bugs Fixed', validators=[Optional(), Length(max=500)])
improvements = TextAreaField('Improvements Made', validators=[Optional(), Length(max=500)])
risks_dependencies = TextAreaField('Risks & Dependencies', validators=[Optional(), Length(max=500)])
challenges = TextAreaField('Challenges Faced', validators=[Optional(), Length(max=500)])
notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=500)])
escalations = TextAreaField('Escalations Required', validators=[Optional(), Length(max=500)])

submit = SubmitField('Submit Progress Update')
```

**Validation Rules**:
- All required fields must be filled
- Text minimum 10 characters (except optional)
- Text maximum 500-1000 characters
- Hours: 0-720 only
- Dates: Must be valid
- CSRF protection on all submissions

---

### FORM 2: ReviewProgressUpdateForm (2 Fields)

**Location**: `app/forms.py`

```python
review_status = SelectField(
    'Review Status',
    choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('needs_revision', 'Needs Revision')
    ],
    validators=[DataRequired()]
)

admin_comments = TextAreaField(
    'Your Feedback',
    validators=[Optional(), Length(max=1000)],
    render_kw={
        "rows": 6,
        "placeholder": "Provide constructive feedback..."
    }
)

submit = SubmitField('Submit Review')
```

---

### FORM 3: LoginForm

```python
username = StringField(
    'Username',
    validators=[DataRequired(), Length(min=3, max=80)]
)

password = PasswordField(
    'Password',
    validators=[DataRequired()]
)

remember_me = BooleanField('Remember Me')
submit = SubmitField('Sign In')
```

---

### FORM 4: RegisterForm

```python
username = StringField(
    'Username',
    validators=[DataRequired(), Length(min=3, max=80), 
                Regexp('^[A-Za-z0-9_]*$')]
)

email = StringField(
    'Email',
    validators=[DataRequired(), Email()]
)

password = PasswordField(
    'Password',
    validators=[DataRequired(), Length(min=6)]
)

confirm_password = PasswordField(
    'Confirm Password',
    validators=[DataRequired(), EqualTo('password')]
)

submit = SubmitField('Register')
```

---

## 🎨 Visual Workflows

### WORKFLOW 1: Employee Submitting Progress Update

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMPLOYEE WORKFLOW                             │
└─────────────────────────────────────────────────────────────────┘

STEP 1: NAVIGATE TO FORM
┌──────────────────────────────────────┐
│ Sidebar: "Progress Updates"           │
│ Menu: "Submit New Update"             │ ← Click here
│                                       │
└──────────────────────────────────────┘
                   ↓
STEP 2: FORM APPEARS
┌──────────────────────────────────────────────────────────────┐
│ Form: Submit Progress Update                                  │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 📅 Reporting Period: [Weekly v]                         │  │
│ │ 📅 Start Date: [2026-02-01] (Auto-filled)              │  │
│ │ 📅 End Date: [2026-02-07] (Auto-filled)                │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ ✅ REQUIRED FIELDS                                      │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ 📝 Completed Work:                                      │  │
│ │ [Fixed authentication bug, implemented...]             │  │
│ │                                                          │  │
│ │ 📝 Work In Progress:                                    │  │
│ │ [Working on API endpoint documentation...]             │  │
│ │                                                          │  │
│ │ ⏱️  Hours Spent: [40]                                   │  │
│ │                                                          │  │
│ │ 💪 Effort Level: [High v]                              │  │
│ │                                                          │  │
│ │ 📊 Project Status: [On Track v]                         │  │
│ │                                                          │  │
│ │ 🎯 Next Priorities:                                     │  │
│ │ [Complete API docs, review pull requests...]           │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ ⚠️ OPTIONAL FIELDS (Click to expand)                   │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ 🚫 Blocked Tasks: [                          ]         │  │
│ │ 💬 Challenges: [                             ]         │  │
│ │ 📌 Escalations: [                            ]         │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ [Submit] [Save as Draft] [Cancel]                      │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                                │
└──────────────────────────────────────────────────────────────┘
                   ↓
STEP 3: VALIDATION
┌──────────────────────────────────────┐
│ System checks:                         │
│ ✓ All required fields filled?          │
│ ✓ Text length OK (min 10 chars)?       │
│ ✓ Hours 0-720?                         │
│ ✓ Valid dates?                         │
│ ✓ CSRF token valid?                    │
│                                        │
│ ❌ If error:                           │
│    → Shows red alert at top            │
│    → Invalid fields highlighted        │
│    → Cannot submit                     │
└──────────────────────────────────────┘
                   ↓
STEP 4: SAVE TO DATABASE
┌──────────────────────────────────────┐
│ 1. Create ProgressUpdate object       │
│ 2. Encrypt sensitive fields (15 of them)
│ 3. Set status = "pending"             │
│ 4. Save to database                   │
│ 5. Record submitted_at timestamp      │
│                                        │
└──────────────────────────────────────┘
                   ↓
STEP 5: CONFIRMATION
┌──────────────────────────────────────┐
│ ✅ Success!                            │
│ "Update submitted successfully"        │
│                                        │
│ Show: "View your updates"              │ ← Click
│                                        │
└──────────────────────────────────────┘
                   ↓
STEP 6: REDIRECT TO MY UPDATES
┌──────────────────────────────────────┐
│ List of YOUR progress updates:        │
│                                        │
│ ┌─ Weekly (Jan 27 - Feb 2) ──────┐   │
│ │ Status: 🟡 Pending             │   │
│ │ Submitted: Feb 3, 2:15 PM       │   │
│ │ [View] [Edit]                   │   │
│ └─────────────────────────────────┘   │
│                                        │
│ ┌─ Weekly (Jan 20 - Jan 26) ─────┐   │
│ │ Status: 🟢 Approved             │   │
│ │ Feedback: "Great work!"          │   │
│ │ [View]                          │   │
│ └─────────────────────────────────┘   │
│                                        │
└──────────────────────────────────────┘
                   ↓
STEP 7: MANAGER REVIEWS (Happens next)
┌──────────────────────────────────────┐
│ Manager sees notification:             │
│ "New update from John Doe"            │
│                                        │
│ Manager clicks "Pending Reviews"      │
│ Sees your update in queue              │
│ Reads your submission                  │
│ Adds feedback or approves              │
│                                        │
└──────────────────────────────────────┘
                   ↓
STEP 8: YOU GET NOTIFIED
┌──────────────────────────────────────┐
│ You get notification:                  │
│ "Your update was approved!"           │
│                                        │
│ OR                                     │
│                                        │
│ "Your update needs revision"           │
│ "Manager comment: Please add more..."  │
│                                        │
│ If revision needed:                    │
│ → Click [Edit]                        │
│ → Make changes                         │
│ → Resubmit                             │
│                                        │
└──────────────────────────────────────┘
```

---

### WORKFLOW 2: Manager Reviewing Update

```
┌─────────────────────────────────────────────────────────────────┐
│                    MANAGER WORKFLOW                              │
└─────────────────────────────────────────────────────────────────┘

STEP 1: NAVIGATE TO REVIEWS
┌──────────────────────────────────────┐
│ Sidebar: "Progress Reviews"           │
│ Menu: "Pending Reviews"               │ ← Click here
│                                       │
│ Badge shows: "5 pending"              │
│                                       │
└──────────────────────────────────────┘
                   ↓
STEP 2: SEE PENDING QUEUE
┌──────────────────────────────────────────────────────────────┐
│ Pending Reviews (5 total)                                     │
│                                                                │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 👤 John Doe                                             │  │
│ │ 📅 Weekly (Jan 27 - Feb 2)                              │  │
│ │ 📊 Status: On Track                                     │  │
│ │ ⏱️  Hours: 40                                           │  │
│ │ ⚠️  BLOCKED (Has blockers!)                             │  │
│ │ 🔴 Submitted: 3 days ago                                │  │
│ │ [View] [Review]                                         │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                                │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 👤 Jane Smith                                           │  │
│ │ 📅 Weekly (Jan 27 - Feb 2)                              │  │
│ │ 📊 Status: At Risk                                      │  │
│ │ ⏱️  Hours: 35                                           │  │
│ │ ✅ No Blockers                                          │  │
│ │ 🟡 Submitted: 2 days ago                                │  │
│ │ [View] [Review]                                         │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                                │
└──────────────────────────────────────────────────────────────┘
                   ↓
STEP 3: CLICK ON UPDATE TO REVIEW
┌──────────────────────────────────────────────────────────────┐
│ Split Screen Review Interface                                 │
│                                                                │
│ LEFT SIDE: EMPLOYEE'S SUBMISSION          RIGHT SIDE: YOUR REVIEW
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐
│ │ John Doe                    │  │ Review Form                 │
│ │ Weekly (Jan 27 - Feb 2)     │  │                             │
│ │ 📊 On Track                 │  │ Status: [Pending v]         │
│ │ ⏱️ 40 hours                 │  │                             │
│ │ 💪 High effort              │  │ ┌───────────────────────┐   │
│ │ ⚠️ Blocked                  │  │ │ Your Feedback:        │   │
│ │                             │  │ │                       │   │
│ │ Completed Work:             │  │ │ [Quick templates]     │   │
│ │ "Fixed auth bug, updated UI │  │ │ [👍 Approve] [⚠️Info]│   │
│ │  for mobile..."             │  │ │                       │   │
│ │                             │  │ │ Type here...          │   │
│ │ Work In Progress:           │  │ │                       │   │
│ │ "Working on API endpoints.."│  │ │ [Submit Review]       │   │
│ │                             │  │ └───────────────────────┘   │
│ │ Hours: 40                   │  │                             │
│ │                             │  │                             │
│ │ Blocked Tasks: ⚠️            │  │ (Sticky on scroll)          │
│ │ "API documentation delayed" │  │                             │
│ │                             │  │                             │
│ │ [Expand to see full...]     │  │                             │
│ │                             │  │                             │
│ └─────────────────────────────┘  └─────────────────────────────┘
│                                                                │
└──────────────────────────────────────────────────────────────┘
                   ↓
STEP 4: READ SUBMISSION CAREFULLY
┌──────────────────────────────────────┐
│ Questions to ask yourself:             │
│                                        │
│ ✓ Is the work completed sufficient?   │
│ ✓ Are there blockers? (⚠️ flag)       │
│ ✓ Is effort level realistic?          │
│ ✓ Is project status accurate?         │
│ ✓ Any red flags or concerns?          │
│                                        │
└──────────────────────────────────────┘
                   ↓
STEP 5: PROVIDE FEEDBACK
┌──────────────────────────────────────────────────────────────┐
│ Option 1: APPROVE                                             │
│   • Click "Status: Approve"                                   │
│   • Type: "Looks great! Keep up the good work."              │
│   • Click [Submit Review]                                     │
│   ✓ Status becomes GREEN                                      │
│   ✓ Employee notified                                         │
│                                                                │
│ Option 2: REQUEST REVISION                                    │
│   • Click "Status: Needs Revision"                           │
│   • Type: "Can you provide more details on blockers?"        │
│   • Click [Submit Review]                                     │
│   ✓ Status becomes BLUE                                       │
│   ✓ Employee gets notified                                    │
│   ✓ Employee can edit and resubmit                            │
│                                                                │
│ Option 3: PENDING (No decision)                              │
│   • Leave status as "Pending"                                 │
│   • Add comment: "Reviewing, will respond tomorrow"          │
│   • Click [Submit Review]                                     │
│   ✓ Saves your comment                                        │
│   ✓ Still shows in pending queue                              │
│                                                                │
└──────────────────────────────────────────────────────────────┘
                   ↓
STEP 6: SUBMISSION SAVED
┌──────────────────────────────────────┐
│ Review saved to database:              │
│ • Status changed to approved/revision  │
│ • Comments encrypted and stored        │
│ • Timestamp recorded                   │
│ • Reviewed_by set to your ID           │
│                                        │
└──────────────────────────────────────┘
                   ↓
STEP 7: NEXT PENDING
┌──────────────────────────────────────┐
│ Automatically shows next pending       │
│ OR                                     │
│ Returns to pending list                │
│                                        │
│ Badge updates: "4 pending" (was 5)    │
│                                        │
└──────────────────────────────────────┘
```

---

### WORKFLOW 3: Create New Project (Admin)

```
ADMIN CREATES PROJECT
        ↓
┌──────────────────────────────────────┐
│ Click: Admin → Projects → New Project │
│                                       │
│ Form appears:                         │
│ ✓ Project Name                        │
│ ✓ Description                         │
│ ✓ Status: Planning/Active             │
│ ✓ Start Date                          │
│ ✓ End Date                            │
│ ✓ Priority: High/Medium/Low           │
│ ✓ Team Members: Select from list      │
│                                       │
│ Click [Create]                        │
│                                       │
└──────────────────────────────────────┘
        ↓
PROJECT CREATED
        ↓
┌──────────────────────────────────────┐
│ Admin can now:                        │
│ • Create issues in this project       │
│ • Assign issues to team members       │
│ • Set project status/timeline         │
│ • Add/remove team members             │
│ • Delete entire project (⚠️)          │
│                                       │
│ Team members can:                     │
│ • See project on dashboard            │
│ • View assigned issues                │
│ • Submit progress updates             │
│                                       │
└──────────────────────────────────────┘
```

---

## 👨‍💼 Admin Manual

### How to Start the Application

**Method 1: Using run.py (Recommended)**
```bash
cd /home/KALPESH/Stuffs/Project\ Management
python run.py
```

**Method 2: Using Flask CLI**
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

**Method 3: Using Gunicorn (Production)**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

After starting, visit: `http://localhost:5000`

---

### How to Reset Password (Multiple Methods)

**METHOD 1: Using password_manager.py (RECOMMENDED)**
```bash
python password_manager.py reset-password

# Follow prompts:
# Username: admin
# New Password: ••••••
# Confirm Password: ••••••
```

**METHOD 2: List all users first**
```bash
python password_manager.py list-users

# Shows all usernames and roles
```

**METHOD 3: Create new user**
```bash
python password_manager.py create-user

# Create a completely new admin account
```

**METHOD 4: Emergency reset script**
```bash
python fix_user_passwords.py
```

---

### How to Create Sample Data

```bash
# Create 4 projects with 6 issues each = 24 issues
python create_sample_data.py

# Imports:
# - 4 projects: Ecommerce Platform, Mobile App, Dashboard, API
# - 24 issues across projects
# - Sample data for testing
```

---

### How to Initialize Database

```bash
# Fresh database setup
python init_db.py

# Creates empty tables:
# - user
# - project
# - issue
# - progress_update
# - report
```

---

### Admin Dashboard Features

```
Admin Panel (http://localhost:5000/admin)
│
├─ 📊 Dashboard
│  └─ System statistics, overview
│
├─ 👥 Users
│  ├─ List all users
│  ├─ Create new user
│  ├─ Edit user role/email
│  ├─ Reset user password
│  └─ Delete user
│
├─ 📁 Projects
│  ├─ List all projects
│  ├─ Create new project
│  ├─ Edit project details
│  ├─ Assign team members
│  └─ Delete project
│
├─ 🐛 Issues
│  ├─ List all issues
│  ├─ Create new issue
│  ├─ Assign to team member
│  ├─ Change status/priority
│  └─ Delete issue
│
├─ 📊 Progress Reviews
│  ├─ Pending reviews (count)
│  ├─ Review interface
│  ├─ All updates (filtered)
│  └─ Statistics dashboard
│
└─ ⚙️ Settings
   └─ System configuration
```

---

## 🔧 Troubleshooting

### Problem 1: Cannot Login

**Symptoms:**
```
"Invalid credentials" error
Can't remember password
Account locked
```

**Solutions:**

```bash
# Solution 1: Reset password
python password_manager.py reset-password
→ Enter username
→ Enter new password

# Solution 2: Check user exists
python password_manager.py list-users
→ See all users in system

# Solution 3: Create new admin
python password_manager.py create-user
→ Create new account
→ Use as admin temporarily
```

---

### Problem 2: Database Errors

**Symptoms:**
```
"No such table: user"
"Database is locked"
"Operational error"
```

**Solutions:**

```bash
# Solution 1: Reinitialize database
python init_db.py

# Solution 2: Delete and recreate
rm instance/project_mgmt.db
python init_db.py

# Solution 3: Run migrations
python migrate_db.py
```

---

### Problem 3: Can't Submit Progress Update

**Symptoms:**
```
Form won't submit
"This field is required"
Validation error
```

**Check:**
- All required fields filled (marked with *)
- Text fields have minimum 10 characters
- Hours is 0-720
- Dates are valid
- No special characters in fields
- CSRF token present (automatic)

---

### Problem 4: Data Not Showing

**Symptoms:**
```
Dashboard empty
No progress updates visible
Projects not showing
```

**Solutions:**

```bash
# Solution 1: Create sample data
python create_sample_data.py

# Solution 2: Check permissions
→ Login as admin
→ Check user role in database

# Solution 3: Clear cache
→ Hard refresh page (Ctrl+F5)
→ Clear browser cookies
→ Logout and login again
```

---

### Problem 5: Encryption Issues

**Symptoms:**
```
"Fernet token invalid"
"Decryption failed"
Encrypted fields show garbage
```

**Solutions:**

```bash
# Solution 1: Check encryption key
cat encryption.key
→ Should show 44-character string

# Solution 2: Regenerate key
rm encryption.key
→ New key will be created on next run

# Solution 3: Check .env file
cat .env
→ ENCRYPTION_KEY should match
→ DATABASE_URL should be valid
```

---

### Problem 6: Port Already in Use

**Symptoms:**
```
"Address already in use"
Port 5000 occupied
Cannot start server
```

**Solutions:**

```bash
# Solution 1: Kill existing process
lsof -i :5000
kill <PID>

# Solution 2: Use different port
python run.py --port 5001

# Solution 3: Check what's using port
netstat -tulpn | grep 5000
```

---

## 📞 Support & Commands Summary

### Quick Command Reference

```bash
# START APPLICATION
python run.py

# MANAGE USERS
python password_manager.py reset-password         # Reset password
python password_manager.py list-users             # List all users
python password_manager.py create-user            # Create new user

# DATABASE
python init_db.py                                 # Initialize database
python create_sample_data.py                      # Create 4 projects
python migrate_db.py                              # Run migrations

# TESTING
python comprehensive_test.py                      # Full system test
python test_routes.py                             # Test all routes
python test_functionality.py                      # Test features

# DEBUGGING
python debug_login.py                             # Debug login issues
python diagnose_app.py                            # Full diagnosis
```

---

## 📌 Important URLs

```
MAIN PAGES:
GET  http://localhost:5000/                      Home page
GET  http://localhost:5000/dashboard             User dashboard
GET  http://localhost:5000/login                 Login page
GET  http://localhost:5000/register              Register page

PROGRESS UPDATES:
GET  http://localhost:5000/progress/submit       New update form
GET  http://localhost:5000/progress/my-updates   My updates list
GET  http://localhost:5000/progress/view/1      View update #1
GET  http://localhost:5000/progress/edit/1      Edit update #1

MANAGER/ADMIN:
GET  http://localhost:5000/progress/admin/pending     Reviews to do
GET  http://localhost:5000/progress/admin/all         All updates
GET  http://localhost:5000/progress/admin/review/1   Review update #1
GET  http://localhost:5000/progress/admin/stats      Statistics

ADMIN ONLY:
GET  http://localhost:5000/admin                      Admin dashboard
GET  http://localhost:5000/admin/users               Manage users
GET  http://localhost:5000/admin/projects            Manage projects
GET  http://localhost:5000/admin/issues              Manage issues

API ENDPOINTS:
GET  http://localhost:5000/api/projects              Get projects (JSON)
GET  http://localhost:5000/api/issues                Get issues (JSON)
```

---

**End of Complete Application Manual**

*This manual covers all files, routes, features, and usage scenarios in the Project Management System.*

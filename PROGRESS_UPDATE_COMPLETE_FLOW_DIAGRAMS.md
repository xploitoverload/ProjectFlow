# Progress Update System - Complete Flow Diagrams & Use Cases

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   PROGRESS UPDATE SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │   EMPLOYEES      │         │   ADMINS         │             │
│  │                  │         │                  │             │
│  │ - Submit Updates │         │ - Review Updates │             │
│  │ - View History   │         │ - Give Feedback  │             │
│  │ - Edit Pending   │         │ - View Dashboard │             │
│  │ - See Feedback   │         │ - Filter Reports │             │
│  └────────┬─────────┘         └────────┬─────────┘             │
│           │                            │                       │
│           └───────────┬────────────────┘                        │
│                       │                                         │
│                ┌──────▼──────┐                                  │
│                │  FORMS &    │                                  │
│                │  VALIDATION │                                  │
│                └──────┬──────┘                                  │
│                       │                                         │
│                ┌──────▼──────────────┐                          │
│                │   DATABASE          │                          │
│                │ (progress_update)   │                          │
│                │   27 Columns        │                          │
│                │   15 Encrypted      │                          │
│                └─────────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 COMPLETE EMPLOYEE SUBMISSION FLOW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EMPLOYEE SUBMISSION FLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

STEP 1: INITIATE
┌─────────────────────────┐
│ Employee clicks         │
│ "Progress Updates"      │
│ in sidebar              │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Navigates to            │
│ /progress/submit        │
└────────────┬────────────┘
             │
             ▼

STEP 2: LOAD FORM
┌─────────────────────────┐
│ Route: @progress_bp     │
│ .route('/submit')       │
│                         │
│ ✅ Check: @login_required
│ ✅ Load: ProgressUpdateForm
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ FORM RENDERS            │
│                         │
│ Template:               │
│ submit_update.html      │
│                         │
│ Shows 13 Sections:      │
│ • Reporting Period      │
│ • Work Completed        │
│ • Blockers              │
│ • Time & Effort         │
│ • Contributions         │
│ • Product Work          │
│ • Status & Risks        │
│ • Next Priorities       │
│ • Additional Info       │
└────────────┬────────────┘
             │
             ▼

STEP 3: FILL FORM
┌─────────────────────────┐
│ Employee selects:       │
│ Period (Daily/Weekly/   │
│  Monthly)               │
│                         │
│ ✅ Dates auto-fill      │
│ (Based on period)       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Employee fills:         │
│                         │
│ REQUIRED FIELDS:        │
│ ✓ Completed Work        │
│ ✓ In Progress           │
│ ✓ Individual Contrib.   │
│ ✓ Project Status        │
│ ✓ Next Priorities       │
│                         │
│ OPTIONAL FIELDS:        │
│ ◯ Blocked Tasks         │
│ ◯ Team Work             │
│ ◯ Features/Bugs         │
│ ◯ Risks/Challenges      │
│ ◯ Notes/Escalations     │
└────────────┬────────────┘
             │
             ▼

STEP 4: SUBMIT
┌─────────────────────────┐
│ Employee clicks         │
│ "Submit Update"         │
└────────────┬────────────┘
             │
             ▼

STEP 5: VALIDATION
┌─────────────────────────┐
│ Form Validation:        │
│                         │
│ ✅ Check all required   │
│ ✅ Check field lengths  │
│ ✅ Check date range     │
│ ✅ Check hour range     │
│    (0-720)              │
│ ✅ CSRF token valid     │
└────────────┬────────────┘
             │
             ├─ FAIL ─────────────────┐
             │                        │
             ▼                        ▼
    ✅ PASS              ❌ ERROR
     │                  Show form with
     │                  error messages
     ▼                  Back to Step 3
     
┌─────────────────────────┐
│ SAVE TO DATABASE        │
│                         │
│ Create: ProgressUpdate  │
│                         │
│ Set:                    │
│ • user_id              │
│ • submitted_at =       │
│   datetime.now()       │
│ • review_status =      │
│   'pending'            │
│                         │
│ 15 Fields:             │
│ • Auto-encrypt         │
│   sensitive data       │
│                         │
│ db.session.commit()    │
└────────────┬────────────┘
             │
             ▼

STEP 6: CONFIRMATION
┌─────────────────────────┐
│ Redirect to:            │
│ /progress/my-updates    │
│                         │
│ Flash message:          │
│ "✓ Update submitted     │
│  successfully!"         │
└────────────┬────────────┘
             │
             ▼

STEP 7: VIEW SUBMISSION
┌─────────────────────────┐
│ Template:               │
│ my_updates.html         │
│                         │
│ Shows:                  │
│ • New update in list    │
│ • Status: PENDING      │
│ • Submitted date       │
│ • Quick actions:       │
│   - View               │
│   - Edit (if pending)  │
└─────────────────────────┘
```

---

## 👥 ADMIN REVIEW FLOW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ADMIN REVIEW FLOW                                  │
└─────────────────────────────────────────────────────────────────────────┘

STEP 1: NAVIGATE
┌─────────────────────────┐
│ Admin clicks            │
│ "Progress Reviews"      │
│ in admin sidebar        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Navigates to            │
│ /progress/admin/pending │
└────────────┬────────────┘
             │
             ▼

STEP 2: VIEW PENDING QUEUE
┌─────────────────────────┐
│ Route:                  │
│ @progress_bp            │
│ .route('/admin/pending')│
│                         │
│ ✅ Check: @admin_required
│ ✅ Query: ProgressUpdate │
│    WHERE status=pending │
│    ORDER BY submitted   │
└────────────┬────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Template: admin_pending.html          │
│                                       │
│ DISPLAYS:                             │
│ ┌─────────────────────────────────┐  │
│ │ Pending Count: 5                │  │
│ │ Oldest Pending: 3 days ago      │  │
│ ├─────────────────────────────────┤  │
│ │ Table of Updates:               │  │
│ │                                 │  │
│ │ User    | Period | Status | Age │  │
│ │---------|--------|--------|-----│  │
│ │ john    | Weekly | 🟡Pend | 2d  │  │
│ │ jane    | Daily  | 🟡Pend | 1d  │  │
│ │ bob     | Month  | 🟡Pend | 5d  │  │
│ │                                 │  │
│ │ [View] [Review] buttons         │  │
│ └─────────────────────────────────┘  │
└────────────┬─────────────────────────┘
             │
             ▼

STEP 3: SELECT UPDATE TO REVIEW
┌─────────────────────────┐
│ Admin clicks            │
│ [Review] button         │
│ on specific update      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Navigates to                        │
│ /progress/admin/review/<update_id>  │
└────────────┬───────────────────────┘
             │
             ▼

STEP 4: VIEW UPDATE DETAILS
┌─────────────────────────────────────┐
│ Route:                              │
│ @progress_bp                        │
│ .route('/admin/review/<id>')        │
│                                     │
│ ✅ Check: @admin_required           │
│ ✅ Load: ProgressUpdate record      │
│ ✅ Load: ReviewProgressUpdateForm   │
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ Template: admin_review.html                            │
│                                                        │
│ LEFT SIDE: UPDATE PREVIEW                             │
│ ┌──────────────────────────────────────────────────┐  │
│ │ john_doe - Weekly (Jan 27 - Feb 2)               │  │
│ │ Status: Pending | Effort: Medium                 │  │
│ ├──────────────────────────────────────────────────┤  │
│ │ Project Status: 🟡 At Risk                       │  │
│ │ Hours Spent: 40 hrs                              │  │
│ │ Has Blockers: ⚠️ YES                             │  │
│ ├──────────────────────────────────────────────────┤  │
│ │ COMPLETED WORK:                                  │  │
│ │ "Fixed authentication bug in..."                 │  │
│ │                                                  │  │
│ │ ⚠️ BLOCKED TASKS ALERT:                          │  │
│ │ "Database migration blocked by..."               │  │
│ │                                                  │  │
│ │ 🚨 ESCALATIONS:                                  │  │
│ │ "Need approval for new server..."                │  │
│ │                                                  │  │
│ │ [View Full Update]                               │  │
│ └──────────────────────────────────────────────────┘  │
│                                                        │
│ RIGHT SIDE: REVIEW FORM (Sticky)                      │
│ ┌──────────────────────────────────────────────────┐  │
│ │ YOUR REVIEW                                      │  │
│ ├──────────────────────────────────────────────────┤  │
│ │ Review Status:                                   │  │
│ │ [Dropdown: pending / approved / needs_revision] │  │
│ ├──────────────────────────────────────────────────┤  │
│ │ Comments:                                        │  │
│ │ ┌──────────────────────────────────────────────┐ │  │
│ │ │ [Text box for feedback]                      │ │  │
│ │ │                                              │ │  │
│ │ └──────────────────────────────────────────────┘ │  │
│ ├──────────────────────────────────────────────────┤  │
│ │ [Submit Review] button                           │  │
│ ├──────────────────────────────────────────────────┤  │
│ │ Quick Templates:                                 │  │
│ │ [👍 Approve] [⚠️ Needs Info]                     │  │
│ └──────────────────────────────────────────────────┘  │
│                                                        │
└────────────┬───────────────────────────────────────────┘
             │
             ▼

STEP 5: ADD FEEDBACK
┌─────────────────────────┐
│ Admin:                  │
│                         │
│ 1. Selects status       │
│    (e.g., "approved")   │
│                         │
│ 2. Types feedback       │
│    (e.g., "Great work   │
│     on the auth fix!")  │
└────────────┬────────────┘
             │
             ▼

STEP 6: SUBMIT REVIEW
┌─────────────────────────┐
│ Admin clicks            │
│ [Submit Review]         │
└────────────┬────────────┘
             │
             ▼

STEP 7: SAVE REVIEW
┌──────────────────────────┐
│ Update ProgressUpdate:    │
│                          │
│ Set:                     │
│ • review_status =        │
│   'approved'             │
│ • admin_comments =       │
│   "Great work..."        │
│   (encrypted)            │
│ • reviewed_at =          │
│   datetime.now()         │
│ • reviewed_by_id =       │
│   current_user.id        │
│                          │
│ db.session.commit()      │
└────────────┬─────────────┘
             │
             ▼

STEP 8: CONFIRMATION
┌─────────────────────────┐
│ Redirect to:            │
│ /progress/admin/pending │
│                         │
│ Flash message:          │
│ "✓ Review submitted!"   │
│                         │
│ Update no longer in     │
│ pending queue           │
└─────────────────────────┘
```

---

## 🔍 DATA FLOW DIAGRAMS

### Data Flow 1: Form Data to Database

```
┌──────────────────────────────────────────────────────────┐
│             FORM SUBMISSION TO DATABASE                   │
└──────────────────────────────────────────────────────────┘

Frontend (HTML Form)
    │
    ├─ Form Fields (25)
    │  ├─ reporting_period: "weekly"
    │  ├─ period_start_date: "2026-01-27"
    │  ├─ period_end_date: "2026-02-02"
    │  ├─ completed_work: "Fixed auth bug..."
    │  ├─ work_in_progress: "Database migration"
    │  ├─ blocked_tasks: "API redesign"
    │  ├─ blocked_reasons: "Waiting for spec..."
    │  ├─ hours_spent: 40
    │  ├─ effort_level: "medium"
    │  ├─ [... 16 more fields ...]
    │  └─ All validated by WTForms
    │
    ▼
Form Validation (ProgressUpdateForm)
    │
    ├─ Check: Required fields present
    ├─ Check: Text length (min/max)
    ├─ Check: Date range valid
    ├─ Check: Hours 0-720
    ├─ Check: Effort level valid
    ├─ Check: CSRF token valid
    │
    ├─ ALL PASS ──────────────────┐
    │                             │
    ▼                             ▼
Create Object              Show Errors
    │                      Reload Form
    │
    ▼
Create ProgressUpdate()
    │
    ├─ user_id = current_user.id
    ├─ submitted_at = datetime.now()
    ├─ review_status = 'pending'
    ├─ Plain fields:
    │  ├─ reporting_period
    │  ├─ period_start_date
    │  ├─ period_end_date
    │  ├─ hours_spent
    │  ├─ effort_level
    │  └─ project_status
    │
    ├─ Encrypted fields:
    │  ├─ completed_work ──┐
    │  ├─ work_in_progress │
    │  ├─ blocked_tasks    │
    │  ├─ blocked_reasons  │
    │  ├─ individual_...   ├──► Fernet Encryption
    │  ├─ team_work        │
    │  ├─ features_worked  │
    │  ├─ bugs_fixed       │
    │  ├─ improvements     │
    │  ├─ risks_...        │
    │  ├─ challenges       │
    │  ├─ next_priorities  │
    │  ├─ notes            │
    │  └─ escalations      │
    │                      │
    │                      ▼
    │              Encrypted Bytes
    │              (Stored in DB)
    │
    ▼
Database Insert
    │
    ├─ INSERT INTO progress_update (
    │      user_id,
    │      reporting_period,
    │      period_start_date,
    │      period_end_date,
    │      completed_work_encrypted,
    │      work_in_progress_encrypted,
    │      [... 15 encrypted fields ...]
    │      blocked_reasons_encrypted,
    │      hours_spent,
    │      effort_level,
    │      project_status,
    │      submitted_at,
    │      review_status
    │  )
    │  VALUES (...)
    │
    ▼
✅ Record Saved
    │
    ▼
Redirect to
/progress/my-updates
```

### Data Flow 2: Database to Display

```
┌──────────────────────────────────────────────────────────┐
│           RETRIEVING & DISPLAYING DATA                    │
└──────────────────────────────────────────────────────────┘

GET /progress/view/<id>
    │
    ▼
Query Database
    │
    ├─ SELECT * FROM progress_update
    │  WHERE id = <id>
    │
    ▼
ProgressUpdate Model Instance Created
    │
    ├─ Encryption Properties
    │  │
    │  ├─ @property completed_work
    │  │  └─ Decrypts on access
    │  │
    │  ├─ @property work_in_progress
    │  │  └─ Decrypts on access
    │  │
    │  ├─ [... 13 more encrypted fields ...]
    │  │
    │  └─ Plain fields returned as-is
    │     ├─ reporting_period
    │     ├─ hours_spent
    │     ├─ project_status
    │     └─ etc.
    │
    ▼
Render Template
    │
    └─ view_update.html
       │
       ├─ Display Metadata
       │  ├─ User: {{ update.user.username }}
       │  ├─ Status: {{ update.review_status }}
       │  ├─ Submitted: {{ update.submitted_at }}
       │  └─ Reviewed: {{ update.reviewed_at }}
       │
       ├─ Display Decrypted Content
       │  ├─ Completed: {{ update.completed_work }}
       │  │             (Auto-decrypted)
       │  ├─ In Progress: {{ update.work_in_progress }}
       │  │               (Auto-decrypted)
       │  └─ [... 13 more encrypted fields ...]
       │
       ├─ Display Feedback (if reviewed)
       │  └─ {{ update.admin_comments }}
       │     (Auto-decrypted)
       │
       └─ Render to HTML
          │
          ▼
        Browser Display
```

---

## 🎨 TEMPLATE USAGE & DATA FLOW

### Template 1: submit_update.html

```
┌───────────────────────────────────────────────────┐
│          SUBMIT UPDATE TEMPLATE                   │
└───────────────────────────────────────────────────┘

PURPOSE: Allow employees to submit progress updates

DATA FROM BACKEND:
    │
    ├─ form: ProgressUpdateForm object
    │
    ├─ form.reporting_period: Field
    │  └─ Choices: daily, weekly, monthly
    │
    ├─ form.period_start_date: DateField
    │
    ├─ form.period_end_date: DateField
    │
    ├─ form.completed_work: TextAreaField (required)
    │  └─ Min 10, Max 5000 chars
    │
    ├─ form.work_in_progress: TextAreaField (required)
    │
    ├─ form.blocked_tasks: TextAreaField (optional)
    │
    ├─ form.blocked_reasons: TextAreaField (optional)
    │
    ├─ form.hours_spent: IntegerField (0-720)
    │
    ├─ form.effort_level: SelectField
    │  └─ Choices: low, medium, high
    │
    ├─ form.individual_contributions: TextAreaField (required)
    │
    ├─ form.team_work: TextAreaField (optional)
    │
    ├─ form.features_worked: TextAreaField (optional)
    │
    ├─ form.bugs_fixed: TextAreaField (optional)
    │
    ├─ form.improvements: TextAreaField (optional)
    │
    ├─ form.project_status: SelectField (required)
    │  └─ Choices: on_track, at_risk, delayed
    │
    ├─ form.risks_dependencies: TextAreaField (optional)
    │
    ├─ form.challenges: TextAreaField (optional)
    │
    ├─ form.next_priorities: TextAreaField (required)
    │
    ├─ form.notes: TextAreaField (optional)
    │
    ├─ form.escalations: TextAreaField (optional)
    │
    └─ form.submit: SubmitField

TEMPLATE STRUCTURE:
    │
    ├─ extends base.html
    │
    ├─ block title
    │  └─ "Submit Progress Update"
    │
    ├─ block content
    │  │
    │  ├─ Header
    │  │  └─ "Submit Progress Update"
    │  │
    │  ├─ Form (13 Sections)
    │  │  │
    │  │  ├─ Section 1: Reporting Period
    │  │  │  ├─ form.reporting_period
    │  │  │  ├─ form.period_start_date
    │  │  │  └─ form.period_end_date
    │  │  │     (Script: Auto-fill dates based on period)
    │  │  │
    │  │  ├─ Section 2: Work Completed
    │  │  │  └─ form.completed_work
    │  │  │
    │  │  ├─ Section 3: Current Work & Blockers
    │  │  │  ├─ form.work_in_progress
    │  │  │  ├─ form.blocked_tasks
    │  │  │  └─ form.blocked_reasons
    │  │  │
    │  │  ├─ Section 4: Time & Effort
    │  │  │  ├─ form.hours_spent
    │  │  │  └─ form.effort_level
    │  │  │
    │  │  ├─ Section 5: Contributions & Impact
    │  │  │  ├─ form.individual_contributions
    │  │  │  └─ form.team_work
    │  │  │
    │  │  ├─ Section 6: Product Work
    │  │  │  ├─ form.features_worked
    │  │  │  ├─ form.bugs_fixed
    │  │  │  └─ form.improvements
    │  │  │
    │  │  ├─ Section 7: Status & Risks
    │  │  │  ├─ form.project_status
    │  │  │  ├─ form.risks_dependencies
    │  │  │  └─ form.challenges
    │  │  │
    │  │  ├─ Section 8: Next Period Planning
    │  │  │  └─ form.next_priorities
    │  │  │
    │  │  └─ Section 9: Additional Info
    │  │     ├─ form.notes
    │  │     └─ form.escalations
    │  │
    │  ├─ Form Styling
    │  │  ├─ Bootstrap 5 classes
    │  │  ├─ Section headers with icons
    │  │  ├─ Field descriptions
    │  │  ├─ Validation feedback
    │  │  └─ Submit button
    │  │
    │  └─ JavaScript
    │     └─ Date auto-fill logic
    │        └─ On period_select change:
    │           ├─ Get selected period
    │           ├─ Calculate date range
    │           └─ Auto-fill date fields
    │
    └─ end block

USER FLOW:
    1. Page loads
    2. Form renders with empty fields
    3. User selects period
    4. Dates auto-fill (via JavaScript)
    5. User fills all 13 sections
    6. Form validation on submit
    7. If valid: Save to database
    8. Redirect to my-updates
```

### Template 2: view_update.html

```
┌───────────────────────────────────────────────────┐
│         VIEW UPDATE TEMPLATE                      │
└───────────────────────────────────────────────────┘

PURPOSE: Display submitted update in read-only format

DATA FROM BACKEND:
    │
    ├─ update: ProgressUpdate object (queried from DB)
    │
    ├─ update.user.username
    ├─ update.user.email
    ├─ update.reporting_period
    ├─ update.period_start_date
    ├─ update.period_end_date
    ├─ update.completed_work (decrypted)
    ├─ update.work_in_progress (decrypted)
    ├─ update.blocked_tasks (decrypted)
    ├─ update.blocked_reasons (decrypted)
    ├─ update.hours_spent
    ├─ update.effort_level
    ├─ update.individual_contributions (decrypted)
    ├─ update.team_work (decrypted)
    ├─ update.features_worked (decrypted)
    ├─ update.bugs_fixed (decrypted)
    ├─ update.improvements (decrypted)
    ├─ update.project_status
    ├─ update.risks_dependencies (decrypted)
    ├─ update.challenges (decrypted)
    ├─ update.next_priorities (decrypted)
    ├─ update.notes (decrypted)
    ├─ update.escalations (decrypted)
    ├─ update.submitted_at
    ├─ update.reviewed_at
    ├─ update.review_status
    ├─ update.reviewed_by.username (if reviewed)
    └─ update.admin_comments (decrypted, if reviewed)

TEMPLATE STRUCTURE:
    │
    ├─ extends base.html
    │
    ├─ Header
    │  └─ Update title & period
    │
    ├─ Status Cards (Row 1)
    │  ├─ Submission card
    │  │  ├─ Submitted date
    │  │  └─ Submitter info
    │  ├─ Review card
    │  │  ├─ Review status badge
    │  │  │  └─ Color-coded (pending/approved/revision)
    │  │  ├─ Reviewed date
    │  │  └─ Reviewer name
    │  └─ Action cards
    │     ├─ Edit button (if pending)
    │     └─ Review button (if admin & pending)
    │
    ├─ Quick Stats (Row 2)
    │  ├─ Project Status
    │  │  └─ Color badge (green/yellow/red)
    │  ├─ Hours Spent
    │  ├─ Effort Level
    │  │  └─ Badge (Low/Medium/High)
    │  └─ Blockers Indicator
    │     └─ If has blockers: 🟡 BLOCKED
    │
    ├─ Content Sections (11 sections)
    │  ├─ Completed Work
    │  │  └─ {{ update.completed_work }}
    │  ├─ In Progress
    │  │  └─ {{ update.work_in_progress }}
    │  ├─ Blocked Tasks (conditional)
    │  │  └─ Alert box with {{ update.blocked_tasks }}
    │  ├─ Block Reasons (conditional)
    │  │  └─ {{ update.blocked_reasons }}
    │  ├─ Individual Contributions
    │  │  └─ {{ update.individual_contributions }}
    │  ├─ Team Work
    │  │  └─ {{ update.team_work }}
    │  ├─ Features Worked
    │  │  └─ {{ update.features_worked }}
    │  ├─ Bugs Fixed
    │  │  └─ {{ update.bugs_fixed }}
    │  ├─ Improvements
    │  │  └─ {{ update.improvements }}
    │  ├─ Risks & Dependencies
    │  │  └─ {{ update.risks_dependencies }}
    │  └─ Challenges
    │     └─ {{ update.challenges }}
    │
    ├─ Planning Section
    │  ├─ Next Priorities
    │  │  └─ {{ update.next_priorities }}
    │  └─ Notes
    │     └─ {{ update.notes }}
    │
    ├─ Escalations (conditional)
    │  └─ Alert box with {{ update.escalations }}
    │
    ├─ Admin Feedback (conditional)
    │  └─ If update.admin_comments:
    │     ├─ Reviewer info
    │     ├─ Review status
    │     └─ Comments
    │        └─ {{ update.admin_comments }}
    │
    └─ Footer
       ├─ Back button
       └─ Edit button (if applicable)

DISPLAY LOGIC:
    │
    ├─ Status Badge Logic
    │  ├─ if update.review_status == 'pending'
    │  │  └─ 🟡 Yellow badge
    │  ├─ elif update.review_status == 'approved'
    │  │  └─ 🟢 Green badge
    │  └─ else
    │     └─ 🔵 Blue badge
    │
    ├─ Conditional Sections
    │  ├─ Show blockers only if blocked_tasks exists
    │  ├─ Show escalations only if escalations exists
    │  ├─ Show feedback only if reviewed
    │  └─ Show edit button only if user owns & pending
    │
    └─ Color Coding
       ├─ Project Status
       │  ├─ on_track → 🟢 Green
       │  ├─ at_risk → 🟡 Yellow
       │  └─ delayed → 🔴 Red
       └─ Effort Level
          ├─ low → Gray
          ├─ medium → Blue
          └─ high → Green

USER FLOW:
    1. Employee/Admin navigates to update
    2. Template queries and decrypts data
    3. Displays update in read-only format
    4. Shows status and metadata
    5. Displays all 13 sections
    6. Shows feedback if available
    7. Shows action buttons (Edit/Review/Back)
```

### Template 3: admin_pending.html

```
┌───────────────────────────────────────────────────┐
│      ADMIN PENDING QUEUE TEMPLATE                 │
└───────────────────────────────────────────────────┘

PURPOSE: Show admin list of pending updates to review

DATA FROM BACKEND:
    │
    ├─ updates: Paginated query results
    │  └─ WHERE review_status = 'pending'
    │  └─ ORDER BY submitted_at DESC
    │  └─ LIMIT 15 per page
    │
    ├─ For each update:
    │  ├─ update.id
    │  ├─ update.user.username
    │  ├─ update.user.email
    │  ├─ update.user.role
    │  ├─ update.reporting_period
    │  ├─ update.period_start_date
    │  ├─ update.period_end_date
    │  ├─ update.project_status
    │  ├─ update.blocked_tasks
    │  ├─ update.escalations
    │  ├─ update.completed_work (first 200 chars)
    │  ├─ update.submitted_at
    │  └─ Days pending calculation
    │
    └─ now: Current datetime for age calculation

TEMPLATE STRUCTURE:
    │
    ├─ extends base.html
    │
    ├─ Header
    │  ├─ Title: "Pending Reviews"
    │  ├─ Pending count card
    │  │  └─ "5 pending reviews"
    │  ├─ Oldest pending card
    │  │  └─ "Oldest: 5 days ago"
    │  └─ Action buttons
    │     ├─ [Dashboard] → /progress/admin/stats
    │     └─ [All Updates] → /progress/admin/all
    │
    ├─ Pending Updates Table
    │  │
    │  ├─ Table Headers
    │  │  ├─ User (with avatar)
    │  │  ├─ Period
    │  │  ├─ Project Status
    │  │  ├─ Hours Spent
    │  │  ├─ Has Blockers
    │  │  ├─ Submitted
    │  │  └─ Actions
    │  │
    │  ├─ Table Rows (for each update)
    │  │  │
    │  │  ├─ User Column
    │  │  │  ├─ Avatar (colored circle with initials)
    │  │  │  ├─ Username
    │  │  │  └─ Email
    │  │  │
    │  │  ├─ Period Column
    │  │  │  ├─ reporting_period (Daily/Weekly/Monthly)
    │  │  │  └─ Date range
    │  │  │
    │  │  ├─ Project Status Column
    │  │  │  └─ Color-coded badge
    │  │  │     ├─ 🟢 on_track
    │  │  │     ├─ 🟡 at_risk
    │  │  │     └─ 🔴 delayed
    │  │  │
    │  │  ├─ Hours Column
    │  │  │  └─ hours_spent value
    │  │  │
    │  │  ├─ Blockers Column
    │  │  │  ├─ If blocked_tasks exists
    │  │  │  │  └─ 🟡 YES (red badge)
    │  │  │  └─ Else
    │  │  │     └─ ✅ NO (green badge)
    │  │  │
    │  │  ├─ Submitted Column
    │  │  │  ├─ submitted_at date
    │  │  │  └─ Days ago badge
    │  │  │
    │  │  └─ Actions Column
    │  │     ├─ [View] button
    │  │     │  └─ → /progress/view/<id>
    │  │     └─ [Review] button
    │  │        └─ → /progress/admin/review/<id>
    │  │
    │  ├─ Row Alerts (conditional)
    │  │  ├─ If blocked_tasks: Show alert icon
    │  │  └─ If escalations: Show escalation icon
    │  │
    │  └─ Empty State
    │     └─ If no pending updates:
    │        └─ "No pending updates!"
    │           "All reviews completed"
    │
    ├─ Pagination (if multiple pages)
    │  ├─ Previous button
    │  ├─ Page numbers
    │  └─ Next button
    │
    └─ Footer
       └─ Update count summary

LOGIC & CALCULATIONS:
    │
    ├─ Days Pending Calculation
    │  └─ (now - update.submitted_at).days
    │
    ├─ Badge Colors
    │  ├─ Days pending < 1 → 🟢 Green
    │  ├─ Days pending 1-3 → 🟡 Yellow
    │  └─ Days pending > 3 → 🔴 Red
    │
    ├─ Avatar Generation
    │  ├─ Initials from username
    │  ├─ Random background color
    │  └─ White text
    │
    └─ Quick Previews
       ├─ Show completed_work[:200]
       ├─ Show blocked_tasks preview
       └─ Show escalations preview

USER FLOW:
    1. Admin clicks "Progress Reviews"
    2. Page loads pending queue
    3. Shows count and age metrics
    4. Lists all pending updates
    5. Admin can:
       - Click [View] for full details
       - Click [Review] to review & feedback
       - Sort by clicking column headers
       - Navigate pages
    6. No pending left? Shows empty state
```

---

## 🎯 USE CASES BY ROLE

### Employee Use Cases

```
┌─────────────────────────────────────────────────────────┐
│          EMPLOYEE USE CASES                             │
└─────────────────────────────────────────────────────────┘

USE CASE 1: Submit Weekly Progress Update
├─ Actor: John Doe (Employee)
├─ Goal: Document weekly accomplishments
├─ Trigger: End of week
├─ Flow:
│  1. Click "Progress Updates" in sidebar
│  2. Click "Submit New Update"
│  3. Select period: Weekly
│  4. Dates auto-fill (Mon-Sun)
│  5. Fill completed work (fixed bugs, deployed features)
│  6. Fill in-progress (new API endpoint)
│  7. Note blockers (waiting for design spec)
│  8. Log hours: 38 hrs
│  9. Set effort: Medium
│  10. Add individual contributions
│  11. Set project status: On Track
│  12. Add next week priorities
│  13. Click Submit
│  14. Receives confirmation & redirected
│  15. Can see update in My Updates list
└─ Result: Update submitted & pending review

USE CASE 2: Receive Admin Feedback
├─ Actor: John Doe (Employee)
├─ Goal: Read feedback from admin
├─ Trigger: Admin completes review
├─ Flow:
│  1. Goes to "My Updates"
│  2. Sees update status changed to "approved" (green)
│  3. Clicks "View" to see details
│  4. Reads admin comments section
│  5. Sees feedback: "Great work on the bug fixes!"
│  6. Can view original update content
└─ Result: Employee informed of approval & feedback

USE CASE 3: Resubmit After Revision Request
├─ Actor: John Doe (Employee)
├─ Goal: Fix update per admin request
├─ Trigger: Review status is "needs_revision"
├─ Flow:
│  1. Goes to "My Updates"
│  2. Sees update with blue "Needs Revision" badge
│  3. Reads admin feedback: "Please add more detail..."
│  4. Clicks "Edit" button
│  5. Form pre-fills with original data
│  6. Adds more details to sections
│  7. Clicks "Update"
│  8. Status goes back to "pending"
│  9. Redirected to My Updates
└─ Result: Updated submission sent to admin for re-review

USE CASE 4: Track Personal Progress History
├─ Actor: John Doe (Employee)
├─ Goal: Review past submissions
├─ Trigger: Want to check previous updates
├─ Flow:
│  1. Click "Progress Updates"
│  2. Click "My Updates"
│  3. See table with all submissions
│  4. Shows: Period | Status | Hours | Submitted
│  5. Can sort by clicking headers
│  6. Can navigate pages if many updates
│  7. Click "View" on any to see details
│  8. Statistics cards show:
│     ├─ Total: 12 updates
│     ├─ Pending: 1 update
│     ├─ Approved: 10 updates
│     └─ Revision: 1 update
└─ Result: Employee can review submission history
```

### Admin Use Cases

```
┌─────────────────────────────────────────────────────────┐
│          ADMIN USE CASES                                │
└─────────────────────────────────────────────────────────┘

USE CASE 1: Review Pending Update
├─ Actor: Manager (Admin)
├─ Goal: Review and approve employee progress
├─ Trigger: End of day review time
├─ Flow:
│  1. Click "Progress Reviews" in admin menu
│  2. See pending queue (5 updates waiting)
│  3. Click [Review] on john_doe's update
│  4. Read update preview on left:
│     ├─ What was completed
│     ├─ Current work
│     ├─ Any blockers with reasons
│     ├─ Hours and effort
│     └─ Project status
│  5. On right, add feedback in comment box
│  6. Select review status: "approved"
│  7. Click "Submit Review"
│  8. Confirmation message & back to queue
│  9. Update no longer in pending
└─ Result: Employee receives approval & feedback

USE CASE 2: Request More Details
├─ Actor: Manager (Admin)
├─ Goal: Get clarification on update
├─ Trigger: Update missing important info
├─ Flow:
│  1. Go to pending queue
│  2. Click [Review] on update
│  3. Read: Very brief completed work section
│  4. Type comment: "Please provide more detail on..."
│  5. Select status: "needs_revision"
│  6. Click "Submit Review"
│  7. Employee gets notified & can edit
│  8. Employee resubmits with more info
│  9. Employee update goes back to pending
│  10. Manager reviews again
└─ Result: Better quality, detailed updates

USE CASE 3: Identify At-Risk Projects
├─ Actor: Manager (Admin)
├─ Goal: Find projects with status issues
├─ Trigger: Weekly status review
├─ Flow:
│  1. Go to /progress/admin/all
│  2. Use filter: Project Status = "at_risk"
│  3. See all employees reporting at-risk projects
│  4. Click [View] on each to see details
│  5. Read blockers and challenges
│  6. Note risks and dependencies
│  7. Identify common blockers across team
│  8. Plan mitigation steps
└─ Result: Manager aware of project risks

USE CASE 4: Analyze Team Productivity
├─ Actor: Manager (Admin)
├─ Goal: Understand team effort distribution
├─ Trigger: Monthly review meeting
├─ Flow:
│  1. Go to /progress/admin/stats dashboard
│  2. See key metrics:
│     ├─ Total updates: 48
│     ├─ Approved: 45
│     ├─ Pending: 2
│     ├─ Needs revision: 1
│  3. See effort breakdown:
│     ├─ Low effort: 12 (25%)
│     ├─ Medium effort: 24 (50%)
│     ├─ High effort: 12 (25%)
│  4. See project status breakdown:
│     ├─ On track: 40 (83%)
│     ├─ At risk: 8 (17%)
│     ├─ Delayed: 0 (0%)
│  5. See top submitters (consistency)
│  6. See average hours per person
│  7. Review recent submissions
├─ Analysis:
│  ├─ Team mostly on track ✓
│  ├─ Balanced effort distribution ✓
│  ├─ Some at-risk items to address ✓
└─ Result: Data-driven insights for team performance

USE CASE 5: Filter & Search Updates
├─ Actor: Manager (Admin)
├─ Goal: Find specific employee's updates
├─ Trigger: Need to review one person's progress
├─ Flow:
│  1. Go to /progress/admin/all
│  2. Filter by User: Select "john_doe"
│  3. See only john_doe's 6 updates
│  4. Further filter by Period: "weekly"
│  5. See 4 weekly updates
│  6. Further filter by Status: "approved"
│  7. See john_doe's 3 approved weekly updates
│  8. Click [View] on any to see full details
│  9. Can assess employee's consistency
└─ Result: Focused view of specific employee
```

---

## 🔄 COMPONENT INTERACTION DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│         HOW COMPONENTS WORK TOGETHER                            │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   BROWSER/UI    │
                    │  (Templates)    │
                    └────────┬────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
          ┌────────▼────────┐  ┌──────▼──────────┐
          │  HTML Forms     │  │ Display Data    │
          │                 │  │                 │
          │ • submit_update │  │ • view_update   │
          │ • admin_review  │  │ • my_updates    │
          │ • admin_all     │  │ • admin_pending │
          └────────┬────────┘  │ • admin_stats   │
                   │           └──────┬──────────┘
                   │                  │
                   │  Form Data       │  Query Data
                   │  & User Action   │  to Display
                   │                  │
                   └──────────┬───────┘
                              │
                    ┌─────────▼──────────┐
                    │  FLASK ROUTES      │
                    │  (app/routes/      │
                    │   progress.py)     │
                    │                    │
                    │ @progress_bp       │
                    │ .route('/submit')  │
                    │ .route('/pending') │
                    │ .route('/review')  │
                    │ .route('/stats')   │
                    └─────────┬──────────┘
                              │
                   ┌──────────┴──────────┐
                   │                     │
         ┌─────────▼────────┐   ┌────────▼────────┐
         │ FORMS            │   │ AUTHORIZATION   │
         │ (app/forms.py)   │   │ (@admin_required)
         │                  │   │ (@login_required)
         │ Validation:      │   │                 │
         │ • Required       │   │ Role Checks:    │
         │ • Length         │   │ • Is logged in? │
         │ • Range          │   │ • Is admin?     │
         │ • Date range     │   │ • Owns record?  │
         │ • CSRF token     │   └────────┬────────┘
         └─────────┬────────┘            │
                   │                     │
                   │    Valid Data       │    Access OK
                   │    & Authorization │
                   │                     │
                   └──────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │ MODELS             │
                    │ (models.py)        │
                    │                    │
                    │ ProgressUpdate:    │
                    │ • 27 columns       │
                    │ • 15 encrypted     │
                    │ • Relationships    │
                    │ • Timestamps       │
                    │ • Encryption props │
                    └─────────┬──────────┘
                              │
                   ┌──────────┴──────────┐
                   │                     │
         ┌─────────▼────────┐   ┌────────▼────────┐
         │ ENCRYPTION       │   │ DATABASE QUERY  │
         │                  │   │                 │
         │ @property        │   │ SELECT          │
         │ completed_work:  │   │ INSERT          │
         │ • Get encrypted  │   │ UPDATE          │
         │   bytes from DB  │   │ DELETE          │
         │ • Decrypt with   │   │                 │
         │   Fernet key     │   │ SQLite          │
         │ • Return plain   │   │ progress_update │
         │   text           │   │ table           │
         └────────┬─────────┘   └────────┬────────┘
                  │                      │
                  │   Encrypted Data     │
                  │   In Database        │
                  │                      │
                  └──────────┬───────────┘
                             │
                    ┌────────▼────────┐
                    │ SQLITE DATABASE │
                    │                 │
                    │ progress_update:│
                    │ • 27 columns    │
                    │ • Indexes       │
                    │ • Foreign keys  │
                    │ • Encrypted     │
                    │   blobs         │
                    └─────────────────┘

EXAMPLE DATA FLOW:

Employee Submits Update
    │
    ▼
POST /progress/submit (Form data)
    │
    ▼
ProgressUpdateForm validates
    │
    ├─ All required? ✓
    ├─ Valid ranges? ✓
    ├─ CSRF valid? ✓
    │
    ▼
Create ProgressUpdate object
    │
    ├─ Set user_id = employee
    ├─ Set completed_work = (Fernet encrypts)
    ├─ Set work_in_progress = (Fernet encrypts)
    ├─ [... 13 more fields encrypted ...]
    ├─ Set review_status = pending
    ├─ Set submitted_at = now()
    │
    ▼
INSERT INTO progress_update (...)
    │
    ▼
Database stores encrypted blobs
    │
    ▼
Redirect to /progress/my-updates
    │
    ▼
GET /progress/my-updates
    │
    ▼
Query: SELECT * FROM progress_update WHERE user_id=?
    │
    ▼
Load ProgressUpdate object(s)
    │
    ├─ Access @property completed_work
    ├─ Model decrypts automatically
    ├─ Return plain text
    │
    ▼
Render my_updates.html
    │
    ├─ Show new update in list
    ├─ Status: 🟡 Pending
    ├─ Submitted: Today
    ├─ Action: [View] [Edit]
    │
    ▼
Display in browser
```

---

## 📱 RESPONSIVE DESIGN & UI FLOW

```
┌────────────────────────────────────────────────────────┐
│     HOW UI RESPONDS TO DATA CHANGES                     │
└────────────────────────────────────────────────────────┘

SCENARIO: Period Selection Changes Dates

BEFORE:
┌─────────────────────────┐
│ Period: [Select]        │ ← Default
│ Start:  [  /  /    ]    │ ← Empty
│ End:    [  /  /    ]    │ ← Empty
└─────────────────────────┘

USER SELECTS: "Weekly"
    │
    ▼
JavaScript Event: onChange
    │
    ├─ Get selected value: "weekly"
    ├─ Calculate dates:
    │  ├─ Today = Feb 3, 2026 (Monday)
    │  └─ Last week = Jan 27 - Feb 2
    ├─ Set form fields:
    │  ├─ start_date.value = "2026-01-27"
    │  └─ end_date.value = "2026-02-02"
    │
    ▼
AFTER:
┌─────────────────────────┐
│ Period: [Weekly ✓]      │
│ Start:  [01/27/2026]    │ ← Auto-filled
│ End:    [02/02/2026]    │ ← Auto-filled
└─────────────────────────┘

---

SCENARIO: Form Validation Error

USER SUBMITS EMPTY FORM
    │
    ▼
Form.validate_on_submit() = False
    │
    ├─ completed_work: "This field is required"
    ├─ individual_contributions: "This field is required"
    ├─ project_status: "This field is required"
    └─ next_priorities: "This field is required"
    │
    ▼
Form RE-RENDERS with errors
    │
    ├─ Red border on required fields
    ├─ Error messages below each
    ├─ Scroll to first error
    │
    ▼
USER SEES:
┌───────────────────────────────────┐
│ ❌ Completed Work                 │
│    This field is required.        │
│    [Text box] ← Red border        │
├───────────────────────────────────┤
│ ❌ Individual Contributions        │
│    This field is required.        │
│    [Text box] ← Red border        │
├───────────────────────────────────┤
│ ❌ Project Status                 │
│    This field is required.        │
│    [Dropdown] ← Red border        │
└───────────────────────────────────┘

---

SCENARIO: Admin Reviews Update

Database state before review:
├─ review_status = 'pending'
├─ reviewed_at = NULL
├─ reviewed_by_id = NULL
├─ admin_comments = NULL

Admin submits review (approved):
    │
    ▼
POST /progress/admin/review/<id>
    │
    ├─ review_status = 'approved'
    ├─ admin_comments = "Great work!" (encrypted)
    ├─ reviewed_at = datetime.now()
    ├─ reviewed_by_id = admin_user_id
    │
    ▼
Database update:
├─ review_status = 'approved' ✓
├─ reviewed_at = '2026-02-03 14:30:00' ✓
├─ reviewed_by_id = 1 ✓
├─ admin_comments = [encrypted blob] ✓

When employee views update:
    │
    ▼
view_update.html displays:
    │
    ├─ Status Badge: 🟢 APPROVED (green)
    ├─ Review Card:
    │  ├─ "Reviewed by: Admin"
    │  ├─ "Reviewed on: Feb 3, 2:30 PM"
    │  └─ Comments: "Great work!"
    │         (decrypted from blob)
    │
    ├─ Action Buttons:
    │  ├─ [Edit] ← HIDDEN (not pending)
    │  └─ [Back]
    │
    └─ Styling:
       ├─ Whole update highlighted green
       ├─ Checkmark icon
       └─ Success styling
```

---

## 🎓 SUMMARY: WHAT EACH PIECE DOES

```
┌────────────────────────────────────────────────────────┐
│    COMPLETE COMPONENT REFERENCE                        │
└────────────────────────────────────────────────────────┘

1. ROUTES (app/routes/progress.py)
   │
   ├─ /progress/submit (GET/POST)
   │  └─ Purpose: Show form & process submission
   │     └─ Returns: submit_update.html template
   │
   ├─ /progress/my-updates (GET)
   │  └─ Purpose: List user's own updates
   │     └─ Returns: my_updates.html template
   │
   ├─ /progress/view/<id> (GET)
   │  └─ Purpose: Show specific update details
   │     └─ Returns: view_update.html template
   │
   ├─ /progress/edit/<id> (GET/POST)
   │  └─ Purpose: Edit pending update
   │     └─ Returns: submit_update.html with pre-filled data
   │
   ├─ /progress/admin/pending (GET)
   │  └─ Purpose: Show pending reviews queue
   │     └─ Returns: admin_pending.html template
   │
   ├─ /progress/admin/all (GET)
   │  └─ Purpose: Show all updates with filters
   │     └─ Returns: admin_all.html template
   │
   ├─ /progress/admin/review/<id> (GET/POST)
   │  └─ Purpose: Review update & save feedback
   │     └─ Returns: admin_review.html template
   │
   └─ /progress/admin/stats (GET)
      └─ Purpose: Show dashboard & statistics
         └─ Returns: admin_stats.html template

2. FORMS (app/forms.py)
   │
   ├─ ProgressUpdateForm (25 fields)
   │  └─ Purpose: Validate employee submission
   │     └─ Fields: reporting_period, dates, work, hours, etc
   │
   └─ ReviewProgressUpdateForm (2 fields)
      └─ Purpose: Validate admin review
         └─ Fields: review_status, admin_comments

3. TEMPLATES (app/templates/progress/)
   │
   ├─ submit_update.html (445 lines)
   │  └─ Purpose: Form for submitting updates
   │     └─ Uses: 13 sections with Bootstrap 5 styling
   │
   ├─ view_update.html (265 lines)
   │  └─ Purpose: Display update details
   │     └─ Uses: Status cards, content sections, feedback
   │
   ├─ my_updates.html (142 lines)
   │  └─ Purpose: List user's updates
   │     └─ Uses: Table with pagination, stats cards
   │
   ├─ admin_pending.html (158 lines)
   │  └─ Purpose: Pending reviews queue
   │     └─ Uses: Urgency indicators, quick previews
   │
   ├─ admin_all.html (290+ lines)
   │  └─ Purpose: All updates with filters
   │     └─ Uses: Filter dropdowns, advanced table
   │
   ├─ admin_review.html (290+ lines)
   │  └─ Purpose: Review interface with feedback
   │     └─ Uses: Split layout (preview + form)
   │
   └─ admin_stats.html (400+ lines)
      └─ Purpose: Statistics dashboard
         └─ Uses: Cards, progress bars, charts, lists

4. DATABASE MODEL (models.py)
   │
   └─ ProgressUpdate (27 columns)
      │
      ├─ Primary Data
      │  ├─ id, user_id, reviewed_by_id
      │  ├─ submitted_at, reviewed_at
      │  └─ review_status
      │
      ├─ Reporting Period
      │  ├─ reporting_period (daily/weekly/monthly)
      │  ├─ period_start_date
      │  └─ period_end_date
      │
      ├─ Work Data (Encrypted)
      │  ├─ completed_work
      │  ├─ work_in_progress
      │  ├─ blocked_tasks
      │  └─ blocked_reasons
      │
      ├─ Time & Effort
      │  ├─ hours_spent (0-720)
      │  └─ effort_level (low/medium/high)
      │
      ├─ Contributions (Encrypted)
      │  ├─ individual_contributions
      │  └─ team_work
      │
      ├─ Product Work (Encrypted)
      │  ├─ features_worked
      │  ├─ bugs_fixed
      │  └─ improvements
      │
      ├─ Status & Risks (Encrypted)
      │  ├─ project_status (on_track/at_risk/delayed)
      │  ├─ risks_dependencies
      │  └─ challenges
      │
      ├─ Planning (Encrypted)
      │  ├─ next_priorities
      │  ├─ notes
      │  └─ escalations
      │
      └─ Review (Encrypted)
         └─ admin_comments

5. ENCRYPTION SYSTEM
   │
   └─ Fernet (Symmetric)
      │
      ├─ Encryption Key: encryption.key file
      ├─ Encrypted Fields: 15 total
      ├─ Transparent: Auto on set, auto decrypt on get
      ├─ Storage: Binary blobs in database
      └─ Security: Industry-standard symmetric encryption

6. AUTHORIZATION SYSTEM
   │
   ├─ @login_required
   │  └─ Checks: Is user logged in?
   │
   ├─ @admin_required
   │  └─ Checks: Is user logged in? Is user admin?
   │
   └─ User Isolation
      └─ Checks: Can only view own updates (except admins)

7. VALIDATION SYSTEM
   │
   ├─ Form Validation
   │  ├─ Required fields: Must have value
   │  ├─ Text length: Min/max character limits
   │  ├─ Date range: End date > start date
   │  ├─ Hour range: 0-720 hours
   │  └─ CSRF token: Must match session
   │
   └─ Database Validation
      ├─ Foreign keys: user_id must exist
      ├─ Enum checks: Status values must be valid
      └─ Timestamp checks: Dates must be valid

8. DISPLAY SYSTEM
   │
   ├─ Color Coding
   │  ├─ Status: Green (approved), Yellow (pending), Blue (revision)
   │  ├─ Project: Green (on track), Yellow (at risk), Red (delayed)
   │  └─ Effort: Gray (low), Blue (medium), Green (high)
   │
   ├─ Icons & Badges
   │  ├─ Status badges: ✓, ⏳, ⚠️, 🔴
   │  ├─ Alert boxes: ⚠️ For blockers/escalations
   │  └─ Metrics: Hours, days, count numbers
   │
   └─ Responsive Design
      ├─ Desktop: Full width, multi-column
      ├─ Tablet: Adjusted layout
      └─ Mobile: Single column, touch-friendly
```

This provides a complete understanding of how everything works together!

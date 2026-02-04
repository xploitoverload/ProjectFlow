# Progress Update System - Template Data Mapping Guide

## 📊 Data Flow from Database to Templates

### Complete Data Journey

```
┌──────────────────────────────────────────────────────────────┐
│         HOW DATA FLOWS INTO TEMPLATES                         │
└──────────────────────────────────────────────────────────────┘

STEP 1: ROUTE GETS DATA
┌─────────────────────────────────────────────────────────────┐
│ @progress_bp.route('/view/<int:update_id>')                 │
│ @login_required                                             │
│ def view_update(update_id):                                 │
│     # Query database                                        │
│     update = ProgressUpdate.query.get_or_404(update_id)    │
│                                                             │
│     # Check authorization                                  │
│     if (update.user_id != current_user.id and             │
│         current_user.role != 'admin'):                     │
│         abort(403)                                         │
│                                                             │
│     # Pass to template                                      │
│     return render_template('progress/view_update.html',    │
│         update=update)  ← DATA PASSED HERE                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
STEP 2: TEMPLATE RECEIVES DATA
┌─────────────────────────────────────────────────────────────┐
│ view_update.html                                            │
│                                                             │
│ {% extends "base.html" %}                                  │
│                                                             │
│ {% block content %}                                         │
│     <!-- update variable available -->                      │
│     <!-- update.user, update.submitted_at, etc -->          │
│     <!-- Encrypted fields auto-decrypt on access -->        │
│ {% endblock %}                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
STEP 3: TEMPLATE ACCESSES DATA
┌─────────────────────────────────────────────────────────────┐
│ {{ update.user.username }}  ← Access user name             │
│ {{ update.submitted_at }}   ← Access timestamp             │
│ {{ update.completed_work }} ← Auto-decrypt & display       │
│ {{ update.hours_spent }}    ← Access number field          │
│ {{ update.project_status }} ← Access enum value            │
│                                                             │
│ {% if update.blocked_tasks %}  ← Check if encrypted       │
│     <!-- Conditional rendering based on data -->            │
│ {% endif %}                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
STEP 4: BROWSER RENDERS HTML
┌─────────────────────────────────────────────────────────────┐
│ <h1>john_doe - Weekly (Jan 27 - Feb 2)</h1>               │
│ <span class="badge bg-warning">Pending</span>              │
│ <p>Fixed authentication bug in login module...</p>         │
│ <span>40 hours</span>                                       │
│ <span class="badge bg-success">On Track</span>             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Template by Template: Data Mapping

### Template 1: submit_update.html

**Purpose**: Show form to employee  
**Source**: Fresh form (not from database)

```
┌──────────────────────────────────────────────────────────┐
│           DATA USED IN submit_update.html                 │
└──────────────────────────────────────────────────────────┘

FROM ROUTE:
    form: ProgressUpdateForm()
    
    Form Fields Access:
    {{ form.reporting_period }}        ← Dropdown (empty on new)
    {{ form.period_start_date }}       ← DateField (empty on new)
    {{ form.period_end_date }}         ← DateField (empty on new)
    {{ form.completed_work }}          ← TextArea (empty)
    {{ form.work_in_progress }}        ← TextArea (empty)
    [... 20 more fields ...]
    {{ form.submit }}                  ← Submit button
    
CONDITIONALLY (if editing):
    update: ProgressUpdate object
    
    Pre-fill Logic:
    {% if update %}
        {{ form.completed_work.data = update.completed_work }}
        {{ form.work_in_progress.data = update.work_in_progress }}
        [... all fields pre-filled ...]
    {% endif %}

TEMPLATE SECTIONS:
    
    Section 1: Header
    ├─ Static: "Submit Progress Update"
    ├─ Dynamic: If editing: Show "Edit Progress Update"
    └─ Form tag: {% for field in form %}
    
    Section 2: Reporting Period
    ├─ form.reporting_period (Dropdown)
    │  Choices: Daily / Weekly / Monthly
    │  Event: onChange → Auto-fill dates (JavaScript)
    ├─ form.period_start_date (DateField)
    │  Auto-filled based on period
    └─ form.period_end_date (DateField)
       Auto-filled based on period
    
    Sections 3-13: Form Fields
    ├─ Each renders: {{ form.<fieldname> }}
    ├─ Each shows: {{ form.<fieldname>.label }}
    ├─ Each shows: Validation errors if present
    ├─ Each shows: Help text (form field.description)
    └─ Each styled with Bootstrap classes
    
    Footer: Buttons
    ├─ {{ form.submit }} (Submit button)
    └─ Cancel link (Back to previous)

JAVASCRIPT LOGIC:
    
    // Auto-fill dates when period changes
    document.getElementById('reporting_period')
        .addEventListener('change', function() {
            
        const period = this.value;  // 'daily', 'weekly', 'monthly'
        const today = new Date();
        let start, end;
        
        if (period === 'daily') {
            start = today;
            end = today;
        } else if (period === 'weekly') {
            // Get last Monday
            start = new Date(today);
            start.setDate(today.getDate() - today.getDay() + 1);
            end = today;
        } else if (period === 'monthly') {
            // Get 1st of this month
            start = new Date(today.getFullYear(), today.getMonth(), 1);
            end = today;
        }
        
        // Set form fields
        document.getElementById('period_start_date')
            .value = formatDate(start);
        document.getElementById('period_end_date')
            .value = formatDate(end);
    });

ERROR HANDLING:
    {% for field in form %}
        {% if field.errors %}
            <div class="invalid-feedback">
                {% for error in field.errors %}
                    {{ error }}
                {% endfor %}
            </div>
        {% endif %}
    {% endfor %}

STYLING:
    Bootstrap 5 Classes:
    ├─ form-group: Container for each field
    ├─ form-label: Label styling
    ├─ form-control: Text input styling
    ├─ form-select: Dropdown styling
    ├─ is-invalid: Red border when error
    ├─ invalid-feedback: Error message styling
    └─ btn btn-primary: Submit button styling
```

**Data Flow for Edit Scenario:**
```
GET /progress/edit/123 (existing update)
    ↓
Route queries: update = ProgressUpdate.query.get(123)
    ↓
Route checks: Is update.user_id == current_user.id?
    ↓
Route creates form: form = ProgressUpdateForm()
    ↓
Route pre-fills: 
    form.completed_work.data = update.completed_work
    form.work_in_progress.data = update.work_in_progress
    [... all 25 fields ...]
    ↓
Render template with pre-filled form
    ↓
POST /progress/edit/123 with modified data
    ↓
Validate & update database
```

---

### Template 2: view_update.html

**Purpose**: Display update details (read-only)  
**Source**: Database query

```
┌──────────────────────────────────────────────────────────┐
│           DATA USED IN view_update.html                   │
└──────────────────────────────────────────────────────────┘

FROM ROUTE:
    update: ProgressUpdate object
    
    Can access:
    {{ update.id }}                          ← Record ID
    {{ update.user.username }}               ← Employee name
    {{ update.user.email }}                  ← Employee email
    {{ update.reporting_period }}            ← daily/weekly/monthly
    {{ update.period_start_date }}           ← Date object
    {{ update.period_end_date }}             ← Date object
    {{ update.completed_work }}              ← Decrypted text
    {{ update.work_in_progress }}            ← Decrypted text
    {{ update.blocked_tasks }}               ← Decrypted text or None
    {{ update.blocked_reasons }}             ← Decrypted text or None
    {{ update.hours_spent }}                 ← Integer (0-720)
    {{ update.effort_level }}                ← low/medium/high
    {{ update.individual_contributions }}    ← Decrypted text
    {{ update.team_work }}                   ← Decrypted text or None
    {{ update.features_worked }}             ← Decrypted text or None
    {{ update.bugs_fixed }}                  ← Decrypted text or None
    {{ update.improvements }}                ← Decrypted text or None
    {{ update.project_status }}              ← on_track/at_risk/delayed
    {{ update.risks_dependencies }}          ← Decrypted text or None
    {{ update.challenges }}                  ← Decrypted text or None
    {{ update.next_priorities }}             ← Decrypted text
    {{ update.notes }}                       ← Decrypted text or None
    {{ update.escalations }}                 ← Decrypted text or None
    {{ update.submitted_at }}                ← DateTime object
    {{ update.reviewed_at }}                 ← DateTime object or None
    {{ update.review_status }}               ← pending/approved/needs_revision
    {{ update.reviewed_by.username }}        ← Admin name (if reviewed)
    {{ update.admin_comments }}              ← Decrypted text (if reviewed)

CONDITIONAL RENDERING:

    {% if update.blocked_tasks %}
        <!-- Show blocker alert -->
        <div class="alert alert-warning">
            {{ update.blocked_tasks }}
        </div>
    {% endif %}
    
    {% if update.escalations %}
        <!-- Show escalation alert -->
        <div class="alert alert-danger">
            {{ update.escalations }}
        </div>
    {% endif %}
    
    {% if update.review_status == 'pending' %}
        <!-- Show pending badge -->
        <span class="badge bg-warning">PENDING</span>
    {% elif update.review_status == 'approved' %}
        <!-- Show approved badge -->
        <span class="badge bg-success">APPROVED</span>
    {% else %}
        <!-- Show revision badge -->
        <span class="badge bg-info">NEEDS REVISION</span>
    {% endif %}
    
    {% if update.admin_comments %}
        <!-- Show admin feedback section -->
        <div class="feedback-section">
            <strong>Admin Feedback:</strong>
            {{ update.admin_comments }}
        </div>
    {% endif %}
    
    {% if update.user_id == current_user.id and
           update.review_status == 'pending' %}
        <!-- Show edit button (only owner, only if pending) -->
        <a href="{{ url_for('progress.edit_update', 
                   update_id=update.id) }}" 
           class="btn btn-primary">
            Edit
        </a>
    {% endif %}
    
    {% if current_user.role == 'admin' and
           update.review_status == 'pending' %}
        <!-- Show review button (admin only, only if pending) -->
        <a href="{{ url_for('progress.admin_review',
                   update_id=update.id) }}" 
           class="btn btn-warning">
            Review
        </a>
    {% endif %}

STATUS BADGE STYLING:
    {% if update.project_status == 'on_track' %}
        <span class="badge bg-success">On Track</span>
    {% elif update.project_status == 'at_risk' %}
        <span class="badge bg-warning">At Risk</span>
    {% else %}
        <span class="badge bg-danger">Delayed</span>
    {% endif %}

EFFORT LEVEL STYLING:
    {% if update.effort_level == 'low' %}
        <span class="badge bg-secondary">Low</span>
    {% elif update.effort_level == 'medium' %}
        <span class="badge bg-info">Medium</span>
    {% else %}
        <span class="badge bg-success">High</span>
    {% endif %}

DATE FORMATTING:
    {{ update.submitted_at.strftime('%b %d, %Y') }}
    <!-- Output: Feb 03, 2026 -->
    
    {{ update.period_start_date }}
    <!-- Output: 2026-01-27 -->

CONTENT SECTIONS (11 display sections):
    
    1. Completed Work
       {{ update.completed_work }}
    
    2. In Progress
       {{ update.work_in_progress }}
    
    3. Blocked Tasks (conditional)
       {% if update.blocked_tasks %}
           {{ update.blocked_tasks }}
       {% endif %}
    
    4. Block Reasons (conditional)
       {% if update.blocked_reasons %}
           {{ update.blocked_reasons }}
       {% endif %}
    
    5. Individual Contributions
       {{ update.individual_contributions }}
    
    6. Team Work (conditional)
       {% if update.team_work %}
           {{ update.team_work }}
       {% endif %}
    
    7. Features Worked (conditional)
       {% if update.features_worked %}
           {{ update.features_worked }}
       {% endif %}
    
    8. Bugs Fixed (conditional)
       {% if update.bugs_fixed %}
           {{ update.bugs_fixed }}
       {% endif %}
    
    9. Improvements (conditional)
       {% if update.improvements %}
           {{ update.improvements }}
       {% endif %}
    
    10. Risks & Dependencies (conditional)
        {% if update.risks_dependencies %}
            {{ update.risks_dependencies }}
        {% endif %}
    
    11. Challenges (conditional)
        {% if update.challenges %}
            {{ update.challenges }}
        {% endif %}
    
    12. Next Priorities
        {{ update.next_priorities }}
    
    13. Notes (conditional)
        {% if update.notes %}
            {{ update.notes }}
        {% endif %}
```

---

### Template 3: admin_pending.html

**Purpose**: Show admin pending queue  
**Source**: Database query with pagination

```
┌──────────────────────────────────────────────────────────┐
│         DATA USED IN admin_pending.html                   │
└──────────────────────────────────────────────────────────┘

FROM ROUTE:
    updates: Paginated results
    now: Current datetime
    
    Route code:
    @progress_bp.route('/admin/pending', methods=['GET'])
    @login_required
    @admin_required
    def admin_pending():
        page = request.args.get('page', 1, type=int)
        updates = ProgressUpdate.query.filter_by(
            review_status='pending'
        ).order_by(
            ProgressUpdate.submitted_at.desc()
        ).paginate(page=page, per_page=15)
        
        return render_template(
            'progress/admin_pending.html',
            updates=updates,
            now=datetime.utcnow()
        )

PAGINATION DATA:
    {{ updates.total }}              ← Total pending count
    {{ updates.pages }}              ← Total pages
    {{ updates.page }}               ← Current page
    {{ updates.has_prev }}           ← Has previous page?
    {{ updates.has_next }}           ← Has next page?
    {{ updates.prev_num }}           ← Previous page number
    {{ updates.next_num }}           ← Next page number
    {{ updates.iter_pages() }}       ← Iterator for page links

METRICS CARDS:
    <!-- Pending count -->
    Pending Count: {{ updates.total }}
    
    <!-- Calculate oldest pending -->
    {% set oldest_pending = updates.items[0] if updates.items %}
    {% if oldest_pending %}
        Oldest: {{ (now - oldest_pending.submitted_at).days }} days
    {% endif %}

TABLE LOOP - For each update:
    {% for update in updates.items %}
        
        Row Data:
        ├─ {{ update.user.username }}        ← User name
        ├─ {{ update.user.email }}           ← User email
        ├─ {{ update.user.role }}            ← User role
        ├─ {{ update.reporting_period }}     ← Period type
        ├─ {{ update.period_start_date }}    ← Start date
        ├─ {{ update.period_end_date }}      ← End date
        ├─ {{ update.project_status }}       ← Project status
        ├─ {{ update.hours_spent }}          ← Hours
        ├─ {{ update.submitted_at }}         ← Submit date
        ├─ {{ update.completed_work[:200] }} ← Preview (first 200 chars)
        ├─ {{ update.blocked_tasks }}        ← Has blockers?
        └─ {{ update.escalations }}          ← Has escalations?
        
        Calculations:
        days_pending = (now - update.submitted_at).days
        
        Status Badge:
        {% if update.review_status == 'pending' %}
            <span class="badge bg-warning">Pending</span>
        {% endif %}
        
        Project Status Badge:
        {% if update.project_status == 'on_track' %}
            <span class="badge bg-success">On Track</span>
        {% elif update.project_status == 'at_risk' %}
            <span class="badge bg-warning">At Risk</span>
        {% else %}
            <span class="badge bg-danger">Delayed</span>
        {% endif %}
        
        Blocker Indicator:
        {% if update.blocked_tasks %}
            <span class="badge bg-danger">⚠️ Blocked</span>
        {% else %}
            <span class="badge bg-success">✓ No Blockers</span>
        {% endif %}
        
        Age Indicator:
        {% if days_pending >= 5 %}
            <span class="badge bg-danger">{{ days_pending }}d</span>
        {% elif days_pending >= 2 %}
            <span class="badge bg-warning">{{ days_pending }}d</span>
        {% else %}
            <span class="badge bg-success">{{ days_pending }}d</span>
        {% endif %}
        
        Action Buttons:
        [View] → /progress/view/<id>
        [Review] → /progress/admin/review/<id>
    
    {% endfor %}

EMPTY STATE:
    {% if not updates.items %}
        <div class="empty-state">
            <h5>No pending updates</h5>
            <p>All reviews are complete!</p>
        </div>
    {% endif %}

PAGINATION LINKS:
    {% for page_num in updates.iter_pages() %}
        {% if page_num %}
            {% if page_num == updates.page %}
                <span class="active">{{ page_num }}</span>
            {% else %}
                <a href="...?page={{ page_num }}">
                    {{ page_num }}
                </a>
            {% endif %}
        {% else %}
            <span>...</span>
        {% endif %}
    {% endfor %}
```

---

### Template 4: admin_all.html

**Purpose**: Show all updates with filters  
**Source**: Filtered database query

```
┌──────────────────────────────────────────────────────────┐
│         DATA USED IN admin_all.html                       │
└──────────────────────────────────────────────────────────┘

FROM ROUTE:
    updates: Filtered, paginated results
    users: All user objects (for filter dropdown)
    now: Current datetime
    total_updates: Count of all updates
    pending_count: Count of pending
    approved_count: Count of approved
    revision_count: Count needing revision

FILTER DROPDOWNS:
    
    User Filter:
    <select name="user_id" onchange="submit()">
        <option value="">All Users</option>
        {% for user in users %}
            <option value="{{ user.id }}"
                    {% if selected_user_id == user.id %}selected{% endif %}>
                {{ user.username }}
            </option>
        {% endfor %}
    </select>
    
    Status Filter:
    <select name="status" onchange="submit()">
        <option value="">All Statuses</option>
        <option value="pending" 
                {% if selected_status == 'pending' %}selected{% endif %}>
            Pending
        </option>
        <option value="approved"
                {% if selected_status == 'approved' %}selected{% endif %}>
            Approved
        </option>
        <option value="needs_revision"
                {% if selected_status == 'needs_revision' %}selected{% endif %}>
            Needs Revision
        </option>
    </select>
    
    Period Filter:
    <select name="period" onchange="submit()">
        <option value="">All Periods</option>
        <option value="daily"
                {% if selected_period == 'daily' %}selected{% endif %}>
            Daily
        </option>
        <option value="weekly"
                {% if selected_period == 'weekly' %}selected{% endif %}>
            Weekly
        </option>
        <option value="monthly"
                {% if selected_period == 'monthly' %}selected{% endif %}>
            Monthly
        </option>
    </select>

TABLE DISPLAY:
    
    For each update in updates.items:
    
    Columns:
    ├─ User
    │  ├─ Avatar: First 2 letters of username
    │  ├─ Name: {{ update.user.username }}
    │  └─ Email: {{ update.user.email }}
    │
    ├─ Period
    │  ├─ Type: {{ update.reporting_period|title }}
    │  └─ Range: {{ update.period_start_date }} - 
    │             {{ update.period_end_date }}
    │
    ├─ Project Status
    │  └─ Badge: Color-coded by status
    │
    ├─ Hours
    │  └─ {{ update.hours_spent }} hrs
    │
    ├─ Review Status
    │  ├─ Pending → 🟡 Yellow
    │  ├─ Approved → 🟢 Green
    │  └─ Needs Revision → 🔵 Blue
    │
    ├─ Submitted Date
    │  ├─ Date: {{ update.submitted_at.strftime('%b %d, %Y') }}
    │  └─ Age: <span class="badge">
    │           {{ (now - update.submitted_at).days }}d ago
    │           </span>
    │
    └─ Actions
       ├─ [View] → /progress/view/<id>
       └─ [Review] (if pending) → /progress/admin/review/<id>

SUMMARY CARDS:
    
    Total Updates:
    {{ total_updates }}
    
    Pending Reviews:
    {{ pending_count }}
    
    Approved:
    {{ approved_count }}
    
    Needs Revision:
    {{ revision_count }}

RESET BUTTON:
    <a href="{{ url_for('progress.admin_all') }}">
        Reset All Filters
    </a>
```

---

### Template 5: admin_review.html

**Purpose**: Review interface with feedback  
**Source**: Single update object + form

```
┌──────────────────────────────────────────────────────────┐
│         DATA USED IN admin_review.html                    │
└──────────────────────────────────────────────────────────┘

FROM ROUTE:
    update: ProgressUpdate object
    form: ReviewProgressUpdateForm object

LAYOUT: Split screen

LEFT SIDE - Update Preview:
    
    Header:
    ├─ {{ update.user.username }}'s Progress Update
    └─ {{ update.reporting_period|title }} 
       ({{ update.period_start_date }} - {{ update.period_end_date }})
    
    Quick Stats Row:
    ├─ Project Status:
    │  {% if update.project_status == 'on_track' %}
    │      <span class="badge bg-success">On Track</span>
    │  {% elif update.project_status == 'at_risk' %}
    │      <span class="badge bg-warning">At Risk</span>
    │  {% else %}
    │      <span class="badge bg-danger">Delayed</span>
    │  {% endif %}
    │
    ├─ Hours: {{ update.hours_spent }} hrs
    │
    ├─ Effort: {{ update.effort_level|title }}
    │  {% if update.effort_level == 'low' %}
    │      <span class="badge bg-secondary">Low</span>
    │  {% elif update.effort_level == 'medium' %}
    │      <span class="badge bg-info">Medium</span>
    │  {% else %}
    │      <span class="badge bg-success">High</span>
    │  {% endif %}
    │
    └─ Blockers:
       {% if update.blocked_tasks %}
           <span class="badge bg-danger">Yes</span>
       {% else %}
           <span class="badge bg-success">No</span>
       {% endif %}
    
    Content Summary:
    ├─ Completed Work:
    │  {{ update.completed_work[:500] }}
    │  {% if update.completed_work|length > 500 %}...{% endif %}
    │
    ├─ Blocked Tasks (if exists):
    │  <div class="alert alert-warning">
    │      {{ update.blocked_tasks }}
    │  </div>
    │
    └─ Escalations (if exists):
       <div class="alert alert-danger">
           {{ update.escalations }}
       </div>
    
    View Full Link:
    [Expand] → /progress/view/<id>

RIGHT SIDE - Review Form (Sticky):
    
    Review Status Dropdown:
    {{ form.review_status }}
    Choices:
    ├─ pending (default)
    ├─ approved
    └─ needs_revision
    
    Admin Comments Textarea:
    {{ form.admin_comments }}
    Placeholder: "Your feedback and observations..."
    Rows: 6
    Help text: "Provide constructive feedback..."
    
    Submit Button:
    {{ form.submit(class="btn btn-primary") }}
    
    Quick Templates:
    <!-- Helpful comment snippets -->
    [👍 Approve] → Auto-fill: "Looks great! Keep up..."
    [⚠️ Needs Info] → Auto-fill: "Please provide more..."

JAVASCRIPT FOR QUICK TEMPLATES:
    
    function setTemplate(message) {
        document.querySelector('textarea[name="admin_comments"]')
            .value = message;
        document.querySelector('select[name="review_status"]')
            .focus();
    }
    
    onclick="setTemplate('Looks great!')"
```

---

### Template 6: admin_stats.html

**Purpose**: Statistics dashboard  
**Source**: Aggregated data from route

```
┌──────────────────────────────────────────────────────────┐
│         DATA USED IN admin_stats.html                     │
└──────────────────────────────────────────────────────────┘

FROM ROUTE:
    stats: Dictionary with all metrics
    recent_updates: List of 10 recent updates
    top_submitters: List of (user, count) tuples
    avg_hours: List of (user, avg_hrs) tuples
    now: Current datetime

STATS DICTIONARY CONTENTS:
    
    stats['total_updates']           ← Total count
    stats['pending_reviews']         ← Pending count
    stats['approved_reviews']        ← Approved count
    stats['needs_revision']          ← Revision count
    stats['on_track']                ← On track count
    stats['at_risk']                 ← At risk count
    stats['delayed']                 ← Delayed count
    stats['effort_low']              ← Low effort count
    stats['effort_medium']           ← Medium effort count
    stats['effort_high']             ← High effort count
    stats['period_daily']            ← Daily count
    stats['period_weekly']           ← Weekly count
    stats['period_monthly']          ← Monthly count

KEY METRICS CARDS:
    
    Total Updates:
    {{ stats['total_updates'] }}
    
    Pending Reviews:
    {{ stats['pending_reviews'] }}
    
    Approved:
    {{ stats['approved_reviews'] }}
    
    Needs Revision:
    {{ stats['needs_revision'] }}

PROJECT STATUS BREAKDOWN:
    
    On Track:
    {{ stats['on_track'] }}
    <div class="progress">
        <div class="progress-bar bg-success"
             style="width: {{ 
                 (stats['on_track'] / 
                  stats['total_updates'] * 100)|int
             }}%">
        </div>
    </div>
    
    At Risk:
    {{ stats['at_risk'] }}
    <div class="progress">
        <div class="progress-bar bg-warning"
             style="width: {{ 
                 (stats['at_risk'] / 
                  stats['total_updates'] * 100)|int
             }}%">
        </div>
    </div>
    
    Delayed:
    {{ stats['delayed'] }}
    <div class="progress">
        <div class="progress-bar bg-danger"
             style="width: {{ 
                 (stats['delayed'] / 
                  stats['total_updates'] * 100)|int
             }}%">
        </div>
    </div>

EFFORT DISTRIBUTION:
    
    Low: {{ stats['effort_low'] }}
    Width: {{ (stats['effort_low'] / 
               stats['total_updates'] * 100)|int }}%
    
    Medium: {{ stats['effort_medium'] }}
    Width: {{ (stats['effort_medium'] / 
               stats['total_updates'] * 100)|int }}%
    
    High: {{ stats['effort_high'] }}
    Width: {{ (stats['effort_high'] / 
               stats['total_updates'] * 100)|int }}%

PERIOD BREAKDOWN:
    
    Daily: {{ stats['period_daily'] }}
    Width: {{ (stats['period_daily'] / 
               stats['total_updates'] * 100)|int }}%
    
    Weekly: {{ stats['period_weekly'] }}
    Width: {{ (stats['period_weekly'] / 
               stats['total_updates'] * 100)|int }}%
    
    Monthly: {{ stats['period_monthly'] }}
    Width: {{ (stats['period_monthly'] / 
               stats['total_updates'] * 100)|int }}%

TOP SUBMITTERS TABLE:
    
    {% for user, count in top_submitters %}
        <tr>
            <td>{{ user.username }}</td>
            <td><span class="badge bg-primary">
                {{ count }}
            </span></td>
        </tr>
    {% endfor %}

AVERAGE HOURS TABLE:
    
    {% for user, avg_hrs in avg_hours %}
        <tr>
            <td>{{ user.username }}</td>
            <td><span class="badge bg-info">
                {{ avg_hrs|round(1) }} hrs
            </span></td>
        </tr>
    {% endfor %}

RECENT SUBMISSIONS TABLE:
    
    {% for update in recent_updates %}
        <tr>
            <td>{{ update.user.username }}</td>
            <td>{{ update.reporting_period|title }}</td>
            <td>
                {% if update.project_status == 'on_track' %}
                    <span class="badge bg-success">On Track</span>
                {% elif update.project_status == 'at_risk' %}
                    <span class="badge bg-warning">At Risk</span>
                {% else %}
                    <span class="badge bg-danger">Delayed</span>
                {% endif %}
            </td>
            <td>{{ update.hours_spent }} hrs</td>
            <td>
                {% if update.review_status == 'pending' %}
                    <span class="badge bg-warning">Pending</span>
                {% elif update.review_status == 'approved' %}
                    <span class="badge bg-success">Approved</span>
                {% else %}
                    <span class="badge bg-info">Revision</span>
                {% endif %}
            </td>
            <td>
                {{ update.submitted_at.strftime('%b %d, %Y') }}
            </td>
            <td>
                <a href="{{ url_for('progress.view_update',
                           update_id=update.id) }}">
                    View
                </a>
            </td>
        </tr>
    {% endfor %}
```

---

## 🎨 Conditional Rendering Patterns

All templates use these patterns:

```
# Pattern 1: Check if field has content (optional fields)
{% if update.blocked_tasks %}
    <!-- Show only if blocked_tasks is not None/empty -->
    <div>{{ update.blocked_tasks }}</div>
{% endif %}

# Pattern 2: Enum-based display (status colors)
{% if update.project_status == 'on_track' %}
    <span class="badge bg-success">On Track</span>
{% elif update.project_status == 'at_risk' %}
    <span class="badge bg-warning">At Risk</span>
{% else %}
    <span class="badge bg-danger">Delayed</span>
{% endif %}

# Pattern 3: Role-based buttons (authorization)
{% if current_user.role == 'admin' %}
    <a href="{{ url_for('progress.admin_review',
               update_id=update.id) }}">
        Review
    </a>
{% endif %}

# Pattern 4: Owner-based editing (user isolation)
{% if update.user_id == current_user.id %}
    <a href="{{ url_for('progress.edit_update',
               update_id=update.id) }}">
        Edit
    </a>
{% endif %}

# Pattern 5: Date calculations (age/pending)
{% set days_ago = (now - update.submitted_at).days %}
{{ days_ago }} days ago

# Pattern 6: Text preview (long content)
{{ update.completed_work[:200] }}
{% if update.completed_work|length > 200 %}...{% endif %}

# Pattern 7: List iteration (pagination)
{% for update in updates.items %}
    <!-- Render each update -->
{% endfor %}

# Pattern 8: Pagination links
{% for page_num in updates.iter_pages() %}
    {% if page_num %}
        <a href="...?page={{ page_num }}">{{ page_num }}</a>
    {% else %}
        <span>...</span>
    {% endif %}
{% endfor %}

# Pattern 9: Form field rendering with errors
<div class="form-group">
    {{ form.completed_work.label }}
    {{ form.completed_work(class="form-control" +
                          (" is-invalid" 
                           if form.completed_work.errors else "")) }}
    {% if form.completed_work.errors %}
        <div class="invalid-feedback">
            {{ form.completed_work.errors[0] }}
        </div>
    {% endif %}
</div>

# Pattern 10: Calculation-based styling
{% set percentage = (stat_value / total * 100)|int %}
<div class="progress-bar" style="width: {{ percentage }}%">
    {{ percentage }}%
</div>
```

---

## 🧩 Complete Data Mapping Summary

| Template | Main Data | Count | Purpose |
|----------|-----------|-------|---------|
| submit_update.html | ProgressUpdateForm | 25 fields | Collect data from employee |
| view_update.html | ProgressUpdate | 27 columns | Display update to user |
| my_updates.html | List[ProgressUpdate] | 10 per page | Show employee's updates |
| admin_pending.html | List[ProgressUpdate] | 15 per page | Show pending queue |
| admin_all.html | List[ProgressUpdate] | 15 per page | Show filtered updates |
| admin_review.html | ProgressUpdate + Form | 1 + 2 fields | Review & provide feedback |
| admin_stats.html | Stats dict | 13 metrics | Show dashboard |

---

This complete guide shows exactly how data flows from database → routes → templates → browser, with all the conditional logic and styling applied!

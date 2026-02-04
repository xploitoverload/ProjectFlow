# 🔥 COMPLETE EXHAUSTIVE APPLICATION MANUAL - PART 2

**Continuing from Part 1...** Everything you need to know.

---

## 🎯 All Decorators & Middlewares

### Security Decorators (app/security/decorators.py)

```python
# DECORATOR 1: @login_required
# Location: Flask-Login built-in
# Purpose: Ensure user is logged in
# Applied to: Most routes
#
# How it works:
# 1. Check if user in session
# 2. If not: Redirect to /login
# 3. If yes: Allow route to execute
#
# Usage:
@app.route('/dashboard')
@login_required
def dashboard():
    # current_user is automatically available
    return render_template('dashboard.html', user=current_user)
#
# If not logged in:
# - Redirected to /login
# - After login, redirected to requested page
# - No error message shown (silent redirect)
#
# Parameters:
# - None
# - No configuration needed

# DECORATOR 2: @admin_required
# Location: Custom decorator in security/decorators.py
# Purpose: Ensure user is admin
# Applied to: Admin-only routes
#
# How it works:
# 1. Check if user logged in (uses @login_required internally)
# 2. Check if user.role == 'admin'
# 3. If not admin: Return 403 Forbidden
# 4. If admin: Allow route to execute
#
# Usage:
@app.route('/admin/users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)
#
# If not admin:
# - Error page shown: "403 Forbidden - Access Denied"
# - No redirect
# - Logged in users see error
# - Not logged in users redirected to /login first
#
# Typical error:
# HTTP 403 Forbidden
# You do not have permission to access this resource
#
# Code:
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user is None or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# DECORATOR 3: @manager_required (optional)
# Location: Custom decorator
# Purpose: Manager or admin only
# Applied to: Manager features
#
# How it works:
# 1. Check if user logged in
# 2. Check if user.role in ['admin', 'manager']
# 3. If not: Return 403 Forbidden
# 4. If yes: Allow
#
# Usage:
@app.route('/progress/admin/pending')
@manager_required  # Both admin and manager can access
def pending_reviews():
    updates = ProgressUpdate.query.filter_by(review_status='pending').all()
    return render_template('progress/admin_pending.html', updates=updates)

# DECORATOR 4: @method_required
# Location: Builtin
# Purpose: Only allow specific HTTP methods
#
# How it works:
# 1. Check request method (GET, POST, PUT, DELETE)
# 2. If not in allowed methods: Return 405 Method Not Allowed
#
# Usage:
@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    # GET: Show form
    # POST: Process form
    # PUT, DELETE: Not allowed (405 error)

# DECORATOR 5: @require_http_methods
# Location: django.views.decorators.http (from Flask utils)
# Purpose: Require specific HTTP method
#
# Example:
from flask import request

@app.route('/api/data', methods=['POST'])
def api_post():
    # Only POST allowed
    # GET will return 405
```

### Middleware (app/middleware/auth_middleware.py)

```python
# MIDDLEWARE 1: Authentication Middleware
# Location: app/middleware/auth_middleware.py
# Purpose: Process authentication on every request
# Execution: Before every route handler
#
# What it does:
# 1. Load user from session
# 2. Set current_user in request context
# 3. Check if session expired
# 4. Update last_activity
# 5. Check if account locked (5+ failed attempts)
# 6. Add CSRF token to request
#
# How it works:
# app.py:
# 1. @app.before_request
# 2. auth_middleware.process_request()
# 3. Load user from session (user_id)
# 4. If found: current_user = user object
# 5. If not found: current_user = AnonymousUser()
# 6. Check session timeout (30 mins inactivity)
# 7. If expired: Logout user, redirect to /login
#
# Usage:
# Automatic, no manual implementation needed
#
# Example flow:
# Request comes in
# ↓
# @app.before_request (middleware runs)
# ↓
# Load user from session (user_id stored in cookie)
# ↓
# Set current_user = User(id=5)
# ↓
# Route handler executes
# ↓
# Can access {{ current_user.username }}
# ↓
# Response sent
# ↓
# @app.after_request (middleware runs again)
# ↓
# Update last_activity timestamp
# ↓
# Set response headers (security headers)

# MIDDLEWARE 2: Error Handlers
# Location: app/__init__.py
#
# 404 Not Found:
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
# Triggered when: Route doesn't exist
# Shows: "Page not found"

# 403 Forbidden:
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403
# Triggered when: User lacks permission
# Shows: "Access denied"

# 500 Internal Server Error:
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
# Triggered when: Server error
# Shows: "Something went wrong"

# MIDDLEWARE 3: Request Logging
# Location: app/__init__.py
#
# Logs every request:
@app.before_request
def log_request():
    if request.method != 'OPTIONS':
        logging.info(f"{request.method} {request.path}")
#
# Logs to: server.log
# Format: TIMESTAMP - METHOD - PATH - IP - USER
# Used for: Debugging, security audit trail
```

---

## 📊 Complete Models Reference

### User Model (app/models.py or models.py)

```python
class User(UserMixin, db.Model):
    """User account model"""
    
    # COLUMNS
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email_encrypted = db.Column(db.Text, nullable=False, index=True)
    role = db.Column(db.String(20), default='user')
    full_name = db.Column(db.String(120))
    department = db.Column(db.String(100))
    avatar_url = db.Column(db.String(255))
    phone_encrypted = db.Column(db.Text)
    address_encrypted = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # RELATIONSHIPS
    projects_created = db.relationship('Project', backref='creator', foreign_keys='Project.created_by')
    issues_assigned = db.relationship('Issue', backref='assignee', foreign_keys='Issue.assigned_to')
    issues_created = db.relationship('Issue', backref='creator', foreign_keys='Issue.created_by')
    progress_updates = db.relationship('ProgressUpdate', backref='user', foreign_keys='ProgressUpdate.user_id')
    reviews_given = db.relationship('ProgressUpdate', backref='reviewer', foreign_keys='ProgressUpdate.reviewed_by')
    reports = db.relationship('Report', backref='user', foreign_keys='Report.user_id')
    
    # PROPERTIES (Encrypted fields - auto-decrypt)
    @property
    def email(self):
        """Get decrypted email"""
        if self.email_encrypted:
            return decrypt(self.email_encrypted)
        return None
    
    @email.setter
    def email(self, value):
        """Set email (auto-encrypts)"""
        if value:
            self.email_encrypted = encrypt(value)
    
    @property
    def phone(self):
        """Get decrypted phone"""
        if self.phone_encrypted:
            return decrypt(self.phone_encrypted)
        return None
    
    @phone.setter
    def phone(self, value):
        """Set phone (auto-encrypts)"""
        if value:
            self.phone_encrypted = encrypt(value)
    
    @property
    def address(self):
        """Get decrypted address"""
        if self.address_encrypted:
            return decrypt(self.address_encrypted)
        return None
    
    @address.setter
    def address(self, value):
        """Set address (auto-encrypts)"""
        if value:
            self.address_encrypted = encrypt(value)
    
    # METHODS
    def set_password(self, password):
        """Hash and store password"""
        # Usage: user.set_password('password123')
        # Hashing: PBKDF2-SHA256 with 600,000 iterations
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password correct"""
        # Usage: if user.check_password('password123'): ...
        # Returns: True if match, False otherwise
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_manager(self):
        """Check if user is manager or admin"""
        return self.role in ['admin', 'manager']
    
    def is_locked(self):
        """Check if account locked (5+ failed attempts)"""
        return self.failed_login_attempts >= 5
    
    def reset_failed_attempts(self):
        """Clear failed login count"""
        self.failed_login_attempts = 0
    
    def increment_failed_attempts(self):
        """Add 1 to failed attempts"""
        self.failed_login_attempts += 1
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
    
    def __repr__(self):
        return f'<User {self.username}>'
```

### Project Model

```python
class Project(db.Model):
    """Project model"""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='planning')  # planning, active, completed, on_hold
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Numeric(10, 2))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS
    issues = db.relationship('Issue', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    # METHODS
    def get_issue_count(self):
        """Get total issues in project"""
        return self.issues.count()
    
    def get_open_issues(self):
        """Get open issues in project"""
        return self.issues.filter_by(status='open').count()
    
    def get_progress(self):
        """Get project progress percentage"""
        total = self.issues.count()
        if total == 0:
            return 0
        closed = self.issues.filter_by(status='closed').count()
        return int((closed / total) * 100)
    
    def __repr__(self):
        return f'<Project {self.name}>'
```

### Issue Model

```python
class Issue(db.Model):
    """Issue/Task model"""
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='open', index=True)  # open, in_progress, closed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS
    comments = db.relationship('Comment', backref='issue', lazy='dynamic', cascade='all, delete-orphan')
    
    # PROPERTIES
    @property
    def is_overdue(self):
        """Check if issue overdue"""
        if self.due_date and self.status != 'closed':
            return date.today() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        """Days until due date"""
        if self.due_date:
            return (self.due_date - date.today()).days
        return None
    
    # METHODS
    def __repr__(self):
        return f'<Issue {self.title}>'
```

### ProgressUpdate Model

```python
class ProgressUpdate(db.Model):
    """Progress update model (27 columns, 15 encrypted)"""
    
    id = db.Column(db.Integer, primary_key=True)
    
    # SUBMITTER
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # PERIOD
    reporting_period = db.Column(db.String(20))  # daily, weekly, monthly
    period_start_date = db.Column(db.Date)
    period_end_date = db.Column(db.Date)
    
    # WORK (Encrypted)
    completed_work_encrypted = db.Column(db.Text)
    work_in_progress_encrypted = db.Column(db.Text)
    blocked_tasks_encrypted = db.Column(db.Text)
    blocked_reasons_encrypted = db.Column(db.Text)
    
    # EFFORT
    hours_spent = db.Column(db.Integer)  # 0-720
    effort_level = db.Column(db.String(20))  # low, medium, high
    
    # CONTRIBUTIONS (Encrypted)
    individual_contributions_encrypted = db.Column(db.Text)
    team_work_encrypted = db.Column(db.Text)
    features_worked_encrypted = db.Column(db.Text)
    bugs_fixed_encrypted = db.Column(db.Text)
    improvements_encrypted = db.Column(db.Text)
    
    # PROJECT
    project_status = db.Column(db.String(20))  # on_track, at_risk, delayed
    
    # RISKS (Encrypted)
    risks_dependencies_encrypted = db.Column(db.Text)
    challenges_encrypted = db.Column(db.Text)
    
    # PLANNING (Encrypted)
    next_priorities_encrypted = db.Column(db.Text)
    notes_encrypted = db.Column(db.Text)
    escalations_encrypted = db.Column(db.Text)
    
    # REVIEW
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    review_status = db.Column(db.String(20), default='pending', index=True)  # pending, approved, needs_revision
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    reviewed_at = db.Column(db.DateTime)
    admin_comments_encrypted = db.Column(db.Text)
    
    # RELATIONSHIPS
    # user: The submitter (foreign key)
    # reviewer: The manager/admin who reviewed it (foreign key)
    
    # PROPERTIES (Auto-decrypt encrypted fields)
    @property
    def completed_work(self):
        if self.completed_work_encrypted:
            return decrypt(self.completed_work_encrypted)
        return None
    
    @completed_work.setter
    def completed_work(self, value):
        if value:
            self.completed_work_encrypted = encrypt(value)
    
    # (15 similar properties for all encrypted fields...)
    
    # METHODS
    def is_pending(self):
        """Check if pending review"""
        return self.review_status == 'pending'
    
    def is_approved(self):
        """Check if approved"""
        return self.review_status == 'approved'
    
    def needs_revision(self):
        """Check if needs revision"""
        return self.review_status == 'needs_revision'
    
    def get_period_display(self):
        """Get formatted period"""
        return f"{self.period_start_date} - {self.period_end_date}"
    
    def days_pending(self):
        """Days since submitted"""
        return (datetime.utcnow() - self.submitted_at).days
```

---

## 🎨 All Templates - What They Show

### Base Template (templates/base.html)

```html
<!-- Master template that all pages extend -->

<!DOCTYPE html>
<html>
<head>
    <!-- Metadata -->
    <title>{% block title %}Project Management System{% endblock %}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <!-- CSS Files -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/bootstrap.min.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/responsive.css') }}">
</head>
<body>
    <!-- NAVIGATION BAR (Top) -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <!-- Logo -->
            <a class="navbar-brand" href="/">
                <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
                Project Management
            </a>
            
            <!-- Hamburger Menu (Mobile) -->
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <!-- Navigation Links -->
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ml-auto">
                    {% if current_user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href="/dashboard">Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/projects">Projects</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/issues">Issues</a>
                        </li>
                        
                        <!-- Admin Only -->
                        {% if current_user.is_admin() %}
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" id="adminMenu" role="button" data-toggle="dropdown">
                                Admin
                            </a>
                            <div class="dropdown-menu" aria-labelledby="adminMenu">
                                <a class="dropdown-item" href="/admin">Dashboard</a>
                                <a class="dropdown-item" href="/admin/users">Users</a>
                                <a class="dropdown-item" href="/admin/projects">Projects</a>
                                <a class="dropdown-item" href="/admin/issues">Issues</a>
                                <div class="dropdown-divider"></div>
                                <a class="dropdown-item" href="/admin/settings">Settings</a>
                            </div>
                        </li>
                        {% endif %}
                        
                        <!-- User Dropdown -->
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" id="userMenu" role="button" data-toggle="dropdown">
                                {{ current_user.username }}
                            </a>
                            <div class="dropdown-menu dropdown-menu-right" aria-labelledby="userMenu">
                                <a class="dropdown-item" href="/profile">Profile</a>
                                <a class="dropdown-item" href="/settings">Settings</a>
                                <div class="dropdown-divider"></div>
                                <a class="dropdown-item" href="/logout">Logout</a>
                            </div>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="/login">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/register">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    
    <!-- SIDEBAR (Left, if needed) -->
    <div class="container-fluid">
        <div class="row">
            {% if current_user.is_authenticated %}
            <nav class="col-md-2 d-md-block bg-light sidebar">
                <div class="sidebar-sticky">
                    <h5 class="sidebar-heading">Menu</h5>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="/dashboard">
                                <i class="fas fa-home"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/progress/submit">
                                <i class="fas fa-pencil"></i> Submit Update
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/progress/my-updates">
                                <i class="fas fa-list"></i> My Updates
                            </a>
                        </li>
                        
                        {% if current_user.is_manager() %}
                        <hr>
                        <h5 class="sidebar-heading">Management</h5>
                        <li class="nav-item">
                            <a class="nav-link" href="/progress/admin/pending">
                                <i class="fas fa-tasks"></i> Reviews
                                <span class="badge badge-danger">{{ pending_count }}</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/progress/admin/stats">
                                <i class="fas fa-chart-bar"></i> Statistics
                            </a>
                        </li>
                        {% endif %}
                    </ul>
                </div>
            </nav>
            {% endif %}
            
            <!-- MAIN CONTENT -->
            <main role="main" class="col-md-10 ml-sm-auto px-md-4">
                <!-- Flash Messages (Success/Error alerts) -->
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                        <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }} alert-dismissible fade show" role="alert">
                            {{ message }}
                            <button type="button" class="close" data-dismiss="alert">
                                <span>&times;</span>
                            </button>
                        </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                <!-- PAGE CONTENT GOES HERE -->
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
    
    <!-- FOOTER -->
    <footer class="footer mt-auto py-3 bg-light">
        <div class="container text-center">
            <span class="text-muted">© 2026 Project Management System. All rights reserved.</span>
        </div>
    </footer>
    
    <!-- JavaScript Files -->
    <script src="{{ url_for('static', filename='js/jquery-3.5.1.slim.min.js') }}"></script>
    <script src="{{ url_for('static', filename='js/bootstrap.bundle.min.js') }}"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    
    <!-- Page-specific JavaScript -->
    {% block scripts %}{% endblock %}
</body>
</html>
```

### Login Template (templates/auth/login.html)

```html
{% extends "base.html" %}

{% block title %}Login - Project Management{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">Sign In</h4>
                </div>
                <div class="card-body">
                    <form method="POST" novalidate>
                        {{ form.hidden_tag() }}  <!-- CSRF token -->
                        
                        <!-- Username Field -->
                        <div class="form-group">
                            {{ form.username.label }}
                            {% if form.username.errors %}
                                {{ form.username(class="form-control is-invalid") }}
                                <div class="invalid-feedback">
                                    {% for error in form.username.errors %}
                                        <span>{{ error }}</span>
                                    {% endfor %}
                                </div>
                            {% else %}
                                {{ form.username(class="form-control") }}
                            {% endif %}
                        </div>
                        
                        <!-- Password Field -->
                        <div class="form-group">
                            {{ form.password.label }}
                            {% if form.password.errors %}
                                {{ form.password(class="form-control is-invalid") }}
                                <div class="invalid-feedback">
                                    {% for error in form.password.errors %}
                                        <span>{{ error }}</span>
                                    {% endfor %}
                                </div>
                            {% else %}
                                {{ form.password(class="form-control") }}
                            {% endif %}
                        </div>
                        
                        <!-- Remember Me -->
                        <div class="form-check mb-3">
                            {{ form.remember_me(class="form-check-input") }}
                            {{ form.remember_me.label(class="form-check-label") }}
                        </div>
                        
                        <!-- Submit Button -->
                        <div class="d-grid gap-2">
                            {{ form.submit(class="btn btn-primary btn-block") }}
                        </div>
                    </form>
                    
                    <hr>
                    
                    <!-- Links -->
                    <p class="text-center">
                        Don't have an account? <a href="/register">Register here</a>
                    </p>
                    <p class="text-center">
                        <a href="/forgot-password">Forgot password?</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Dashboard Template (templates/dashboard.html)

```html
{% extends "base.html" %}

{% block title %}Dashboard - Project Management{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>Welcome, {{ current_user.full_name or current_user.username }}!</h1>
    
    <!-- Quick Stats Cards -->
    <div class="row mt-4">
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Updates Submitted</h5>
                    <h2 class="card-text text-primary">{{ total_updates }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Pending Review</h5>
                    <h2 class="card-text text-warning">{{ pending_updates }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Approved</h5>
                    <h2 class="card-text text-success">{{ approved_updates }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Assigned Issues</h5>
                    <h2 class="card-text text-info">{{ assigned_issues }}</h2>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Main Content Row -->
    <div class="row mt-4">
        <!-- Left Column -->
        <div class="col-md-8">
            <!-- Recent Updates Section -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Recent Progress Updates</h5>
                </div>
                <div class="card-body">
                    {% if recent_updates %}
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Period</th>
                                <th>Status</th>
                                <th>Submitted</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for update in recent_updates %}
                            <tr>
                                <td>
                                    {{ update.reporting_period }} 
                                    ({{ update.period_start_date }} - {{ update.period_end_date }})
                                </td>
                                <td>
                                    {% if update.review_status == 'pending' %}
                                        <span class="badge badge-warning">Pending</span>
                                    {% elif update.review_status == 'approved' %}
                                        <span class="badge badge-success">Approved</span>
                                    {% else %}
                                        <span class="badge badge-info">Revision</span>
                                    {% endif %}
                                </td>
                                <td>{{ update.submitted_at.strftime('%m/%d %H:%M') }}</td>
                                <td>
                                    <a href="/progress/view/{{ update.id }}" class="btn btn-sm btn-outline-primary">View</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <p class="text-muted">No updates yet. <a href="/progress/submit">Submit your first update</a></p>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <!-- Right Column (Sidebar) -->
        <div class="col-md-4">
            <!-- Quick Actions -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Quick Actions</h5>
                </div>
                <div class="card-body">
                    <a href="/progress/submit" class="btn btn-primary btn-block mb-2">
                        <i class="fas fa-plus"></i> New Update
                    </a>
                    <a href="/progress/my-updates" class="btn btn-outline-primary btn-block mb-2">
                        <i class="fas fa-list"></i> View Updates
                    </a>
                    {% if current_user.is_manager() %}
                    <a href="/progress/admin/pending" class="btn btn-outline-warning btn-block mb-2">
                        <i class="fas fa-tasks"></i> Pending Reviews
                    </a>
                    {% endif %}
                </div>
            </div>
            
            <!-- Announcements -->
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Announcements</h5>
                </div>
                <div class="card-body">
                    {% if announcements %}
                        {% for announcement in announcements %}
                        <div class="alert alert-info mb-2" role="alert">
                            {{ announcement.text }}
                        </div>
                        {% endfor %}
                    {% else %}
                    <p class="text-muted">No announcements.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 📄 Static Files - CSS, JS, Images

### CSS Organization (static/css/)

```
static/css/
├── bootstrap.min.css
│   └─ Bootstrap 5 framework (responsive grid, components)
│
├── style.css
│   ├─ Color scheme
│   ├─ Custom components
│   ├─ Form styling
│   ├─ Card styling
│   ├─ Badge colors
│   ├─ Button styles
│   ├─ Alert styles
│   └─ Typography
│
└── responsive.css
    ├─ Mobile breakpoints (480px, 768px, 1024px)
    ├─ Tablet adjustments
    ├─ Desktop optimizations
    ├─ Sidebar collapsing
    ├─ Navigation adjustments
    └─ Table responsiveness
```

### JavaScript Organization (static/js/)

```
static/js/
├── jquery-3.5.1.slim.min.js
│   └─ jQuery library (DOM manipulation, events)
│
├── bootstrap.bundle.min.js
│   └─ Bootstrap JS (modals, dropdowns, alerts)
│
├── main.js
│   ├─ Global functions
│   ├─ Event listeners
│   ├─ Form validation
│   └─ UI interactions
│
├── form-validation.js
│   ├─ Client-side validation
│   ├─ Field error highlighting
│   ├─ Real-time validation feedback
│   └─ Form submission handling
│
└─ progress-dates.js
    ├─ Auto-fill dates based on period
    ├─ Weekly date calculation
    ├─ Monthly date calculation
    └─ Custom date handling
```

### Images (static/images/)

```
static/images/
├── logo.png
│   └─ Application logo (displayed in navbar)
│
├── favicon.ico
│   └─ Browser tab icon
│
├── placeholder.jpg
│   └─ Default user avatar
│
└── [other images]
    └─ Banners, decorative images, icons
```

---

## ⚠️ Error Codes & Messages

### HTTP Status Codes

```
200 OK
  └─ Request successful
  └─ Used for: GET, POST successful

201 Created
  └─ Resource created
  └─ Used for: POST creating new resource

204 No Content
  └─ Successful but no response body
  └─ Used for: DELETE operations

301 Moved Permanently
  └─ Resource moved to new URL
  └─ Used for: URL redirects

302 Found (Temporary Redirect)
  └─ Temporary redirect
  └─ Used for: After successful login (/dashboard)

304 Not Modified
  └─ Content hasn't changed
  └─ Used for: Cached resources

400 Bad Request
  └─ Invalid request data
  └─ Example: Form validation failed
  └─ Message: "Invalid input data"

401 Unauthorized
  └─ Not authenticated
  └─ Example: Try to access /dashboard without login
  └─ Action: Redirect to /login

403 Forbidden
  └─ Authenticated but not authorized
  └─ Example: Employee tries /admin/users
  └─ Message: "You don't have permission to access this resource"

404 Not Found
  └─ Resource doesn't exist
  └─ Example: /progress/view/999 (update ID 999 doesn't exist)
  └─ Message: "Page not found"

405 Method Not Allowed
  └─ Wrong HTTP method
  └─ Example: GET /progress/submit-form returns 405
  └─ Message: "This method is not allowed"

409 Conflict
  └─ Request conflicts with current state
  └─ Example: Username already taken on register
  └─ Message: "This username is already in use"

413 Payload Too Large
  └─ File/data too large
  └─ Example: Upload file > 16 MB
  └─ Message: "File too large"

422 Unprocessable Entity
  └─ Request is well-formed but contains logic errors
  └─ Example: end_date < start_date
  └─ Message: "End date must be after start date"

429 Too Many Requests
  └─ Rate limiting
  └─ Example: Too many login attempts
  └─ Message: "Too many requests. Try again later"

500 Internal Server Error
  └─ Server error
  └─ Example: Database connection lost
  └─ Message: "Something went wrong. Try again later"

503 Service Unavailable
  └─ Server temporarily down
  └─ Example: Database maintenance
  └─ Message: "Service temporarily unavailable"
```

### Custom Error Messages

```
AUTHENTICATION ERRORS:
- "Invalid credentials" (wrong username/password)
- "Account locked. Too many failed attempts" (5+ failed)
- "Email not found" (forgot password)
- "Token expired" (password reset link too old)
- "Session expired. Please login again" (timeout)

VALIDATION ERRORS:
- "This field is required" (empty required field)
- "Text must be 10-1000 characters" (length violation)
- "Hours must be 0-720" (range violation)
- "Invalid date format" (bad date)
- "Username already taken" (duplicate)
- "Email already in use" (duplicate)
- "Passwords don't match" (confirm password mismatch)

AUTHORIZATION ERRORS:
- "You don't have permission" (role check failed)
- "Cannot edit approved updates" (status check failed)
- "Can only view own data" (ownership check failed)

DATABASE ERRORS:
- "Database connection failed" (DB down)
- "Record not found" (invalid ID)
- "Transaction failed" (save error)

FORM ERRORS:
- "CSRF token invalid" (cross-site attack detected)
- "Invalid form data" (malformed submission)
```

---

## 🔌 API Complete Reference

### API Response Format

```json
// Success response
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Project Name",
    ...
  }
}

// Error response
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE"
}

// List response
{
  "status": "success",
  "data": [
    { "id": 1, "name": "Item 1" },
    { "id": 2, "name": "Item 2" }
  ],
  "total": 2,
  "page": 1,
  "pages": 1
}
```

### API Endpoints

```
GET /api/projects
  Purpose: Get all projects
  Authentication: @login_required
  Response: Array of projects
  Example:
  $ curl http://localhost:5000/api/projects \
    -H "Authorization: Bearer token"
  
  Response:
  {
    "status": "success",
    "data": [
      {
        "id": 1,
        "name": "Mobile App",
        "status": "active",
        "priority": "high",
        "start_date": "2026-01-01",
        "end_date": "2026-05-31"
      }
    ]
  }

GET /api/projects/<id>
  Purpose: Get single project
  Parameter: id (integer)
  Response: Single project object
  Status codes: 200 (found), 404 (not found)

GET /api/issues
  Purpose: Get all issues
  Query parameters:
    - status: Filter by status
    - priority: Filter by priority
    - project_id: Filter by project
  Response: Array of issues

GET /api/issues/<id>
  Purpose: Get single issue
  Parameter: id (integer)
  Response: Single issue object
```

---

## 📊 Database Operations - CRUD Examples

### CREATE (Create new record)

```python
# CREATE USER
from models import User, db

new_user = User(
    username='john_doe',
    email='john@example.com',
    role='admin',
    full_name='John Doe',
    department='Engineering'
)
new_user.set_password('password123')
db.session.add(new_user)
db.session.commit()
print(f"User created with ID: {new_user.id}")

# CREATE PROJECT
from models import Project

new_project = Project(
    name='Mobile App',
    description='Redesign mobile UI',
    status='active',
    priority='high',
    created_by=1  # User ID
)
db.session.add(new_project)
db.session.commit()
print(f"Project created: {new_project.id}")

# CREATE PROGRESS UPDATE
from models import ProgressUpdate

new_update = ProgressUpdate(
    user_id=5,
    reporting_period='weekly',
    period_start_date=date(2026, 2, 1),
    period_end_date=date(2026, 2, 7),
    completed_work='Fixed bugs, implemented features',
    work_in_progress='Working on API docs',
    hours_spent=40,
    effort_level='high',
    project_status='on_track'
)
db.session.add(new_update)
db.session.commit()
print(f"Update created: {new_update.id}")
```

### READ (Retrieve records)

```python
# READ single user by username
user = User.query.filter_by(username='john_doe').first()
if user:
    print(f"Found: {user.full_name}")
else:
    print("User not found")

# READ user by ID
user = User.query.get(5)

# READ all users
users = User.query.all()
for user in users:
    print(user.username)

# READ with filtering
admin_users = User.query.filter_by(role='admin').all()

# READ with filtering and ordering
recent_updates = ProgressUpdate.query.filter_by(
    user_id=5
).order_by(
    ProgressUpdate.submitted_at.desc()
).all()

# READ with limit
first_10 = User.query.limit(10).all()

# READ with pagination
page = 2
items_per_page = 15
results = User.query.paginate(page=page, per_page=items_per_page)
print(f"Page {results.page} of {results.pages}")
for user in results.items:
    print(user.username)

# READ count
total_users = User.query.count()
print(f"Total users: {total_users}")

# READ with complex filter
from sqlalchemy import and_, or_

results = ProgressUpdate.query.filter(
    and_(
        ProgressUpdate.user_id == 5,
        ProgressUpdate.review_status == 'pending',
        ProgressUpdate.project_status.in_(['at_risk', 'delayed'])
    )
).all()
```

### UPDATE (Modify record)

```python
# UPDATE user email
user = User.query.get(5)
user.email = 'newemail@example.com'
db.session.commit()

# UPDATE multiple fields
user.full_name = 'John Updated'
user.department = 'Management'
user.role = 'manager'
db.session.commit()

# UPDATE password
user = User.query.get(5)
user.set_password('newpassword123')
db.session.commit()

# UPDATE progress update status
update = ProgressUpdate.query.get(10)
update.review_status = 'approved'
update.reviewed_by = 1  # Admin ID
update.reviewed_at = datetime.utcnow()
update.admin_comments = 'Great work!'
db.session.commit()

# UPDATE multiple records
users = User.query.filter_by(is_active=True).all()
for user in users:
    user.last_login = datetime.utcnow()
db.session.commit()

# Bulk update (more efficient)
User.query.filter_by(department='Engineering').update(
    {'department': 'Tech'}
)
db.session.commit()
```

### DELETE (Remove record)

```python
# DELETE single record
user = User.query.get(5)
db.session.delete(user)
db.session.commit()

# DELETE with filter
updates = ProgressUpdate.query.filter_by(review_status='needs_revision').all()
for update in updates:
    db.session.delete(update)
db.session.commit()

# Bulk delete (efficient)
ProgressUpdate.query.filter_by(user_id=5).delete()
db.session.commit()

# DELETE cascade (deletes related records too)
project = Project.query.get(1)
db.session.delete(project)
db.session.commit()
# This also deletes all issues in this project
```

---

## 💻 Frontend JavaScript Details

### main.js (Global Functions)

```javascript
// UTILITY FUNCTIONS

// Format date (YYYY-MM-DD to readable)
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}
// Usage: formatDate('2026-02-03') → "Feb 03, 2026"

// Show alert message
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.insertBefore(alertDiv, document.body.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => alertDiv.remove(), 5000);
}
// Usage: showAlert('Update saved!', 'success')

// Validate form before submit
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form.checkValidity()) {
        event.preventDefault();
        form.classList.add('was-validated');
        return false;
    }
    return true;
}

// Toggle sidebar on mobile
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('show');
}

// FORM SUBMISSION HANDLERS

// Handle form submission with AJAX
async function submitFormAjax(formId, endpoint) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrf_token]').value
            }
        });
        
        if (response.ok) {
            showAlert('Data saved successfully!', 'success');
            // Redirect or refresh
            setTimeout(() => location.reload(), 1500);
        } else {
            showAlert('Error saving data', 'danger');
        }
    } catch (error) {
        showAlert('Network error: ' + error.message, 'danger');
    }
}

// EVENT LISTENERS

document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle
    const darkModeButton = document.getElementById('darkModeToggle');
    if (darkModeButton) {
        darkModeButton.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', 
                document.body.classList.contains('dark-mode'));
        });
    }
    
    // Load dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
    
    // Confirm delete buttons
    const deleteButtons = document.querySelectorAll('[data-confirm="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            if (!confirm('Are you sure? This cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
});
```

### progress-dates.js (Period date auto-fill)

```javascript
// Auto-fill dates based on reporting period

document.addEventListener('DOMContentLoaded', function() {
    const periodSelect = document.getElementById('reporting_period');
    const startDateInput = document.getElementById('period_start_date');
    const endDateInput = document.getElementById('period_end_date');
    
    if (periodSelect) {
        periodSelect.addEventListener('change', function() {
            const today = new Date();
            let startDate, endDate;
            
            switch (this.value) {
                case 'daily':
                    startDate = today;
                    endDate = today;
                    break;
                    
                case 'weekly':
                    // Get last Monday
                    const day = today.getDate();
                    const diff = today.getDate() - today.getDay() + 1; // +1 for Monday
                    startDate = new Date(today.setDate(diff));
                    endDate = new Date();
                    break;
                    
                case 'monthly':
                    // First day of month
                    startDate = new Date(today.getFullYear(), today.getMonth(), 1);
                    endDate = new Date();
                    break;
            }
            
            // Format as YYYY-MM-DD
            const formatDate = (date) => {
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`;
            };
            
            startDateInput.value = formatDate(startDate);
            endDateInput.value = formatDate(endDate);
        });
    }
});
```

---

## 🔐 Encryption & Decryption Details

### How Encryption Works

```python
# FERNET ENCRYPTION (Symmetric, 256-bit AES)

from cryptography.fernet import Fernet
import base64

# Generate encryption key (only once!)
def generate_encryption_key():
    """Generate new encryption key"""
    key = Fernet.generate_key()
    # Returns: b'3d6pb0aScFkQw-HhigMmlwyYoF...' (44 bytes)
    # Store this in: encryption.key file
    # KEEP SAFE! If lost, data unrecoverable!
    return key

# Load encryption key
def load_encryption_key():
    """Load key from file"""
    try:
        with open('encryption.key', 'rb') as key_file:
            return key_file.read()
    except FileNotFoundError:
        # Auto-generate if missing
        key = generate_encryption_key()
        with open('encryption.key', 'wb') as key_file:
            key_file.write(key)
        return key

# Encrypt data
def encrypt(plaintext):
    """Encrypt text (plaintext → ciphertext)"""
    if not plaintext:
        return None
    
    key = load_encryption_key()
    cipher = Fernet(key)
    
    # Convert string to bytes
    plaintext_bytes = plaintext.encode('utf-8')
    
    # Encrypt
    ciphertext_bytes = cipher.encrypt(plaintext_bytes)
    
    # Convert to string for storage
    ciphertext_string = ciphertext_bytes.decode('utf-8')
    
    return ciphertext_string
    # Returns: 'gAAAAABh7_abc123xyz...' (long encrypted string)

# Decrypt data
def decrypt(ciphertext):
    """Decrypt text (ciphertext → plaintext)"""
    if not ciphertext:
        return None
    
    key = load_encryption_key()
    cipher = Fernet(key)
    
    try:
        # Convert string to bytes
        ciphertext_bytes = ciphertext.encode('utf-8')
        
        # Decrypt
        plaintext_bytes = cipher.decrypt(ciphertext_bytes)
        
        # Convert back to string
        plaintext_string = plaintext_bytes.decode('utf-8')
        
        return plaintext_string
    except Exception as e:
        # Decryption failed (wrong key, corrupted data, etc.)
        return None

# Use in SQLAlchemy model with property decorator
class ProgressUpdate(db.Model):
    completed_work_encrypted = db.Column(db.Text)  # Stored encrypted
    
    @property
    def completed_work(self):
        """Decrypt when accessed"""
        return decrypt(self.completed_work_encrypted)
    
    @completed_work.setter
    def completed_work(self, value):
        """Auto-encrypt when set"""
        self.completed_work_encrypted = encrypt(value)

# Usage in routes:
update = ProgressUpdate()
update.completed_work = "This is my work"  # Auto-encrypted
db.session.add(update)
db.session.commit()

# Later, when retrieved:
update = ProgressUpdate.query.get(1)
print(update.completed_work)  # Auto-decrypted!
# Output: "This is my work"
```

### Security Notes

```
KEY SECURITY:
✓ Encryption key is 256-bit (256 bits = 32 bytes = 44 base64 chars)
✓ Generated using cryptographically secure random
✓ Never hardcoded in source code
✓ Stored in: encryption.key (file, not version control)
✓ Backup: encryption.key.backup (keep in safe place)

IF KEY IS LOST:
✗ All encrypted data becomes unreadable
✗ Cannot recover without key
✗ Need database backup with original key
✗ ALWAYS backup encryption.key regularly!

ATTACKS IT PREVENTS:
✓ Database breach: Attacker sees only gibberish
✓ Accidental exposure: Data readable only with key
✓ Database admin snooping: Can't read encrypted fields

ATTACKS IT DOESN'T PREVENT:
✗ Man-in-the-middle (use HTTPS for that)
✗ Application-level attacks (SQL injection, XSS)
✗ Memory attacks (decrypted data in memory)
✗ Timing attacks on decryption (use constant-time checks)

BEST PRACTICES:
1. Use HTTPS in production (encrypts data in transit)
2. Backup encryption key regularly
3. Don't log encrypted data
4. Rotate key periodically (advanced)
5. Use environment variables for key (production)
6. Never commit encryption.key to git
7. Add encryption.key to .gitignore
```

---

**[PART 2 CONTINUES WITH REMAINING SECTIONS - Due to length, creating Part 3...]**

This manual has been split into 3 parts to cover EVERYTHING without forgetting anything:

**PART 1** ✅
- Environment Setup
- Configuration
- Every File
- Database Schema
- Every Route (45+)
- Every Form Field
- Permissions Matrix
- Security Comprehensive

**PART 2** ✅ (Current)
- Decorators & Middlewares
- Complete Models
- All Templates
- Static Files
- Error Codes
- API Reference
- Database Operations (CRUD)
- JavaScript Details
- Encryption Details

**PART 3** (Next)
- User Roles Detailed
- Complete Login Flow
- Common Errors & Fixes
- Performance Tips
- Backup & Restore
- Deployment Checklist
- Testing Guide  
- Complete Glossary

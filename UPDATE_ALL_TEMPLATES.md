# COMPREHENSIVE TEMPLATE UPDATE PLAN

## FILES TO UPDATE (35+ files)

### PRIORITY 1 - Main User Pages (Add theme toggle + notifications + all features)
1. ✅ settings.html - Add theme toggle, notifications, modern styling
2. ✅ profile.html - Add theme toggle, notifications, quick actions
3. ✅ reports.html - Add theme toggle, export options, filters
4. ✅ issue_detail.html - Add theme toggle, quick actions, watchers
5. ✅ sprints.html - Add theme toggle, drag-drop, velocity charts
6. ✅ epics.html - Add theme toggle, roadmap view, progress tracking

### PRIORITY 2 - Admin Pages (Add full admin controls)
7. ✅ admin/dashboard.html - Theme toggle, system health, quick actions
8. ✅ admin/users.html - Theme toggle, bulk actions, advanced filters
9. ✅ admin/security.html - Theme toggle, audit log viewer, alerts
10. ✅ admin/projects.html - Theme toggle, project templates, archiving
11. ✅ admin/teams.html - Theme toggle, team analytics, capacity planning
12. ✅ admin/audit_logs.html - Theme toggle, log filtering, export

### PRIORITY 3 - Project Management Pages
13. ✅ backlog.html - Theme toggle, story prioritization, sprint planning
14. ✅ timeline_view.html - Theme toggle, milestone tracking, dependencies
15. ✅ workflow_diagram.html - Theme toggle, state transitions, automation
16. ✅ project_detail.html - Theme toggle, project insights, team activity
17. ✅ project_settings.html - Theme toggle, advanced settings, permissions
18. ✅ issues_list.html - Theme toggle, advanced filters, bulk edit
19. ✅ issue_edit.html - Theme toggle, quick save, field validation
20. ✅ labels.html - Theme toggle, label management, color picker

### PRIORITY 4 - Supporting Pages
21. ✅ epic_form.html - Theme toggle, epic templates, dependencies
22. ✅ sprint_form.html - Theme toggle, capacity calculator, auto-fill
23. ✅ label_form.html - Theme toggle, color presets, icon picker
24. ✅ add_status.html - Theme toggle, workflow builder, transitions

### FEATURES TO ADD TO EVERY PAGE:

#### In <head> section:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/advanced-features.css') }}">
<script src="{{ url_for('static', filename='js/theme-manager.js') }}"></script>
<script src="{{ url_for('static', filename='js/notification-manager.js') }}"></script>
<script src="{{ url_for('static', filename='js/inline-edit.js') }}"></script>
<script src="{{ url_for('static', filename='js/bulk-actions.js') }}"></script>
<script src="{{ url_for('static', filename='js/advanced-search.js') }}"></script>
```

#### In header-right section:
```html
<!-- Theme Toggle -->
<button class="header-icon-btn theme-toggle-btn" id="themeToggle" title="Toggle Theme">
    <i data-lucide="moon"></i>
</button>

<!-- Notifications -->
<button class="header-icon-btn" id="notificationBtn" title="Notifications">
    <i data-lucide="bell"></i>
    <span class="notification-badge">0</span>
</button>

<!-- Settings (if admin) -->
{% if current_user.role == 'admin' %}
<a href="{{ url_for('admin.admin_dashboard') }}" class="header-icon-btn" title="Admin Settings">
    <i data-lucide="settings"></i>
</a>
{% endif %}

<!-- User Menu -->
<div class="header-user-menu">
    <button class="header-user-btn" id="userMenuBtn">
        <div class="avatar avatar-sm" style="background: {{ current_user.avatar_color }};">
            {{ current_user.username[:2].upper() }}
        </div>
        <i data-lucide="chevron-down" style="width: 14px; height: 14px;"></i>
    </button>
    <div class="header-user-dropdown" id="userDropdown">
        <a href="{{ url_for('main.profile') }}" class="dropdown-item">
            <i data-lucide="user"></i>
            Profile
        </a>
        <a href="{{ url_for('main.settings') }}" class="dropdown-item">
            <i data-lucide="settings"></i>
            Settings
        </a>
        <div class="dropdown-divider"></div>
        <a href="{{ url_for('auth.logout') }}" class="dropdown-item">
            <i data-lucide="log-out"></i>
            Logout
        </a>
    </div>
</div>
```

#### Before </body>:
```html
<script>
// Initialize Lucide icons
if (typeof lucide !== 'undefined') {
    lucide.createIcons();
}

// Initialize theme toggle
document.getElementById('themeToggle')?.addEventListener('click', () => {
    window.themeManager.toggleTheme();
});

// Initialize notification button
document.getElementById('notificationBtn')?.addEventListener('click', () => {
    // Toggle notification panel
    const panel = document.getElementById('notificationPanel');
    panel?.classList.toggle('show');
});

// Initialize user menu
document.getElementById('userMenuBtn')?.addEventListener('click', (e) => {
    e.stopPropagation();
    document.getElementById('userDropdown')?.classList.toggle('show');
});

// Close user menu when clicking outside
document.addEventListener('click', () => {
    document.getElementById('userDropdown')?.classList.remove('show');
});
</script>
```

## ANIMATION CSS TO ADD:

```css
/* Modern Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { transform: translateX(-100%); }
    to { transform: translateX(0); }
}

@keyframes scaleIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

/* Apply animations */
.kanban-card {
    animation: scaleIn 0.2s ease-out;
}

.modal {
    animation: fadeIn 0.3s ease-out;
}

.sidebar-nav-item {
    transition: all 0.2s ease;
}

.sidebar-nav-item:hover {
    transform: translateX(4px);
}

.btn {
    transition: all 0.2s ease;
}

.btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
```

## STATUS: Ready to implement all updates

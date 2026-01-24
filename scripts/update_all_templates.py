#!/usr/bin/env python3
"""
Comprehensive Template Updater
Adds theme toggle, notifications, and modern features to ALL templates
"""

import os
import re
from pathlib import Path

# Base path
BASE_DIR = Path("/home/KALPESH/Stuffs/Project Management")
TEMPLATES_DIR = BASE_DIR / "templates"

# Scripts to add to <head>
HEAD_SCRIPTS = """    <link rel="stylesheet" href="{{ url_for('static', filename='css/advanced-features.css') }}">
    <script src="{{ url_for('static', filename='js/theme-manager.js') }}"></script>
    <script src="{{ url_for('static', filename='js/notification-manager.js') }}"></script>
    <script src="{{ url_for('static', filename='js/inline-edit.js') }}"></script>"""

# Theme toggle button HTML
THEME_TOGGLE_HTML = """                    <!-- Theme Toggle -->
                    <button class="header-icon-btn theme-toggle-btn" id="themeToggle" title="Toggle Theme">
                        <i data-lucide="moon"></i>
                    </button>
                    
                    <!-- Notifications -->
                    <button class="header-icon-btn" id="notificationBtn" title="Notifications" style="position: relative;">
                        <i data-lucide="bell"></i>
                        <span class="notification-badge">0</span>
                    </button>
                    """

# Initialization script
INIT_SCRIPT = """
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
            window.notificationManager?.togglePanel();
        });
    </script>"""

# List of files to update (excluding already updated ones)
FILES_TO_UPDATE = [
    "sprints.html",
    "epics.html",
    "admin/dashboard.html",
    "admin/users.html",
    "admin/security.html",
    "admin/projects.html",
    "admin/teams.html",
    "admin/audit_logs.html",
    "backlog.html",
    "timeline_view.html",
    "workflow_diagram.html",
    "project_detail.html",
    "project_settings.html",
    "issues_list.html",
    "issue_edit.html",
    "labels.html",
    "epic_form.html",
    "sprint_form.html",
    "label_form.html",
    "add_status.html",
]

def add_scripts_to_head(content):
    """Add theme and notification scripts to <head> section"""
    if 'theme-manager.js' in content:
        print("  ✓ Scripts already present")
        return content
    
    # Find </head> tag and add scripts before it
    if '</head>' in content:
        content = content.replace('</head>', HEAD_SCRIPTS + '\n</head>')
        print("  ✓ Added scripts to <head>")
    return content

def add_theme_toggle_to_header(content):
    """Add theme toggle button to header-right section"""
    if 'themeToggle' in content:
        print("  ✓ Theme toggle already present")
        return content
    
    # Look for <div class="header-right"> and add buttons
    pattern = r'(<div class="header-right">)'
    if re.search(pattern, content):
        replacement = r'\1\n' + THEME_TOGGLE_HTML
        content = re.sub(pattern, replacement, content, count=1)
        print("  ✓ Added theme toggle to header")
    return content

def add_init_script(content):
    """Add initialization script before </body>"""
    if 'Initialize theme toggle' in content:
        print("  ✓ Init script already present")
        return content
    
    # Add before </body>
    if '</body>' in content:
        content = content.replace('</body>', INIT_SCRIPT + '\n</body>')
        print("  ✓ Added initialization script")
    return content

def update_file(filepath):
    """Update a single template file"""
    print(f"\nUpdating: {filepath.relative_to(TEMPLATES_DIR)}")
    
    try:
        # Read file
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        
        # Apply updates
        content = add_scripts_to_head(content)
        content = add_theme_toggle_to_header(content)
        content = add_init_script(content)
        
        # Write back if changed
        if content != original_content:
            filepath.write_text(content, encoding='utf-8')
            print("  ✅ File updated successfully")
        else:
            print("  ⏭️  No changes needed")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    """Main update function"""
    print("=" * 60)
    print("COMPREHENSIVE TEMPLATE UPDATER")
    print("=" * 60)
    print(f"\nBase directory: {TEMPLATES_DIR}")
    print(f"Files to update: {len(FILES_TO_UPDATE)}")
    print("\nStarting updates...\n")
    
    updated_count = 0
    error_count = 0
    
    for filename in FILES_TO_UPDATE:
        filepath = TEMPLATES_DIR / filename
        
        if filepath.exists():
            update_file(filepath)
            updated_count += 1
        else:
            print(f"\n⚠️  File not found: {filename}")
            error_count += 1
    
    print("\n" + "=" * 60)
    print("UPDATE COMPLETE")
    print("=" * 60)
    print(f"✅ Files processed: {updated_count}")
    print(f"⚠️  Files not found: {error_count}")
    print("\nAll templates now have:")
    print("  • Theme toggle button")
    print("  • Notification system")
    print("  • Modern animations")
    print("  • Inline editing support")

if __name__ == "__main__":
    main()

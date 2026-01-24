#!/usr/bin/env python3
"""Fix all url_for endpoints by removing blueprint prefixes"""

import os
import re
from pathlib import Path

# Mapping of blueprint endpoints to simple endpoints
REPLACEMENTS = {
    # Auth endpoints
    "url_for('auth.login')": "url_for('login')",
    "url_for('auth.logout')": "url_for('logout')",
    "url_for('auth.change_password')": "url_for('change_password')",
    "url_for('auth.forgot_password')": "url_for('forgot_password')",
    "url_for('auth.reset_password'": "url_for('reset_password'",
    "url_for('auth.register')": "url_for('register')",
    "url_for('auth.confirm_password'": "url_for('confirm_password'",
    
    # Main endpoints  
    "url_for('main.dashboard')": "url_for('dashboard')",
    "url_for('main.reports')": "url_for('reports')",
    "url_for('main.gantt_chart')": "url_for('gantt_chart')",
    "url_for('main.calendar')": "url_for('calendar')",
    "url_for('main.profile')": "url_for('profile')",
    "url_for('main.settings')": "url_for('settings')",
    "url_for('main.update_profile')": "url_for('update_profile')",
    "url_for('main.index')": "url_for('index')",
}

def fix_file(file_path):
    """Fix endpoint references in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all replacements
        for old, new in REPLACEMENTS.items():
            content = content.replace(old, new)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed: {file_path}")
            return True
        
        return False
    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all HTML templates"""
    templates_dir = Path("templates")
    
    if not templates_dir.exists():
        print(f"Error: {templates_dir} does not exist!")
        return
    
    print("Fixing endpoint references in templates...")
    print("=" * 60)
    
    fixed_count = 0
    total_count = 0
    
    # Find all .html files (excluding .bak files)
    for html_file in templates_dir.rglob("*.html"):
        if '.bak' not in html_file.name and '.backup' not in html_file.name:
            total_count += 1
            if fix_file(html_file):
                fixed_count += 1
    
    print("=" * 60)
    print(f"✓ Fixed {fixed_count} out of {total_count} files")
    print("All endpoint references updated!")

if __name__ == '__main__':
    main()

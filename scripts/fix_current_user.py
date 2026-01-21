#!/usr/bin/env python3
"""Fix current_user references in templates to add is_authenticated checks."""
import os
import re

TEMPLATES_DIR = "/home/KALPESH/Stuffs/Project Management/templates"

def fix_templates():
    """Fix all templates with current_user references."""
    patterns = [
        # Fix {{ current_user.username[:2].upper() }} 
        (r'\{\{ current_user\.username\[:2\]\.upper\(\) \}\}', 
         "{{ current_user.username[:2].upper() if current_user.is_authenticated else 'U' }}"),
        # Fix {{ current_user.username }} (but not already fixed)
        (r'\{\{ current_user\.username \}\}', 
         "{{ current_user.username if current_user.is_authenticated else 'User' }}"),
        # Fix {{ current_user.role.title() }} (but not already fixed)
        (r'\{\{ current_user\.role\.title\(\) \}\}',
         "{{ current_user.role.title() if current_user.is_authenticated and current_user.role else 'User' }}"),
        # Fix avatar_color or var()
        (r"\{\{ current_user\.avatar_color or 'var\(--primary-100\)' \}\}",
         "{{ current_user.avatar_color if current_user.is_authenticated else 'var(--primary-100)' }}"),
    ]
    
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        # Skip backup files
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for f in files:
            if not f.endswith('.html') or '.bak' in f or '.backup' in f or '.old' in f:
                continue
                
            filepath = os.path.join(root, f)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                original = content
                
                for pattern, replacement in patterns:
                    # Skip if already fixed
                    if 'is_authenticated' not in content or pattern in content:
                        content = re.sub(pattern, replacement, content)
                
                if content != original:
                    with open(filepath, 'w', encoding='utf-8') as file:
                        file.write(content)
                    print(f"Fixed: {filepath}")
                    
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    fix_templates()
    print("Done!")

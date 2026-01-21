#!/usr/bin/env python3
"""
Script to add Lucide CDN and initialization to templates that have data-lucide icons
but are missing the script initialization.
"""

import os
import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Lucide CDN link to add to head
LUCIDE_CDN = '<script src="https://unpkg.com/lucide@latest"></script>'

# Lucide initialization script
LUCIDE_INIT = '''<script>
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    });
</script>'''

def has_lucide_icons(content):
    """Check if file has Lucide icon references"""
    return 'data-lucide=' in content

def has_lucide_cdn(content):
    """Check if file already has Lucide CDN"""
    return 'lucide@' in content or 'lucide.js' in content

def has_lucide_init(content):
    """Check if file already has Lucide initialization"""
    return 'lucide.createIcons' in content

def add_lucide_to_file(filepath):
    """Add Lucide CDN and initialization to a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not has_lucide_icons(content):
        return False, "No Lucide icons found"
    
    modified = False
    
    # Add CDN to head if missing
    if not has_lucide_cdn(content):
        # Find </head> and add before it
        if '</head>' in content:
            content = content.replace('</head>', f'    {LUCIDE_CDN}\n</head>')
            modified = True
        # Or find {% block head %} end
        elif '{% endblock head %}' in content:
            content = content.replace('{% endblock head %}', f'{LUCIDE_CDN}\n{{% endblock head %}}')
            modified = True
    
    # Add initialization if missing
    if not has_lucide_init(content):
        # Find </body> and add before it
        if '</body>' in content:
            content = content.replace('</body>', f'{LUCIDE_INIT}\n</body>')
            modified = True
        # Or find {% endblock %} at end
        elif '{% endblock %}' in content:
            # Find the last endblock
            last_endblock = content.rfind('{% endblock %}')
            if last_endblock != -1:
                content = content[:last_endblock] + LUCIDE_INIT + '\n' + content[last_endblock:]
                modified = True
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, "Updated"
    
    return False, "Already has Lucide setup"

def main():
    print("=" * 60)
    print("Adding Lucide CDN and Initialization to Templates")
    print("=" * 60)
    print()
    
    updated = 0
    skipped = 0
    
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for filename in sorted(files):
            if filename.endswith('.html'):
                filepath = Path(root) / filename
                rel_path = filepath.relative_to(TEMPLATES_DIR)
                
                success, message = add_lucide_to_file(filepath)
                
                if success:
                    print(f"✓ {rel_path}: {message}")
                    updated += 1
                else:
                    if "No Lucide" in message:
                        skipped += 1
                    else:
                        print(f"  {rel_path}: {message}")
    
    print()
    print("=" * 60)
    print(f"Summary: {updated} files updated, {skipped} files skipped (no icons)")
    print("=" * 60)

if __name__ == "__main__":
    main()

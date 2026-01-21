#!/usr/bin/env python3
"""
Emoji to Lucide Icon Replacement Script

This script replaces emoji characters with professional Lucide icon markup
across all HTML templates in the project.

Usage: python scripts/replace_emojis.py
"""

import os
import re
from pathlib import Path

# Define emoji to Lucide icon mappings
EMOJI_MAPPINGS = {
    # Document/Chart related
    '📊': '<i data-lucide="bar-chart-2"></i>',
    '📈': '<i data-lucide="trending-up"></i>',
    '📉': '<i data-lucide="trending-down"></i>',
    '📋': '<i data-lucide="clipboard-list"></i>',
    '📁': '<i data-lucide="folder"></i>',
    '📂': '<i data-lucide="folder-open"></i>',
    '📄': '<i data-lucide="file-text"></i>',
    '📝': '<i data-lucide="edit"></i>',
    '📅': '<i data-lucide="calendar"></i>',
    '📆': '<i data-lucide="calendar-days"></i>',
    '📌': '<i data-lucide="pin"></i>',
    '📬': '<i data-lucide="mail"></i>',
    '📭': '<i data-lucide="mail"></i>',
    '📥': '<i data-lucide="download"></i>',
    '📤': '<i data-lucide="upload"></i>',
    
    # User related
    '👤': '<i data-lucide="user"></i>',
    '👥': '<i data-lucide="users"></i>',
    '👑': '<i data-lucide="crown"></i>',
    
    # Status/Alert related
    '⚠️': '<i data-lucide="alert-triangle"></i>',
    '⚠': '<i data-lucide="alert-triangle"></i>',
    '✅': '<i data-lucide="check-circle"></i>',
    '✓': '<i data-lucide="check"></i>',
    '❌': '<i data-lucide="x-circle"></i>',
    '⚡': '<i data-lucide="zap"></i>',
    '🚨': '<i data-lucide="alert-octagon"></i>',
    '🛑': '<i data-lucide="octagon"></i>',
    '🔴': '<i data-lucide="circle" style="color: var(--error-500);"></i>',
    '🟢': '<i data-lucide="circle" style="color: var(--success-500);"></i>',
    '🔵': '<i data-lucide="circle" style="color: var(--info-500);"></i>',
    '🟠': '<i data-lucide="circle" style="color: var(--warning-500);"></i>',
    
    # Lock/Security related
    '🔐': '<i data-lucide="lock"></i>',
    '🔒': '<i data-lucide="lock"></i>',
    '🔓': '<i data-lucide="unlock"></i>',
    '🔑': '<i data-lucide="key"></i>',
    '🛡️': '<i data-lucide="shield"></i>',
    '🛡': '<i data-lucide="shield"></i>',
    '🚫': '<i data-lucide="shield-off"></i>',
    
    # Navigation/Action related
    '🏠': '<i data-lucide="home"></i>',
    '🚀': '<i data-lucide="rocket"></i>',
    '💻': '<i data-lucide="laptop"></i>',
    '🎯': '<i data-lucide="target"></i>',
    '➕': '<i data-lucide="plus"></i>',
    '➡️': '<i data-lucide="arrow-right"></i>',
    '←': '<i data-lucide="arrow-left"></i>',
    '→': '<i data-lucide="arrow-right"></i>',
    '↪': '<i data-lucide="log-out"></i>',
    '↓': '<i data-lucide="arrow-down"></i>',
    '↑': '<i data-lucide="arrow-up"></i>',
    
    # Misc
    '💡': '<i data-lucide="lightbulb"></i>',
    '🧩': '<i data-lucide="puzzle"></i>',
    '☁️': '<i data-lucide="cloud"></i>',
    '🌐': '<i data-lucide="globe"></i>',
    '📷': '<i data-lucide="camera"></i>',
    '📱': '<i data-lucide="smartphone"></i>',
    '🏢': '<i data-lucide="building"></i>',
    '⏱️': '<i data-lucide="clock"></i>',
    '⏱': '<i data-lucide="clock"></i>',
    '⏸️': '<i data-lucide="pause"></i>',
    '⏸': '<i data-lucide="pause"></i>',
    '▶': '<i data-lucide="play"></i>',
    '🔄': '<i data-lucide="refresh-cw"></i>',
    '✏️': '<i data-lucide="edit-2"></i>',
    '🗑️': '<i data-lucide="trash-2"></i>',
    '💬': '<i data-lucide="message-circle"></i>',
    '🔗': '<i data-lucide="link"></i>',
    '✨': '<i data-lucide="sparkles"></i>',
    '🔍': '<i data-lucide="search"></i>',
    '📏': '<i data-lucide="ruler"></i>',
    '🦊': '<i data-lucide="globe"></i>',
    '🎫': '<i data-lucide="ticket"></i>',
    'ℹ️': '<i data-lucide="info"></i>',
    '☰': '<i data-lucide="menu"></i>',
    
    # Menu toggle
    '☰': '<i data-lucide="menu"></i>',
}


def find_templates(base_path: str) -> list:
    """Find all HTML templates in the project."""
    templates = []
    for root, dirs, files in os.walk(base_path):
        # Skip backup files and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('__') and d not in ['node_modules', '.git']]
        for file in files:
            if file.endswith('.html') and not file.endswith('.backup'):
                templates.append(os.path.join(root, file))
    return templates


def replace_emojis_in_file(filepath: str, dry_run: bool = False) -> dict:
    """Replace emojis in a single file and return statistics."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    replacements = {}
    
    for emoji, replacement in EMOJI_MAPPINGS.items():
        count = content.count(emoji)
        if count > 0:
            content = content.replace(emoji, replacement)
            replacements[emoji] = count
    
    if content != original_content and not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return replacements


def main():
    import sys
    
    # Check for dry run mode
    dry_run = '--dry-run' in sys.argv
    
    base_path = Path(__file__).parent.parent / 'templates'
    
    if not base_path.exists():
        print(f"Templates directory not found: {base_path}")
        return
    
    print("=" * 60)
    print("Emoji to Lucide Icon Replacement Script")
    print("=" * 60)
    print(f"\nMode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE (files will be modified)'}")
    print(f"Templates directory: {base_path}\n")
    
    templates = find_templates(str(base_path))
    print(f"Found {len(templates)} template files\n")
    
    total_replacements = 0
    files_modified = 0
    
    for template in templates:
        relative_path = os.path.relpath(template, base_path.parent)
        replacements = replace_emojis_in_file(template, dry_run)
        
        if replacements:
            files_modified += 1
            file_total = sum(replacements.values())
            total_replacements += file_total
            
            print(f"📄 {relative_path}")
            for emoji, count in replacements.items():
                print(f"   {emoji} → Lucide icon ({count}x)")
            print()
    
    print("=" * 60)
    print(f"Summary:")
    print(f"  - Files modified: {files_modified}")
    print(f"  - Total replacements: {total_replacements}")
    if dry_run:
        print(f"\n  Run without --dry-run to apply changes")
    print("=" * 60)


if __name__ == '__main__':
    main()

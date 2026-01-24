#!/usr/bin/env python3
"""Quick functionality test for the Flask application"""

import sys
import os

# Add project to path
sys.path.insert(0, '/home/KALPESH/Stuffs/Project Management')

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        import flask
        print("✓ Flask imported")
        import sqlalchemy
        print("✓ SQLAlchemy imported")
        from app import app
        print("✓ App imported")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_static_files():
    """Check if static files exist"""
    print("\nTesting static files...")
    base = '/home/KALPESH/Stuffs/Project Management/static'
    files = [
        'css/design-system.css',
        'css/advanced-features.css',
        'js/lucide.min.js',
        'js/theme-manager.js',
        'js/notification-manager.js',
        'js/drag-drop.js'
    ]
    
    all_exist = True
    for f in files:
        path = os.path.join(base, f)
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        status = "✓" if exists else "✗"
        print(f"{status} {f} ({size} bytes)")
        if not exists:
            all_exist = False
    
    return all_exist

def test_templates():
    """Check if templates exist"""
    print("\nTesting templates...")
    base = '/home/KALPESH/Stuffs/Project Management/templates'
    files = [
        'dashboard.html',
        'kanban_board.html',
        'calendar.html',
        'gantt_chart.html'
    ]
    
    all_exist = True
    for f in files:
        path = os.path.join(base, f)
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        print(f"{status} {f}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_js_content():
    """Check if JS files have required content"""
    print("\nChecking JavaScript content...")
    
    checks = [
        ('/home/KALPESH/Stuffs/Project Management/static/js/theme-manager.js', ['ThemeManager', 'toggleTheme', 'window.themeManager']),
        ('/home/KALPESH/Stuffs/Project Management/static/js/notification-manager.js', ['NotificationManager', 'addNotification', 'window.notificationManager']),
    ]
    
    all_good = True
    for filepath, keywords in checks:
        with open(filepath, 'r') as f:
            content = f.read()
        
        filename = os.path.basename(filepath)
        for keyword in keywords:
            if keyword in content:
                print(f"✓ {filename} contains '{keyword}'")
            else:
                print(f"✗ {filename} missing '{keyword}'")
                all_good = False
    
    return all_good

def main():
    print("="*60)
    print("FRONTEND FUNCTIONALITY TEST")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Static Files", test_static_files),
        ("Templates", test_templates),
        ("JavaScript Content", check_js_content)
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    print("="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())

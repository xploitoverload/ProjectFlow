#!/usr/bin/env python
"""
Test script to verify facial ID setup routes are properly registered
This demonstrates the fix for the 404 error on /secure-mgmt-{token}/setup-facial-id
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_blueprints():
    """Test that all blueprints including secure admin are registered"""
    from app import create_app
    
    print("=" * 70)
    print("FACIAL ID SETUP ROUTE REGISTRATION TEST")
    print("=" * 70)
    
    # Create app
    app = create_app()
    
    # Get hidden token
    hidden_token = app.config.get('HIDDEN_ADMIN_TOKEN')
    print(f"\n✓ Hidden Admin Token Generated: {hidden_token[:20]}...")
    
    # List all registered blueprints
    print(f"\n✓ Registered Blueprints ({len(app.blueprints)}):")
    for blueprint_name in app.blueprints.keys():
        print(f"  - {blueprint_name}")
    
    # Check if admin_secure is registered
    if 'admin_secure' in app.blueprints:
        print("\n✓ SUCCESS: admin_secure blueprint is registered!")
    else:
        print("\n✗ ERROR: admin_secure blueprint is NOT registered!")
        return False
    
    # Get all routes
    print("\n✓ Facial ID Routes Available:")
    facial_id_routes = []
    for rule in app.url_map.iter_rules():
        if 'secure-mgmt' in str(rule) and 'facial' in str(rule):
            facial_id_routes.append(str(rule))
            print(f"  - {rule}")
    
    if not facial_id_routes:
        print("\n✗ WARNING: No facial ID routes found!")
        return False
    
    # Verify key routes
    expected_routes = [
        f'/secure-mgmt-{hidden_token}/setup-facial-id',
        f'/secure-mgmt-{hidden_token}/facial-login',
        f'/secure-mgmt-{hidden_token}/facial-login-verify',
    ]
    
    print("\n✓ Checking Expected Routes:")
    all_found = True
    for expected in expected_routes:
        for rule in app.url_map.iter_rules():
            if expected == str(rule.rule):
                print(f"  ✓ {expected}")
                break
        else:
            print(f"  ✗ NOT FOUND: {expected}")
            all_found = False
    
    print("\n" + "=" * 70)
    if all_found:
        print("✓ ALL TESTS PASSED - Facial ID routes are properly registered!")
    else:
        print("✗ SOME ROUTES MISSING - Check routes.py configuration")
    print("=" * 70)
    
    return all_found

if __name__ == '__main__':
    try:
        success = test_blueprints()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

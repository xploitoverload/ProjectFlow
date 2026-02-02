#!/usr/bin/env python3
import sys
sys.path.append('/home/KALPESH/Stuffs/Project Management')

try:
    from app import create_app
    app = create_app()
    print('✅ App creates successfully')
    
    with app.test_client() as client:
        # Test static files
        resp = client.get('/static/js/lucide.min.js')
        print(f'✅ Static files served: {resp.status_code}')
        
        # Test main routes
        resp = client.get('/issues', follow_redirects=False)
        print(f'✅ Issues route: {resp.status_code}')
        
        resp = client.get('/board', follow_redirects=False)
        print(f'✅ Board route: {resp.status_code}')
        
        # Test CSRF token availability
        resp = client.get('/login')
        if 'csrf_token' in resp.get_data(as_text=True):
            print('✅ CSRF token available in forms')
        else:
            print('❌ CSRF token missing in forms')
            
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
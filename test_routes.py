#!/usr/bin/env python3
"""Test script to verify all the reported URLs are working."""

import sys
import os
sys.path.append('/home/KALPESH/Stuffs/Project Management')

from app import create_app
import requests
from time import sleep
import threading

def test_routes():
    """Test all the routes mentioned by the user."""
    
    # Create app and get test client
    app = create_app('development')
    
    # URLs to test
    urls_to_test = [
        '/issues',
        '/project/1/backlog', 
        '/project/1/kanban',
        '/board',
        '/search',
        '/analytics'
    ]
    
    print("Testing Flask application routes...")
    print("=" * 50)
    
    with app.test_client() as client:
        for url in urls_to_test:
            print(f"Testing: {url}")
            try:
                response = client.get(url)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ SUCCESS - Route is working")
                elif response.status_code == 302:
                    print(f"  ↗️  REDIRECT - Route works but redirects (likely needs login)")
                elif response.status_code == 404:
                    print(f"  ❌ NOT FOUND - Route not registered")
                elif response.status_code == 500:
                    print(f"  💥 ERROR - Server error in route handler")
                else:
                    print(f"  ⚠️  UNKNOWN - Status code: {response.status_code}")
                    
            except Exception as e:
                print(f"  💥 EXCEPTION - {str(e)}")
            
            print()
    
    print("=" * 50)
    print("Route testing completed!")

if __name__ == "__main__":
    test_routes()
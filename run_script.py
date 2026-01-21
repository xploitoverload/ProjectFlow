#!/usr/bin/env python
"""
Project Management System - Easy Start Script
This script checks for database and initializes it if needed, then starts the application.
"""

import os
import sys
from app import app
from models import db

def check_database():
    """Check if database exists and is initialized"""
    db_path = 'project_management.db'
    
    if not os.path.exists(db_path):
        print("=" * 60)
        print("Database not found! Initializing database...")
        print("=" * 60)
        
        # Import and run init_db
        from init_db import init_database
        init_database()
        
        print("\n" + "=" * 60)
        print("Database initialized successfully!")
        print("=" * 60)
        return True
    else:
        print("=" * 60)
        print("Database found. Starting application...")
        print("=" * 60)
        return False

def main():
    """Main function to run the application"""
    
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║     PROJECT MANAGEMENT SYSTEM - STARTUP SCRIPT         ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    # Check and initialize database if needed
    is_new = check_database()
    
    if is_new:
        print("\n📋 Login Credentials:")
        print("-" * 60)
        print("Admin:    username='admin'    password='admin123'")
        print("Employee: username='employee' password='emp123'")
        print("-" * 60)
    
    print("\n🚀 Starting Flask Application...")
    print("=" * 60)
    print("📍 Application will be available at: http://127.0.0.1:5000")
    print("=" * 60)
    print("\n⚠️  Press CTRL+C to stop the server\n")
    
    try:
        # Run the Flask app
        app.run(debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("🛑 Server stopped by user")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print("\n\n" + "=" * 60)
        print(f"❌ Error starting server: {e}")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()
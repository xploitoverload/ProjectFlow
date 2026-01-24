#!/usr/bin/env python3
"""
Database Migration: Add Notification Table
Adds the notification table for user notifications system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Notification
from app.services.notification_service import NotificationService

def migrate():
    """Run the migration"""
    app = create_app()
    
    with app.app_context():
        print("Starting migration: Add Notification table...")
        
        try:
            # Create the notification table
            print("Creating notification table...")
            db.create_all()
            print("✓ Notification table created successfully")
            
            # Get first user for sample notifications
            from models import User
            users = User.query.limit(3).all()
            
            if users:
                print(f"\nCreating sample notifications for {len(users)} user(s)...")
                for user in users:
                    NotificationService.create_sample_notifications(user.id)
                    print(f"✓ Created sample notifications for user: {user.username}")
            
            print("\n✓ Migration completed successfully!")
            print("\nNew features available:")
            print("  - User notifications system")
            print("  - Notification dropdown in header")
            print("  - Unread count badge")
            print("  - Mark as read/delete functionality")
            print("  - Auto-polling for new notifications")
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)

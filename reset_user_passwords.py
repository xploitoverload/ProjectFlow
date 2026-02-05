#!/usr/bin/env python3
"""
Reset all user passwords to 'admin123' for testing
This will properly hash all passwords in the database
"""

from app import create_app
from models import User, db
from werkzeug.security import generate_password_hash

app = create_app('development')

def reset_all_passwords():
    """Reset all user passwords to a default value with proper hashing"""
    
    with app.app_context():
        print("Resetting all user passwords...")
        print("=" * 60)
        
        users = User.query.all()
        
        if not users:
            print("No users found in database!")
            return
        
        # Default password for all users
        default_password = "admin123"
        
        for user in users:
            # Set password using proper hashing method
            user.password = generate_password_hash(default_password, method='pbkdf2:sha256:600000')
            print(f"✓ Reset password for user: {user.username} (ID: {user.id})")
        
        # Commit all changes
        try:
            db.session.commit()
            print("=" * 60)
            print(f"✅ Successfully reset passwords for {len(users)} users")
            print(f"\nDefault password for all users: '{default_password}'")
            print("\nYou can now login with:")
            for user in users:
                print(f"  - Username: {user.username}")
            print(f"  - Password: {default_password}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    reset_all_passwords()

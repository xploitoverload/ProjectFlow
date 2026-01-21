# fix_user_passwords.py
"""
This script will scan all users in the database and set a default password ('password') for any user whose password hash is empty or invalid.
"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def is_valid_hash(pw):
    return pw and pw.startswith('pbkdf2:sha')

def fix_passwords():
    with app.app_context():
        users = User.query.all()
        changed = 0
        for user in users:
            if not is_valid_hash(user.password):
                print(f"Fixing password for user: {user.username}")
                user.password = generate_password_hash('password')
                changed += 1
        if changed:
            db.session.commit()
            print(f"Fixed {changed} user(s). Default password is now 'password'.")
        else:
            print("All user passwords are valid.")

if __name__ == "__main__":
    fix_passwords()

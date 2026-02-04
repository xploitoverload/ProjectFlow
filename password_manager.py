#!/usr/bin/env python
"""
Password Management Script - Reset/Change user passwords
Only for admin use to manage user credentials
"""

from app import create_app
from models import User, db
import click
import sys

app = create_app('development')

@click.group()
def cli():
    """User Password Management Utility"""
    pass

@cli.command()
def list_users():
    """List all users in the system"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in the system.")
            return
        
        print("\n" + "="*100)
        print("USER LIST")
        print("="*100)
        print(f"{'ID':<4} | {'Username':<15} | {'Email':<25} | {'Role':<10} | {'Department':<15} | {'Status':<10}")
        print("-"*100)
        
        for user in users:
            email = user.email or "N/A"
            dept = user.department or "N/A"
            status = "✓ Active" if user.is_active else "✗ Inactive"
            
            print(f"{user.id:<4} | {user.username:<15} | {email:<25} | {user.role:<10} | {dept:<15} | {status:<10}")
        
        print("="*100 + "\n")

@cli.command()
@click.option('--username', prompt='Username', help='Username of the user')
@click.option('--password', prompt='New Password', hide_input=True, confirmation_prompt=True, help='New password for the user')
def reset_password(username, password):
    """Reset password for a specific user"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            click.echo(f"✗ Error: User '{username}' not found.", err=True)
            return
        
        if len(password) < 6:
            click.echo("✗ Error: Password must be at least 6 characters long.", err=True)
            return
        
        try:
            user.set_password(password)
            user.failed_login_attempts = 0  # Reset failed attempts
            user.is_active = True  # Unlock if locked
            db.session.commit()
            
            click.echo(f"\n✓ Password reset successful for user '{username}'")
            click.echo(f"  • Failed login attempts reset to 0")
            click.echo(f"  • Account unlocked if previously locked")
            click.echo(f"  • User can now login with new password\n")
        except Exception as e:
            db.session.rollback()
            click.echo(f"✗ Error: Failed to reset password - {str(e)}", err=True)

@cli.command()
@click.option('--username', prompt='Username', help='Username for the new user')
@click.option('--email', prompt='Email', help='Email address')
@click.option('--password', prompt='Password', hide_input=True, confirmation_prompt=True, help='Initial password')
@click.option('--role', type=click.Choice(['admin', 'developer', 'designer', 'manager', 'user']), 
              default='user', help='User role')
def create_user(username, email, password, role):
    """Create a new user account"""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            click.echo(f"✗ Error: User '{username}' already exists.", err=True)
            return
        
        existing_email = User.query.filter_by(email_encrypted=email).first()
        if existing_email:
            click.echo(f"✗ Error: Email '{email}' already in use.", err=True)
            return
        
        if len(password) < 6:
            click.echo("✗ Error: Password must be at least 6 characters long.", err=True)
            return
        
        try:
            new_user = User(
                username=username,
                email=email,
                role=role,
                is_active=True
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            click.echo(f"\n✓ User created successfully!")
            click.echo(f"  • Username: {username}")
            click.echo(f"  • Email: {email}")
            click.echo(f"  • Role: {role}")
            click.echo(f"  • Status: Active")
            click.echo(f"  • Can login immediately\n")
        except Exception as e:
            db.session.rollback()
            click.echo(f"✗ Error: Failed to create user - {str(e)}", err=True)

@cli.command()
@click.option('--username', prompt='Username', help='Username to deactivate')
def deactivate_user(username):
    """Deactivate a user account (prevent login)"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            click.echo(f"✗ Error: User '{username}' not found.", err=True)
            return
        
        if not user.is_active:
            click.echo(f"✗ User '{username}' is already deactivated.", err=True)
            return
        
        try:
            user.is_active = False
            db.session.commit()
            
            click.echo(f"\n✓ User '{username}' has been deactivated")
            click.echo(f"  • Cannot login until reactivated\n")
        except Exception as e:
            db.session.rollback()
            click.echo(f"✗ Error: Failed to deactivate user - {str(e)}", err=True)

@cli.command()
@click.option('--username', prompt='Username', help='Username to activate')
def activate_user(username):
    """Activate a deactivated user account"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            click.echo(f"✗ Error: User '{username}' not found.", err=True)
            return
        
        if user.is_active:
            click.echo(f"✗ User '{username}' is already active.", err=True)
            return
        
        try:
            user.is_active = True
            user.failed_login_attempts = 0  # Reset failed attempts too
            db.session.commit()
            
            click.echo(f"\n✓ User '{username}' has been activated")
            click.echo(f"  • Can now login\n")
        except Exception as e:
            db.session.rollback()
            click.echo(f"✗ Error: Failed to activate user - {str(e)}", err=True)

@cli.command()
@click.option('--username', prompt='Username', help='Username to check')
def check_user(username):
    """Check user details and account status"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            click.echo(f"✗ Error: User '{username}' not found.", err=True)
            return
        
        print("\n" + "="*60)
        print(f"USER DETAILS: {username}")
        print("="*60)
        print(f"ID:                    {user.id}")
        print(f"Username:              {user.username}")
        print(f"Email:                 {user.email or 'Not set'}")
        print(f"Full Name:             {user.full_name or 'Not set'}")
        print(f"Role:                  {user.role}")
        print(f"Department:            {user.department or 'Not assigned'}")
        print(f"Status:                {'🟢 Active' if user.is_active else '🔴 Inactive'}")
        print(f"Failed Login Attempts: {user.failed_login_attempts}/5")
        print(f"Created At:            {user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else 'N/A'}")
        print(f"Last Login:            {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
        
        if user.failed_login_attempts >= 5:
            print(f"\n⚠️  Account is LOCKED due to failed login attempts")
            print(f"   Run: python password_manager.py reset-password --username {username}")
            print(f"   to reset the password and unlock the account")
        
        print("="*60 + "\n")

@cli.command()
def unlock_all():
    """Unlock all locked accounts (reset failed login attempts)"""
    with app.app_context():
        locked_users = User.query.filter(User.failed_login_attempts >= 5).all()
        
        if not locked_users:
            click.echo("No locked accounts found.\n")
            return
        
        click.echo(f"\nFound {len(locked_users)} locked account(s):")
        for user in locked_users:
            click.echo(f"  • {user.username} ({user.failed_login_attempts} failed attempts)")
        
        if click.confirm("\nUnlock all accounts?"):
            try:
                for user in locked_users:
                    user.failed_login_attempts = 0
                db.session.commit()
                click.echo(f"\n✓ Successfully unlocked {len(locked_users)} account(s)\n")
            except Exception as e:
                db.session.rollback()
                click.echo(f"✗ Error: Failed to unlock accounts - {str(e)}", err=True)

@cli.command()
def reset_all_passwords():
    """Reset all passwords to default (password123) - DANGEROUS!"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            click.echo("No users found in the system.\n")
            return
        
        click.echo(f"\n⚠️  WARNING: This will reset {len(users)} user(s) to default password!")
        click.echo("   Users will be reset to: password123\n")
        
        if click.confirm("Are you absolutely sure? (type yes to confirm)"):
            try:
                for user in users:
                    user.set_password('password123')
                    user.failed_login_attempts = 0
                    user.is_active = True
                db.session.commit()
                
                click.echo(f"\n✓ Reset {len(users)} user(s) to default password")
                click.echo("  • Default password: password123")
                click.echo("  • All accounts unlocked\n")
            except Exception as e:
                db.session.rollback()
                click.echo(f"✗ Error: Failed to reset passwords - {str(e)}", err=True)

def main():
    """Main entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n✗ Operation cancelled by user")
        sys.exit(1)

if __name__ == '__main__':
    main()

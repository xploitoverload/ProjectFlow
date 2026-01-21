# app/services/user_service.py
"""
User Service
Handles user management business logic.
"""

from datetime import datetime
from app.utils.security import hash_password, log_security_event, sanitize_input, validate_email
from app.utils.validators import (
    validate_required, validate_length,
    validate_enum, ValidationError
)


class UserService:
    """Service for handling user operations."""
    
    VALID_ROLES = ['super_admin', 'admin', 'manager', 'employee', 'viewer']
    
    @staticmethod
    def create_user(username, email, password, role='employee', team_id=None, created_by=None):
        """
        Create a new user with validation.
        
        Returns:
            tuple: (success: bool, user: User or None, message: str)
        """
        from app.models import User, db
        from app.utils.security import validate_password_strength, validate_username
        
        try:
            # Validate inputs
            username = sanitize_input(validate_required(username, 'username'))
            validate_length(username, 'username', min_length=3, max_length=30)
            
            if not validate_username(username):
                return False, None, 'Invalid username format. Use 3-30 alphanumeric characters.'
            
            if not validate_email(email):
                return False, None, 'Invalid email format'
            
            is_strong, msg = validate_password_strength(password)
            if not is_strong:
                return False, None, msg
            
            if role not in UserService.VALID_ROLES:
                return False, None, f'Invalid role. Must be one of: {", ".join(UserService.VALID_ROLES)}'
            
            # Check for duplicate username
            if User.query.filter_by(username=username).first():
                return False, None, 'Username already exists'
            
            # Create user
            user = User(
                username=username,
                role=role,
                team_id=int(team_id) if team_id else None,
                avatar_color=UserService._generate_avatar_color()
            )
            user.email = email
            user.password = hash_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            log_security_event(
                'USER_CREATED',
                user_id=created_by,
                details=f'Created user: {username}, role: {role}',
                severity='INFO'
            )
            
            return True, user, 'User created successfully'
            
        except ValidationError as e:
            return False, None, str(e)
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error creating user: {str(e)}'
    
    @staticmethod
    def update_user(user_id, data, updated_by=None):
        """
        Update user information.
        
        Args:
            user_id: ID of user to update
            data: Dictionary with fields to update
            updated_by: ID of user making the update
            
        Returns:
            tuple: (success: bool, user: User or None, message: str)
        """
        from app.models import User, db
        
        try:
            user = User.query.get(user_id)
            if not user:
                return False, None, 'User not found'
            
            # Update allowed fields
            if 'email' in data:
                if not validate_email(data['email']):
                    return False, None, 'Invalid email format'
                user.email = data['email']
            
            if 'role' in data:
                if data['role'] not in UserService.VALID_ROLES:
                    return False, None, 'Invalid role'
                user.role = data['role']
            
            if 'team_id' in data:
                user.team_id = int(data['team_id']) if data['team_id'] else None
            
            if 'avatar_color' in data:
                user.avatar_color = data['avatar_color']
            
            db.session.commit()
            
            log_security_event(
                'USER_UPDATED',
                user_id=updated_by,
                details=f'Updated user: {user.username}',
                severity='INFO'
            )
            
            return True, user, 'User updated successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error updating user: {str(e)}'
    
    @staticmethod
    def delete_user(user_id, deleted_by=None):
        """
        Delete a user.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        from app.models import User, db
        
        try:
            user = User.query.get(user_id)
            if not user:
                return False, 'User not found'
            
            # Prevent self-deletion
            if deleted_by and user_id == deleted_by:
                return False, 'Cannot delete your own account'
            
            # Prevent deletion of last admin
            if user.role in ['admin', 'super_admin']:
                admin_count = User.query.filter(
                    User.role.in_(['admin', 'super_admin']),
                    User.id != user_id
                ).count()
                if admin_count == 0:
                    return False, 'Cannot delete the last administrator'
            
            username = user.username
            db.session.delete(user)
            db.session.commit()
            
            log_security_event(
                'USER_DELETED',
                user_id=deleted_by,
                details=f'Deleted user: {username}',
                severity='WARNING'
            )
            
            return True, 'User deleted successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error deleting user: {str(e)}'
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID."""
        from app.models import User
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_username(username):
        """Get user by username."""
        from app.models import User
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_all_users(include_deleted=False):
        """Get all users."""
        from app.models import User
        return User.query.all()
    
    @staticmethod
    def get_users_by_team(team_id):
        """Get all users in a team."""
        from app.models import User
        return User.query.filter_by(team_id=team_id).all()
    
    @staticmethod
    def get_users_by_role(role):
        """Get all users with a specific role."""
        from app.models import User
        return User.query.filter_by(role=role).all()
    
    @staticmethod
    def search_users(query, limit=20):
        """Search users by username or email."""
        from app.models import User
        
        search_term = f'%{query}%'
        return User.query.filter(
            User.username.ilike(search_term)
        ).limit(limit).all()
    
    @staticmethod
    def _generate_avatar_color():
        """Generate a random avatar color."""
        import random
        colors = [
            '#667eea', '#764ba2', '#6B8DD6', '#8E37D7',
            '#00C9FF', '#92FE9D', '#FF6B6B', '#4ECDC4',
            '#45B7D1', '#96CEB4', '#FFEAA7', '#DFE6E9'
        ]
        return random.choice(colors)
    
    @staticmethod
    def unlock_user(user_id, unlocked_by=None):
        """Unlock a locked user account."""
        from app.models import User, db
        
        user = User.query.get(user_id)
        if not user:
            return False, 'User not found'
        
        user.failed_login_attempts = 0
        db.session.commit()
        
        log_security_event(
            'USER_UNLOCKED',
            user_id=unlocked_by,
            details=f'Unlocked user: {user.username}',
            severity='INFO'
        )
        
        return True, 'User account unlocked'

# app/services/recent_items_service.py
"""
Recent Items Service
Handles tracking and retrieval of recently viewed items.
"""

from datetime import datetime
from flask import session
from app.models import RecentItem, StarredItem, db


class RecentItemsService:
    """Service for managing recently viewed items."""
    
    MAX_RECENT_ITEMS = 10
    
    @staticmethod
    def track_view(item_type, item_id, item_title, item_key=None):
        """
        Track a viewed item for the current user.
        Updates timestamp if already exists, adds new if not.
        Maintains max limit by removing oldest.
        
        Args:
            item_type: Type of item ('issue', 'project', 'board', 'sprint', 'epic')
            item_id: ID of the item
            item_title: Display title/name of the item
            item_key: Optional key for issues (e.g., PROJ-123)
        """
        user_id = session.get('user_id')
        if not user_id:
            return
        
        # Check if already exists
        existing = RecentItem.query.filter_by(
            user_id=user_id,
            item_type=item_type,
            item_id=item_id
        ).first()
        
        if existing:
            # Update timestamp
            existing.viewed_at = datetime.utcnow()
            existing.item_title = item_title  # Update title in case it changed
            existing.item_key = item_key
        else:
            # Create new entry
            new_item = RecentItem(
                user_id=user_id,
                item_type=item_type,
                item_id=item_id,
                item_title=item_title,
                item_key=item_key,
                viewed_at=datetime.utcnow()
            )
            db.session.add(new_item)
            
            # Clean up old items if exceeds max
            RecentItemsService._cleanup_old_items(user_id)
        
        db.session.commit()
    
    @staticmethod
    def _cleanup_old_items(user_id):
        """Remove oldest items if exceeds MAX_RECENT_ITEMS."""
        count = RecentItem.query.filter_by(user_id=user_id).count()
        
        if count >= RecentItemsService.MAX_RECENT_ITEMS:
            # Get items ordered by oldest first
            old_items = RecentItem.query.filter_by(user_id=user_id)\
                .order_by(RecentItem.viewed_at.asc())\
                .limit(count - RecentItemsService.MAX_RECENT_ITEMS + 1)\
                .all()
            
            for item in old_items:
                db.session.delete(item)
    
    @staticmethod
    def get_recent_items(user_id=None, limit=10):
        """
        Get recent items for a user.
        
        Args:
            user_id: User ID (defaults to current session user)
            limit: Maximum number of items to return
            
        Returns:
            List of RecentItem objects ordered by most recent first
        """
        if user_id is None:
            user_id = session.get('user_id')
        
        if not user_id:
            return []
        
        return RecentItem.query.filter_by(user_id=user_id)\
            .order_by(RecentItem.viewed_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_recent_by_type(item_type, user_id=None, limit=5):
        """Get recent items of a specific type."""
        if user_id is None:
            user_id = session.get('user_id')
        
        if not user_id:
            return []
        
        return RecentItem.query.filter_by(user_id=user_id, item_type=item_type)\
            .order_by(RecentItem.viewed_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def clear_recent_items(user_id=None):
        """Clear all recent items for a user."""
        if user_id is None:
            user_id = session.get('user_id')
        
        if not user_id:
            return
        
        RecentItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()


class StarredItemsService:
    """Service for managing starred/favorite items."""
    
    @staticmethod
    def toggle_star(item_type, item_id, item_title, item_key=None):
        """
        Toggle star status for an item.
        
        Returns:
            bool: True if now starred, False if unstarred
        """
        user_id = session.get('user_id')
        if not user_id:
            return False
        
        existing = StarredItem.query.filter_by(
            user_id=user_id,
            item_type=item_type,
            item_id=item_id
        ).first()
        
        if existing:
            # Unstar
            db.session.delete(existing)
            db.session.commit()
            return False
        else:
            # Star
            new_star = StarredItem(
                user_id=user_id,
                item_type=item_type,
                item_id=item_id,
                item_title=item_title,
                item_key=item_key,
                starred_at=datetime.utcnow()
            )
            db.session.add(new_star)
            db.session.commit()
            return True
    
    @staticmethod
    def is_starred(item_type, item_id, user_id=None):
        """Check if an item is starred."""
        if user_id is None:
            user_id = session.get('user_id')
        
        if not user_id:
            return False
        
        return StarredItem.query.filter_by(
            user_id=user_id,
            item_type=item_type,
            item_id=item_id
        ).first() is not None
    
    @staticmethod
    def get_starred_items(user_id=None):
        """Get all starred items for a user."""
        if user_id is None:
            user_id = session.get('user_id')
        
        if not user_id:
            return []
        
        return StarredItem.query.filter_by(user_id=user_id)\
            .order_by(StarredItem.starred_at.desc())\
            .all()
    
    @staticmethod
    def get_starred_by_type(item_type, user_id=None):
        """Get starred items of a specific type."""
        if user_id is None:
            user_id = session.get('user_id')
        
        if not user_id:
            return []
        
        return StarredItem.query.filter_by(user_id=user_id, item_type=item_type)\
            .order_by(StarredItem.starred_at.desc())\
            .all()

"""Push subscription management."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Subscription:
    """Push subscription."""
    id: str
    user_id: str
    endpoint: str
    auth: str
    p256dh: str
    created_at: str
    last_used: Optional[str] = None
    is_active: bool = True
    subscriptions_count: int = 0


class SubscriptionManager:
    """Manages push subscriptions."""
    
    def __init__(self):
        """Initialize subscription manager."""
        self.subscriptions: Dict[str, Subscription] = {}
        self.user_subscriptions: Dict[str, List[str]] = {}
        self.topic_subscriptions: Dict[str, List[str]] = {}
    
    def subscribe(self, user_id: str, endpoint: str, auth: str, p256dh: str) -> Subscription:
        """
        Subscribe user to push notifications.
        
        Args:
            user_id: User ID
            endpoint: Push endpoint
            auth: Auth secret
            p256dh: ECDH public key
            
        Returns:
            Subscription object
        """
        # Use endpoint hash as subscription ID
        subscription_id = f"sub_{hash(endpoint) % 10**8}"
        
        subscription = Subscription(
            id=subscription_id,
            user_id=user_id,
            endpoint=endpoint,
            auth=auth,
            p256dh=p256dh,
            created_at=datetime.now().isoformat(),
            is_active=True
        )
        
        self.subscriptions[subscription_id] = subscription
        
        # Add to user subscriptions
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = []
        self.user_subscriptions[user_id].append(subscription_id)
        
        logger.info(f"User {user_id} subscribed to push")
        return subscription
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from push notifications.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            True if successful
        """
        if subscription_id not in self.subscriptions:
            return False
        
        subscription = self.subscriptions[subscription_id]
        
        # Remove from subscriptions
        del self.subscriptions[subscription_id]
        
        # Remove from user subscriptions
        if subscription.user_id in self.user_subscriptions:
            self.user_subscriptions[subscription.user_id].remove(subscription_id)
        
        logger.info(f"Unsubscribed: {subscription_id}")
        return True
    
    def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """
        Get all subscriptions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of subscriptions
        """
        subscription_ids = self.user_subscriptions.get(user_id, [])
        return [
            self.subscriptions[sid] for sid in subscription_ids
            if sid in self.subscriptions and self.subscriptions[sid].is_active
        ]
    
    def subscribe_to_topic(self, subscription_id: str, topic: str) -> None:
        """
        Subscribe to a topic.
        
        Args:
            subscription_id: Subscription ID
            topic: Topic name
        """
        if topic not in self.topic_subscriptions:
            self.topic_subscriptions[topic] = []
        
        if subscription_id not in self.topic_subscriptions[topic]:
            self.topic_subscriptions[topic].append(subscription_id)
            logger.info(f"Subscription {subscription_id} subscribed to topic: {topic}")
    
    def unsubscribe_from_topic(self, subscription_id: str, topic: str) -> None:
        """
        Unsubscribe from a topic.
        
        Args:
            subscription_id: Subscription ID
            topic: Topic name
        """
        if topic in self.topic_subscriptions:
            if subscription_id in self.topic_subscriptions[topic]:
                self.topic_subscriptions[topic].remove(subscription_id)
                logger.info(f"Subscription {subscription_id} unsubscribed from topic: {topic}")
    
    def get_topic_subscriptions(self, topic: str) -> List[Subscription]:
        """
        Get all subscriptions for a topic.
        
        Args:
            topic: Topic name
            
        Returns:
            List of subscriptions
        """
        subscription_ids = self.topic_subscriptions.get(topic, [])
        return [
            self.subscriptions[sid] for sid in subscription_ids
            if sid in self.subscriptions and self.subscriptions[sid].is_active
        ]
    
    def mark_as_used(self, subscription_id: str) -> None:
        """
        Mark subscription as recently used.
        
        Args:
            subscription_id: Subscription ID
        """
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].last_used = datetime.now().isoformat()
    
    def deactivate_subscription(self, subscription_id: str) -> None:
        """
        Deactivate a subscription.
        
        Args:
            subscription_id: Subscription ID
        """
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].is_active = False
            logger.info(f"Subscription deactivated: {subscription_id}")
    
    def cleanup_inactive(self, days: int = 30) -> int:
        """
        Remove inactive subscriptions.
        
        Args:
            days: Days since last use to consider inactive
            
        Returns:
            Number of subscriptions removed
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        inactive_ids = []
        
        for sub_id, subscription in self.subscriptions.items():
            if subscription.last_used:
                last_used = datetime.fromisoformat(subscription.last_used)
                if last_used < cutoff:
                    inactive_ids.append(sub_id)
            elif datetime.fromisoformat(subscription.created_at) < cutoff:
                inactive_ids.append(sub_id)
        
        # Remove inactive
        for sub_id in inactive_ids:
            self.unsubscribe(sub_id)
        
        logger.info(f"Cleaned up {len(inactive_ids)} inactive subscriptions")
        return len(inactive_ids)
    
    def get_stats(self) -> Dict:
        """
        Get subscription statistics.
        
        Returns:
            Dictionary with stats
        """
        active_count = sum(1 for s in self.subscriptions.values() if s.is_active)
        inactive_count = len(self.subscriptions) - active_count
        
        return {
            'total_subscriptions': len(self.subscriptions),
            'active_subscriptions': active_count,
            'inactive_subscriptions': inactive_count,
            'users_subscribed': len(self.user_subscriptions),
            'topics': len(self.topic_subscriptions),
            'topic_names': list(self.topic_subscriptions.keys())
        }

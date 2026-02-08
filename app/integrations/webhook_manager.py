"""Webhook management for integrations."""

import logging
import hashlib
import hmac
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class WebhookEvent(Enum):
    """Webhook event types."""
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    ISSUE = "issue"
    RELEASE = "release"
    COMMENT = "comment"
    CUSTOM = "custom"


@dataclass
class Webhook:
    """Webhook configuration."""
    id: str
    url: str
    event: WebhookEvent
    secret: str
    active: bool = True
    created_at: str = None
    deliveries: int = 0
    failures: int = 0


class WebhookManager:
    """Manages webhooks for integrations."""
    
    def __init__(self):
        """Initialize webhook manager."""
        self.webhooks: Dict[str, Webhook] = {}
        self.handlers: Dict[WebhookEvent, List[Callable]] = {}
        self.delivery_log: List[Dict] = []
    
    def register_webhook(self, url: str, event: WebhookEvent,
                        secret: str = None) -> Webhook:
        """
        Register a webhook.
        
        Args:
            url: Webhook URL
            event: Event type
            secret: Webhook secret
            
        Returns:
            Webhook instance
        """
        webhook_id = f"webhook_{int(datetime.now().timestamp() * 1000)}"
        
        webhook = Webhook(
            id=webhook_id,
            url=url,
            event=event,
            secret=secret or self._generate_secret(),
            created_at=datetime.now().isoformat()
        )
        
        self.webhooks[webhook_id] = webhook
        logger.info(f"Webhook registered: {webhook_id}")
        
        return webhook
    
    def _generate_secret(self) -> str:
        """Generate secure webhook secret."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def register_handler(self, event: WebhookEvent, handler: Callable) -> None:
        """
        Register event handler.
        
        Args:
            event: Event type
            handler: Handler callable
        """
        if event not in self.handlers:
            self.handlers[event] = []
        
        self.handlers[event].append(handler)
        logger.info(f"Handler registered for {event.value}")
    
    def verify_signature(self, webhook_id: str, payload: str, 
                        signature: str) -> bool:
        """
        Verify webhook signature.
        
        Args:
            webhook_id: Webhook ID
            payload: Request payload
            signature: Request signature
            
        Returns:
            True if valid
        """
        if webhook_id not in self.webhooks:
            return False
        
        webhook = self.webhooks[webhook_id]
        expected_sig = hmac.new(
            webhook.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_sig, signature)
    
    async def deliver(self, webhook_id: str, payload: Dict) -> Dict:
        """
        Deliver webhook payload.
        
        Args:
            webhook_id: Webhook ID
            payload: Payload to deliver
            
        Returns:
            Delivery result
        """
        if webhook_id not in self.webhooks:
            return {'status': 'error', 'message': 'Webhook not found'}
        
        webhook = self.webhooks[webhook_id]
        
        try:
            # Execute handlers
            results = []
            if webhook.event in self.handlers:
                for handler in self.handlers[webhook.event]:
                    try:
                        result = await handler(payload) if \
                               hasattr(handler, '__await__') else handler(payload)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Handler error: {e}")
            
            webhook.deliveries += 1
            
            delivery = {
                'webhook_id': webhook_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'delivered',
                'handlers': len(results)
            }
            
            self.delivery_log.append(delivery)
            logger.info(f"Webhook delivered: {webhook_id}")
            
            return {'status': 'delivered', 'handlers_executed': len(results)}
        
        except Exception as e:
            webhook.failures += 1
            logger.error(f"Delivery error: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def deactivate_webhook(self, webhook_id: str) -> bool:
        """Deactivate webhook."""
        if webhook_id in self.webhooks:
            self.webhooks[webhook_id].active = False
            return True
        return False
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook."""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Get webhook manager statistics."""
        total_deliveries = sum(w.deliveries for w in self.webhooks.values())
        total_failures = sum(w.failures for w in self.webhooks.values())
        
        return {
            'total_webhooks': len(self.webhooks),
            'active_webhooks': sum(1 for w in self.webhooks.values() if w.active),
            'total_deliveries': total_deliveries,
            'total_failures': total_failures,
            'events_handled': len(self.handlers)
        }

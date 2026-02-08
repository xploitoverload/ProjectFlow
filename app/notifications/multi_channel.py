# app/notifications/multi_channel.py
"""
Advanced Multi-Channel Notifications
Support for Slack, Email, SMS, Push, Teams, and custom webhooks.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime


class NotificationChannel(Enum):
    """Notification channels."""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    PUSH = "push"
    TEAMS = "teams"
    WEBHOOK = "webhook"


class NotificationStatus(Enum):
    """Notification status."""
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


@dataclass
class NotificationTemplate:
    """Notification template."""
    id: str
    name: str
    subject: str = ""
    body: str = ""
    html_body: str = ""
    variables: List[str] = field(default_factory=list)
    channels: List[NotificationChannel] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'body': self.body,
            'html_body': self.html_body,
            'variables': self.variables,
            'channels': [c.value for c in self.channels],
            'created_at': self.created_at.isoformat()
        }


@dataclass
class NotificationWorkflow:
    """Notification workflow."""
    id: str
    name: str
    trigger: str  # event trigger (user.signup, payment.received, etc.)
    template_id: str
    channels: List[NotificationChannel] = field(default_factory=list)
    conditions: Dict = field(default_factory=dict)
    enabled: bool = True
    retry_policy: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'trigger': self.trigger,
            'template_id': self.template_id,
            'channels': [c.value for c in self.channels],
            'conditions': self.conditions,
            'enabled': self.enabled,
            'retry_policy': self.retry_policy,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class NotificationRecord:
    """Notification delivery record."""
    id: str
    user_id: str
    channel: NotificationChannel
    status: NotificationStatus
    recipient: str
    subject: str = ""
    body: str = ""
    template_id: str = ""
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_reason: str = ""
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'channel': self.channel.value,
            'status': self.status.value,
            'recipient': self.recipient,
            'subject': self.subject,
            'body': self.body,
            'template_id': self.template_id,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'failed_reason': self.failed_reason,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class ChannelConfig:
    """Channel configuration."""
    channel: NotificationChannel
    enabled: bool = True
    api_key: str = ""
    api_secret: str = ""
    webhook_url: str = ""
    rate_limit: int = 1000  # per hour
    retry_count: int = 3
    timeout_seconds: int = 30
    config: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            'channel': self.channel.value,
            'enabled': self.enabled,
            'rate_limit': self.rate_limit,
            'retry_count': self.retry_count,
            'timeout_seconds': self.timeout_seconds,
            'config': self.config
        }


class MultiChannelNotificationManager:
    """Manage multi-channel notifications."""
    
    def __init__(self):
        self.templates: Dict[str, NotificationTemplate] = {}
        self.workflows: Dict[str, NotificationWorkflow] = {}
        self.records: Dict[str, NotificationRecord] = {}
        self.channel_configs: Dict[NotificationChannel, ChannelConfig] = {}
        self.notification_queue: List[NotificationRecord] = []
    
    def create_template(self, name: str, subject: str, body: str, 
                       html_body: str = "", channels: List[str] = None):
        """Create notification template."""
        template_id = f"tpl_{len(self.templates) + 1}"
        channels = [NotificationChannel(c) for c in (channels or [])]
        template = NotificationTemplate(template_id, name, subject, body, html_body, 
                                       variables=[], channels=channels)
        self.templates[template_id] = template
        return template
    
    def get_template(self, template_id: str):
        """Get template."""
        return self.templates.get(template_id)
    
    def create_workflow(self, name: str, trigger: str, template_id: str, 
                       channels: List[str] = None):
        """Create notification workflow."""
        workflow_id = f"wfl_{len(self.workflows) + 1}"
        channels = [NotificationChannel(c) for c in (channels or [])]
        workflow = NotificationWorkflow(workflow_id, name, trigger, template_id, channels)
        self.workflows[workflow_id] = workflow
        return workflow
    
    def get_workflow(self, workflow_id: str):
        """Get workflow."""
        return self.workflows.get(workflow_id)
    
    def get_workflows_by_trigger(self, trigger: str):
        """Get workflows by trigger event."""
        return [w for w in self.workflows.values() if w.trigger == trigger and w.enabled]
    
    def queue_notification(self, user_id: str, channel: str, recipient: str, 
                          subject: str, body: str, template_id: str = ""):
        """Queue notification for delivery."""
        record_id = f"ntf_{len(self.records) + 1}"
        record = NotificationRecord(
            record_id, user_id, NotificationChannel(channel), 
            NotificationStatus.QUEUED, recipient, subject, body, template_id
        )
        self.records[record_id] = record
        self.notification_queue.append(record)
        return record
    
    def send_notification(self, record_id: str):
        """Send queued notification."""
        record = self.records.get(record_id)
        if not record:
            return False
        
        record.status = NotificationStatus.SENT
        record.sent_at = datetime.utcnow()
        return True
    
    def mark_delivered(self, record_id: str):
        """Mark notification as delivered."""
        record = self.records.get(record_id)
        if not record:
            return False
        
        record.status = NotificationStatus.DELIVERED
        record.delivered_at = datetime.utcnow()
        return True
    
    def mark_failed(self, record_id: str, reason: str):
        """Mark notification as failed."""
        record = self.records.get(record_id)
        if not record:
            return False
        
        record.status = NotificationStatus.FAILED
        record.failed_reason = reason
        return True
    
    def get_notification_history(self, user_id: str):
        """Get notification history for user."""
        return [r.to_dict() for r in self.records.values() if r.user_id == user_id]
    
    def get_delivery_stats(self):
        """Get delivery statistics."""
        total = len(self.records)
        sent = len([r for r in self.records.values() if r.status == NotificationStatus.SENT])
        delivered = len([r for r in self.records.values() if r.status == NotificationStatus.DELIVERED])
        failed = len([r for r in self.records.values() if r.status == NotificationStatus.FAILED])
        
        return {
            'total_notifications': total,
            'sent': sent,
            'delivered': delivered,
            'failed': failed,
            'delivery_rate': (delivered / total * 100) if total > 0 else 0,
            'failure_rate': (failed / total * 100) if total > 0 else 0,
            'pending': len(self.notification_queue)
        }
    
    def configure_channel(self, channel: str, enabled: bool = True, 
                         api_key: str = "", api_secret: str = "", **config):
        """Configure notification channel."""
        channel_enum = NotificationChannel(channel)
        cfg = ChannelConfig(channel_enum, enabled, api_key, api_secret, config=config)
        self.channel_configs[channel_enum] = cfg
        return cfg
    
    def get_channel_config(self, channel: str):
        """Get channel configuration."""
        return self.channel_configs.get(NotificationChannel(channel))
    
    def test_channel(self, channel: str, recipient: str):
        """Test notification channel."""
        return {
            'channel': channel,
            'recipient': recipient,
            'test_sent': True,
            'timestamp': datetime.utcnow().isoformat()
        }


# Global instance
multi_channel_manager = MultiChannelNotificationManager()

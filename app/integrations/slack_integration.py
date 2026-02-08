"""Slack integration module."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SlackConfig:
    """Slack configuration."""
    webhook_url: str
    bot_token: Optional[str] = None
    channel: str = "#general"
    enabled: bool = True


@dataclass
class SlackMessage:
    """Slack message."""
    id: str
    channel: str
    text: str
    timestamp: str
    user_id: Optional[str] = None
    thread_ts: Optional[str] = None


class SlackIntegration:
    """Slack integration manager."""
    
    def __init__(self):
        """Initialize Slack integration."""
        self.config: Optional[SlackConfig] = None
        self.is_configured = False
        self.sent_messages: List[SlackMessage] = []
        self.received_messages: List[SlackMessage] = []
    
    def configure(self, webhook_url: str, bot_token: str = None, 
                  channel: str = "#general") -> None:
        """
        Configure Slack integration.
        
        Args:
            webhook_url: Slack webhook URL
            bot_token: Optional bot token
            channel: Default channel
        """
        self.config = SlackConfig(
            webhook_url=webhook_url,
            bot_token=bot_token,
            channel=channel
        )
        self.is_configured = True
        logger.info("Slack integration configured")
    
    async def send_message(self, text: str, channel: str = None,
                          thread_ts: str = None, fields: Dict = None) -> Dict:
        """
        Send message to Slack.
        
        Args:
            text: Message text
            channel: Target channel
            thread_ts: Thread timestamp for replies
            fields: Rich message fields
            
        Returns:
            Send result
        """
        if not self.is_configured:
            return {'status': 'error', 'message': 'Slack not configured'}
        
        target_channel = channel or self.config.channel
        message_id = f"msg_{int(datetime.now().timestamp() * 1000)}"
        
        try:
            # In production, use slack_sdk
            message = SlackMessage(
                id=message_id,
                channel=target_channel,
                text=text,
                timestamp=datetime.now().isoformat(),
                thread_ts=thread_ts
            )
            
            self.sent_messages.append(message)
            logger.info(f"Slack message sent: {message_id}")
            
            return {
                'status': 'sent',
                'message_id': message_id,
                'channel': target_channel
            }
        
        except Exception as e:
            logger.error(f"Slack send error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def send_issue_notification(self, issue: Dict) -> Dict:
        """
        Send issue notification to Slack.
        
        Args:
            issue: Issue data
            
        Returns:
            Send result
        """
        text = f"🔔 *Issue #{issue.get('id')}*\n"
        text += f"Title: {issue.get('title')}\n"
        text += f"Status: {issue.get('status')}\n"
        text += f"Priority: {issue.get('priority')}"
        
        return await self.send_message(text)
    
    async def send_project_update(self, project: Dict) -> Dict:
        """Send project update to Slack."""
        text = f"📊 *Project Update: {project.get('name')}*\n"
        text += f"Progress: {project.get('completion_rate')}%\n"
        text += f"Team Size: {len(project.get('members', []))}"
        
        return await self.send_message(text)
    
    def get_stats(self) -> Dict:
        """Get Slack integration statistics."""
        return {
            'is_configured': self.is_configured,
            'sent_messages': len(self.sent_messages),
            'received_messages': len(self.received_messages),
            'default_channel': self.config.channel if self.config else None
        }

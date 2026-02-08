"""
Third-Party Integration Hub module.

Provides integrations with Slack, GitHub, Jira, and other services.
"""

from .slack_integration import SlackIntegration
from .github_integration import GitHubIntegration
from .jira_integration import JiraIntegration
from .webhook_manager import WebhookManager
from .sync_manager import SyncManager

# Global instances
slack_integration = SlackIntegration()
github_integration = GitHubIntegration()
jira_integration = JiraIntegration()
webhook_manager = WebhookManager()
sync_manager = SyncManager()

__all__ = [
    'SlackIntegration',
    'GitHubIntegration',
    'JiraIntegration',
    'WebhookManager',
    'SyncManager',
    'slack_integration',
    'github_integration',
    'jira_integration',
    'webhook_manager',
    'sync_manager',
]

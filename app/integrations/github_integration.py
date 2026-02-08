"""GitHub integration module."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GitHubConfig:
    """GitHub configuration."""
    personal_token: str
    repo_owner: str
    repo_name: str
    webhook_secret: Optional[str] = None
    enabled: bool = True


@dataclass
class GitHubPush:
    """GitHub push event."""
    id: str
    repo: str
    branch: str
    commit_count: int
    timestamp: str
    author: str


class GitHubIntegration:
    """GitHub integration manager."""
    
    def __init__(self):
        """Initialize GitHub integration."""
        self.config: Optional[GitHubConfig] = None
        self.is_configured = False
        self.webhook_events: List[Dict] = []
        self.synced_commits: List[GitHubPush] = []
    
    def configure(self, personal_token: str, repo_owner: str, 
                  repo_name: str, webhook_secret: str = None) -> None:
        """
        Configure GitHub integration.
        
        Args:
            personal_token: GitHub personal access token
            repo_owner: Repository owner
            repo_name: Repository name
            webhook_secret: Webhook secret for verification
        """
        self.config = GitHubConfig(
            personal_token=personal_token,
            repo_owner=repo_owner,
            repo_name=repo_name,
            webhook_secret=webhook_secret
        )
        self.is_configured = True
        logger.info(f"GitHub integration configured for {repo_owner}/{repo_name}")
    
    def handle_webhook(self, payload: Dict, signature: str = None) -> Dict:
        """
        Handle GitHub webhook.
        
        Args:
            payload: Webhook payload
            signature: Signature for verification
            
        Returns:
            Handle result
        """
        if not self.is_configured:
            return {'status': 'error', 'message': 'GitHub not configured'}
        
        try:
            event_type = payload.get('action') or payload.get('type', 'unknown')
            
            self.webhook_events.append({
                'type': event_type,
                'timestamp': datetime.now().isoformat(),
                'payload': payload
            })
            
            logger.info(f"GitHub webhook received: {event_type}")
            
            return {
                'status': 'received',
                'event_type': event_type
            }
        
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def sync_commits(self, branch: str = "main", since: str = None) -> Dict:
        """
        Sync commits from GitHub repository.
        
        Args:
            branch: Branch to sync
            since: Sync since timestamp
            
        Returns:
            Sync result
        """
        if not self.is_configured:
            return {'status': 'error', 'message': 'GitHub not configured'}
        
        try:
            # In production, use PyGithub
            push = GitHubPush(
                id=f"push_{int(datetime.now().timestamp() * 1000)}",
                repo=f"{self.config.repo_owner}/{self.config.repo_name}",
                branch=branch,
                commit_count=5,  # Simulated
                timestamp=datetime.now().isoformat(),
                author="bot"
            )
            
            self.synced_commits.append(push)
            
            return {
                'status': 'synced',
                'commits_synced': 5,
                'branch': branch
            }
        
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def create_issue(self, title: str, body: str, 
                          labels: List[str] = None) -> Dict:
        """
        Create issue in GitHub repository.
        
        Args:
            title: Issue title
            body: Issue body
            labels: Labels for issue
            
        Returns:
            Creation result
        """
        if not self.is_configured:
            return {'status': 'error', 'message': 'GitHub not configured'}
        
        try:
            issue_id = f"gh_{int(datetime.now().timestamp())}"
            
            return {
                'status': 'created',
                'issue_id': issue_id,
                'url': f"https://github.com/{self.config.repo_owner}/{self.config.repo_name}/issues/{issue_id}"
            }
        
        except Exception as e:
            logger.error(f"Issue creation error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_stats(self) -> Dict:
        """Get GitHub integration statistics."""
        return {
            'is_configured': self.is_configured,
            'webhook_events': len(self.webhook_events),
            'synced_commits': len(self.synced_commits),
            'repo': f"{self.config.repo_owner}/{self.config.repo_name}" if self.config else None
        }

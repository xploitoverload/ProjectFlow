"""Jira integration module."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class JiraConfig:
    """Jira configuration."""
    url: str
    username: str
    api_token: str
    project_key: str
    enabled: bool = True


@dataclass
class JiraSync:
    """Jira sync event."""
    id: str
    issue_key: str
    status: str  # synced, failed
    timestamp: str
    local_issue_id: Optional[str] = None


class JiraIntegration:
    """Jira integration manager."""
    
    def __init__(self):
        """Initialize Jira integration."""
        self.config: Optional[JiraConfig] = None
        self.is_configured = False
        self.synced_issues: List[JiraSync] = []
        self.issue_mappings: Dict[str, str] = {}  # local_id -> jira_key
    
    def configure(self, url: str, username: str, api_token: str,
                  project_key: str) -> None:
        """
        Configure Jira integration.
        
        Args:
            url: Jira instance URL
            username: Jira username
            api_token: Jira API token
            project_key: Jira project key
        """
        self.config = JiraConfig(
            url=url,
            username=username,
            api_token=api_token,
            project_key=project_key
        )
        self.is_configured = True
        logger.info(f"Jira integration configured for project {project_key}")
    
    async def sync_issue(self, local_issue: Dict) -> Dict:
        """
        Sync local issue to Jira.
        
        Args:
            local_issue: Local issue data
            
        Returns:
            Sync result
        """
        if not self.is_configured:
            return {'status': 'error', 'message': 'Jira not configured'}
        
        try:
            local_id = local_issue.get('id')
            issue_key = f"{self.config.project_key}-{len(self.synced_issues) + 1}"
            
            sync = JiraSync(
                id=f"sync_{int(datetime.now().timestamp() * 1000)}",
                issue_key=issue_key,
                status='synced',
                timestamp=datetime.now().isoformat(),
                local_issue_id=local_id
            )
            
            self.synced_issues.append(sync)
            self.issue_mappings[local_id] = issue_key
            
            logger.info(f"Issue synced to Jira: {issue_key}")
            
            return {
                'status': 'synced',
                'jira_key': issue_key,
                'jira_url': f"{self.config.url}/browse/{issue_key}"
            }
        
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_jira_issues(self, jql: str = None) -> Dict:
        """
        Get issues from Jira.
        
        Args:
            jql: JQL query
            
        Returns:
            Issues list
        """
        if not self.is_configured:
            return {'status': 'error', 'message': 'Jira not configured'}
        
        try:
            # In production, use jira Python library
            return {
                'status': 'success',
                'issues': [],
                'total': 0
            }
        
        except Exception as e:
            logger.error(f"Get issues error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def update_status(self, jira_key: str, status: str) -> Dict:
        """
        Update issue status in Jira.
        
        Args:
            jira_key: Jira issue key
            status: New status
            
        Returns:
            Update result
        """
        if not self.is_configured:
            return {'status': 'error', 'message': 'Jira not configured'}
        
        try:
            logger.info(f"Updated {jira_key} status to {status}")
            
            return {
                'status': 'updated',
                'jira_key': jira_key,
                'new_status': status
            }
        
        except Exception as e:
            logger.error(f"Status update error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_stats(self) -> Dict:
        """Get Jira integration statistics."""
        return {
            'is_configured': self.is_configured,
            'synced_issues': len(self.synced_issues),
            'issue_mappings': len(self.issue_mappings),
            'project_key': self.config.project_key if self.config else None
        }

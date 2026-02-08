# app/search/search_engine.py
"""
Full-text search and advanced filtering system.
Provides fast searching across projects, issues, and users.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import or_, and_, func

logger = logging.getLogger('search')


class SearchEngine:
    """Advanced search and filtering engine."""
    
    # Search result weights
    WEIGHTS = {
        'title_exact': 100,
        'title_partial': 50,
        'description': 20,
        'tags': 30,
        'username': 40
    }
    
    @staticmethod
    def search_issues(query: str, project_id: Optional[int] = None, 
                     status: Optional[str] = None, 
                     priority: Optional[str] = None,
                     assignee_id: Optional[int] = None,
                     limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search issues with advanced filtering.
        
        Args:
            query: Search text
            project_id: Filter by project
            status: Filter by status (open, closed, pending)
            priority: Filter by priority (low, medium, high, critical)
            assignee_id: Filter by assignee
            limit: Max results
        
        Returns:
            List of matching issues with score
        """
        from app.models import Issue, Project
        from app import db
        
        # Build base query
        q = Issue.query
        
        # Add filters
        if project_id:
            q = q.filter_by(project_id=project_id)
        
        if status:
            q = q.filter_by(status=status)
        
        if priority:
            q = q.filter_by(priority=priority)
        
        if assignee_id:
            q = q.filter_by(assigned_to=assignee_id)
        
        # Full-text search on title and description
        search_filter = or_(
            Issue.title.ilike(f'%{query}%'),
            Issue.description.ilike(f'%{query}%'),
            Issue.tags.ilike(f'%{query}%')
        )
        
        results = q.filter(search_filter).limit(limit).all()
        
        # Score and sort results
        scored_results = []
        for issue in results:
            score = SearchEngine._calculate_issue_score(issue, query)
            scored_results.append({
                'type': 'issue',
                'id': issue.id,
                'title': issue.title,
                'description': issue.description[:100] + '...' if len(issue.description or '') > 100 else issue.description,
                'project_id': issue.project_id,
                'status': issue.status,
                'priority': issue.priority,
                'score': score,
                'created_at': issue.created_at
            })
        
        # Sort by score descending
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        
        logger.debug(f"Issue search: '{query}' returned {len(scored_results)} results")
        
        return scored_results
    
    @staticmethod
    def search_projects(query: str, owner_id: Optional[int] = None,
                       status: Optional[str] = None,
                       limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search projects.
        
        Args:
            query: Search text
            owner_id: Filter by owner
            status: Filter by status (active, archived)
            limit: Max results
        
        Returns:
            List of matching projects with score
        """
        from app.models import Project
        
        q = Project.query
        
        if owner_id:
            q = q.filter_by(owner_id=owner_id)
        
        if status:
            q = q.filter_by(status=status)
        
        search_filter = or_(
            Project.name.ilike(f'%{query}%'),
            Project.description.ilike(f'%{query}%')
        )
        
        results = q.filter(search_filter).limit(limit).all()
        
        scored_results = []
        for project in results:
            score = SearchEngine._calculate_project_score(project, query)
            scored_results.append({
                'type': 'project',
                'id': project.id,
                'name': project.name,
                'description': project.description[:100] + '...' if len(project.description or '') > 100 else project.description,
                'owner_id': project.owner_id,
                'issue_count': len(project.issues) if hasattr(project, 'issues') else 0,
                'score': score,
                'created_at': project.created_at
            })
        
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        
        logger.debug(f"Project search: '{query}' returned {len(scored_results)} results")
        
        return scored_results
    
    @staticmethod
    def search_users(query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search users by username or email.
        
        Args:
            query: Search text
            limit: Max results
        
        Returns:
            List of matching users
        """
        from app.models import User
        
        search_filter = or_(
            User.username.ilike(f'%{query}%'),
            User.email.ilike(f'%{query}%')
        )
        
        results = User.query.filter(search_filter).limit(limit).all()
        
        scored_results = []
        for user in results:
            score = SearchEngine._calculate_user_score(user, query)
            scored_results.append({
                'type': 'user',
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'avatar': user.avatar if hasattr(user, 'avatar') else None,
                'score': score
            })
        
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        
        logger.debug(f"User search: '{query}' returned {len(scored_results)} results")
        
        return scored_results
    
    @staticmethod
    def global_search(query: str, search_types: List[str] = None, limit: int = 50) -> Dict[str, List]:
        """
        Global search across all types.
        
        Args:
            query: Search text
            search_types: List of types to search ('issues', 'projects', 'users')
            limit: Max results per type
        
        Returns:
            Dict with results grouped by type
        """
        if not search_types:
            search_types = ['issues', 'projects', 'users']
        
        results = {}
        
        if 'issues' in search_types:
            results['issues'] = SearchEngine.search_issues(query, limit=limit)
        
        if 'projects' in search_types:
            results['projects'] = SearchEngine.search_projects(query, limit=limit)
        
        if 'users' in search_types:
            results['users'] = SearchEngine.search_users(query, limit=limit)
        
        logger.info(f"Global search: '{query}' - Found {sum(len(v) for v in results.values())} total results")
        
        return results
    
    @staticmethod
    def _calculate_issue_score(issue, query: str) -> int:
        """Calculate relevance score for issue."""
        score = 0
        query_lower = query.lower()
        
        # Title matching
        if issue.title and query_lower in issue.title.lower():
            if issue.title.lower() == query_lower:
                score += SearchEngine.WEIGHTS['title_exact']
            else:
                score += SearchEngine.WEIGHTS['title_partial']
        
        # Description matching
        if issue.description and query_lower in issue.description.lower():
            score += SearchEngine.WEIGHTS['description']
        
        # Tags matching
        if hasattr(issue, 'tags') and issue.tags and query_lower in (issue.tags or '').lower():
            score += SearchEngine.WEIGHTS['tags']
        
        # Boost for recent issues
        if hasattr(issue, 'created_at') and issue.created_at:
            days_old = (datetime.now() - issue.created_at).days
            if days_old < 7:
                score += 10
            elif days_old < 30:
                score += 5
        
        # Boost for priority
        priority_boost = {
            'critical': 15,
            'high': 10,
            'medium': 5,
            'low': 0
        }
        if hasattr(issue, 'priority') and issue.priority:
            score += priority_boost.get(issue.priority, 0)
        
        return score
    
    @staticmethod
    def _calculate_project_score(project, query: str) -> int:
        """Calculate relevance score for project."""
        score = 0
        query_lower = query.lower()
        
        # Name matching
        if project.name and query_lower in project.name.lower():
            if project.name.lower() == query_lower:
                score += 80
            else:
                score += 60
        
        # Description matching
        if project.description and query_lower in project.description.lower():
            score += 20
        
        # Boost recent projects
        if hasattr(project, 'created_at') and project.created_at:
            days_old = (datetime.now() - project.created_at).days
            if days_old < 7:
                score += 10
        
        return score
    
    @staticmethod
    def _calculate_user_score(user, query: str) -> int:
        """Calculate relevance score for user."""
        score = 0
        query_lower = query.lower()
        
        # Username exact match
        if user.username and user.username.lower() == query_lower:
            score += SearchEngine.WEIGHTS['username']
        elif user.username and query_lower in user.username.lower():
            score += SearchEngine.WEIGHTS['username'] // 2
        
        # Email matching
        if user.email and query_lower in user.email.lower():
            score += 20
        
        return score


class FilterBuilder:
    """Helper for building complex filters."""
    
    def __init__(self):
        """Initialize filter builder."""
        self.filters = []
    
    def add_status_filter(self, status: str) -> 'FilterBuilder':
        """Add status filter."""
        self.filters.append(('status', status))
        return self
    
    def add_priority_filter(self, priority: str) -> 'FilterBuilder':
        """Add priority filter."""
        self.filters.append(('priority', priority))
        return self
    
    def add_assignee_filter(self, assignee_id: int) -> 'FilterBuilder':
        """Add assignee filter."""
        self.filters.append(('assignee_id', assignee_id))
        return self
    
    def add_date_range_filter(self, start_date, end_date) -> 'FilterBuilder':
        """Add date range filter."""
        self.filters.append(('date_range', (start_date, end_date)))
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build filter dict."""
        return dict(self.filters)
    
    def apply(self, query, model):
        """Apply filters to SQLAlchemy query."""
        for filter_name, filter_value in self.filters:
            if filter_name == 'date_range':
                start, end = filter_value
                query = query.filter(model.created_at.between(start, end))
            else:
                query = query.filter(getattr(model, filter_name) == filter_value)
        
        return query


# Saved searches
class SavedSearch:
    """Manage saved search queries."""
    
    _searches = {}
    
    @staticmethod
    def save(name: str, query: str, filters: Dict[str, Any]) -> bool:
        """Save a search."""
        SavedSearch._searches[name] = {
            'query': query,
            'filters': filters,
            'created_at': datetime.now()
        }
        logger.debug(f"Saved search: '{name}'")
        return True
    
    @staticmethod
    def get(name: str) -> Optional[Dict]:
        """Get saved search."""
        return SavedSearch._searches.get(name)
    
    @staticmethod
    def list_all() -> Dict[str, Any]:
        """List all saved searches."""
        return SavedSearch._searches
    
    @staticmethod
    def delete(name: str) -> bool:
        """Delete saved search."""
        if name in SavedSearch._searches:
            del SavedSearch._searches[name]
            logger.debug(f"Deleted search: '{name}'")
            return True
        return False

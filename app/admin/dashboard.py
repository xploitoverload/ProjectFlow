# app/admin/dashboard.py
"""
Admin dashboard and management utilities.
Provides analytics, user management, system monitoring.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger('admin')


class DashboardMetrics:
    """Collect and calculate dashboard metrics."""
    
    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """
        Get overall system statistics.
        
        Returns:
            System statistics dict
        """
        # In production, would query database
        return {
            'total_users': 0,
            'active_users_today': 0,
            'total_projects': 0,
            'total_issues': 0,
            'total_issues_open': 0,
            'total_issues_closed': 0,
            'avg_issue_completion_time': 0,  # in days
            'system_uptime_hours': 0
        }
    
    @staticmethod
    def get_user_stats(days: int = 30) -> Dict[str, Any]:
        """
        Get user activity statistics.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            User statistics
        """
        return {
            'new_users': 0,
            'active_users': 0,
            'inactive_users': 0,
            'users_by_role': {},
            'most_active_users': [],
            'user_growth': []  # Timeline of user growth
        }
    
    @staticmethod
    def get_project_stats(days: int = 30) -> Dict[str, Any]:
        """
        Get project statistics.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Project statistics
        """
        return {
            'total_projects': 0,
            'new_projects': 0,
            'completed_projects': 0,
            'active_projects': 0,
            'projects_by_status': {},
            'avg_issues_per_project': 0,
            'most_active_projects': []
        }
    
    @staticmethod
    def get_issue_stats(days: int = 30) -> Dict[str, Any]:
        """
        Get issue statistics.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Issue statistics
        """
        return {
            'total_issues': 0,
            'new_issues': 0,
            'resolved_issues': 0,
            'overdue_issues': 0,
            'issues_by_status': {},
            'issues_by_priority': {},
            'avg_resolution_time': 0,  # in hours
            'resolution_rate': 0  # percentage
        }
    
    @staticmethod
    def get_performance_metrics() -> Dict[str, Any]:
        """
        Get system performance metrics.
        
        Returns:
            Performance data
        """
        return {
            'api_response_time_avg': 0,  # in ms
            'api_response_time_p95': 0,
            'api_response_time_p99': 0,
            'error_rate': 0,  # percentage
            'cache_hit_rate': 0,  # percentage
            'database_query_time_avg': 0,  # in ms
            'request_count_last_hour': 0
        }


class UserManager:
    """Manage users from admin panel."""
    
    _users = {}
    
    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        """Get all users."""
        return list(UserManager._users.values())
    
    @staticmethod
    def get_user(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        return UserManager._users.get(user_id)
    
    @staticmethod
    def update_user_role(user_id: int, role: str) -> bool:
        """
        Update user role.
        
        Args:
            user_id: User ID
            role: New role (admin, moderator, user)
        
        Returns:
            Success status
        """
        if user_id not in UserManager._users:
            return False
        
        valid_roles = ['admin', 'moderator', 'user']
        if role not in valid_roles:
            return False
        
        UserManager._users[user_id]['role'] = role
        logger.info(f"User {user_id} role changed to {role}")
        return True
    
    @staticmethod
    def suspend_user(user_id: int, reason: str = "") -> bool:
        """Suspend user account."""
        if user_id not in UserManager._users:
            return False
        
        UserManager._users[user_id]['suspended'] = True
        UserManager._users[user_id]['suspension_reason'] = reason
        UserManager._users[user_id]['suspended_at'] = datetime.now()
        
        logger.warning(f"User {user_id} suspended: {reason}")
        return True
    
    @staticmethod
    def unsuspend_user(user_id: int) -> bool:
        """Unsuspend user account."""
        if user_id not in UserManager._users:
            return False
        
        UserManager._users[user_id]['suspended'] = False
        UserManager._users[user_id]['suspension_reason'] = ""
        
        logger.info(f"User {user_id} unsuspended")
        return True
    
    @staticmethod
    def reset_user_password(user_id: int) -> Optional[str]:
        """
        Reset user password and return temporary password.
        
        Returns:
            Temporary password
        """
        if user_id not in UserManager._users:
            return None
        
        import secrets
        temp_password = secrets.token_urlsafe(12)
        UserManager._users[user_id]['password_reset_required'] = True
        
        logger.info(f"Password reset for user {user_id}")
        return temp_password
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete user account."""
        if user_id not in UserManager._users:
            return False
        
        del UserManager._users[user_id]
        logger.warning(f"User {user_id} deleted")
        return True


class SystemMonitor:
    """Monitor system health and performance."""
    
    _metrics_history = defaultdict(list)
    
    @staticmethod
    def record_request(endpoint: str, method: str, response_time: float, 
                      status_code: int):
        """Record API request metric."""
        metric = {
            'timestamp': datetime.now(),
            'endpoint': endpoint,
            'method': method,
            'response_time': response_time,
            'status_code': status_code
        }
        SystemMonitor._metrics_history['requests'].append(metric)
        
        # Keep only last 1000 metrics
        if len(SystemMonitor._metrics_history['requests']) > 1000:
            SystemMonitor._metrics_history['requests'].pop(0)
    
    @staticmethod
    def record_database_query(query_type: str, execution_time: float):
        """Record database query metric."""
        metric = {
            'timestamp': datetime.now(),
            'type': query_type,
            'execution_time': execution_time
        }
        SystemMonitor._metrics_history['queries'].append(metric)
        
        if len(SystemMonitor._metrics_history['queries']) > 1000:
            SystemMonitor._metrics_history['queries'].pop(0)
    
    @staticmethod
    def record_cache_hit(hit: bool):
        """Record cache hit/miss."""
        status = 'hit' if hit else 'miss'
        metric = {
            'timestamp': datetime.now(),
            'status': status
        }
        SystemMonitor._metrics_history['cache'].append(metric)
        
        if len(SystemMonitor._metrics_history['cache']) > 1000:
            SystemMonitor._metrics_history['cache'].pop(0)
    
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        """Get system health status."""
        health = {
            'status': 'healthy',
            'checks': {
                'database': True,
                'cache': True,
                'api': True,
                'logging': True
            },
            'timestamp': datetime.now().isoformat(),
            'issues': []
        }
        
        # Check metrics for issues
        requests = SystemMonitor._metrics_history.get('requests', [])
        if requests:
            last_hour = datetime.now() - timedelta(hours=1)
            recent = [r for r in requests if r['timestamp'] > last_hour]
            
            errors = [r for r in recent if r['status_code'] >= 500]
            if len(errors) > 10:
                health['checks']['api'] = False
                health['issues'].append(f"High error rate: {len(errors)} errors in last hour")
            
            avg_response = sum(r['response_time'] for r in recent) / len(recent) if recent else 0
            if avg_response > 1000:  # > 1 second
                health['issues'].append(f"Slow API response: {avg_response:.0f}ms average")
        
        # Set overall status
        if not all(health['checks'].values()):
            health['status'] = 'degraded'
        
        return health
    
    @staticmethod
    def get_metrics_summary(hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for time period."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        summary = {
            'requests': 0,
            'avg_response_time': 0,
            'error_rate': 0,
            'cache_hit_rate': 0,
            'total_errors': 0
        }
        
        # Analyze requests
        requests = [r for r in SystemMonitor._metrics_history.get('requests', [])
                   if r['timestamp'] > cutoff]
        if requests:
            summary['requests'] = len(requests)
            summary['avg_response_time'] = sum(r['response_time'] for r in requests) / len(requests)
            errors = sum(1 for r in requests if r['status_code'] >= 400)
            summary['error_rate'] = (errors / len(requests)) * 100
            summary['total_errors'] = errors
        
        # Analyze cache
        cache = [c for c in SystemMonitor._metrics_history.get('cache', [])
                if c['timestamp'] > cutoff]
        if cache:
            hits = sum(1 for c in cache if c['status'] == 'hit')
            summary['cache_hit_rate'] = (hits / len(cache)) * 100
        
        return summary


class AuditLogger:
    """Log admin actions for compliance."""
    
    _audit_log = []
    
    @staticmethod
    def log_action(admin_id: int, action: str, target: str, 
                  details: str = "", status: str = "success"):
        """
        Log admin action.
        
        Args:
            admin_id: Admin user ID
            action: Action type (create, update, delete, suspend, etc.)
            target: Target resource (user, project, issue, etc.)
            details: Additional details
            status: Action status (success, failed)
        """
        entry = {
            'timestamp': datetime.now(),
            'admin_id': admin_id,
            'action': action,
            'target': target,
            'details': details,
            'status': status,
            'ip_address': None  # Would get from request
        }
        
        AuditLogger._audit_log.append(entry)
        
        # Keep last 10000 entries
        if len(AuditLogger._audit_log) > 10000:
            AuditLogger._audit_log.pop(0)
        
        logger.info(f"Audit: {action} on {target} by admin {admin_id}: {status}")
    
    @staticmethod
    def get_audit_log(days: int = 30, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries."""
        cutoff = datetime.now() - timedelta(days=days)
        entries = [e for e in AuditLogger._audit_log if e['timestamp'] > cutoff]
        return entries[-limit:]  # Return most recent
    
    @staticmethod
    def get_user_actions(user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get actions by specific user."""
        cutoff = datetime.now() - timedelta(days=days)
        return [e for e in AuditLogger._audit_log 
                if e['admin_id'] == user_id and e['timestamp'] > cutoff]

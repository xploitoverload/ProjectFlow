# app/services/audit_service.py
"""
Audit Service
Handles security auditing and activity logging.
"""

from datetime import datetime, timedelta
from app.utils.security import get_client_ip


class AuditService:
    """Service for handling audit logs and security monitoring."""
    
    # Event severity levels
    SEVERITY_INFO = 'INFO'
    SEVERITY_WARNING = 'WARNING'
    SEVERITY_ERROR = 'ERROR'
    SEVERITY_CRITICAL = 'CRITICAL'
    
    # Event categories
    CATEGORY_AUTH = 'AUTHENTICATION'
    CATEGORY_ACCESS = 'ACCESS_CONTROL'
    CATEGORY_DATA = 'DATA_MODIFICATION'
    CATEGORY_SECURITY = 'SECURITY_EVENT'
    CATEGORY_SYSTEM = 'SYSTEM'
    
    @staticmethod
    def log_event(action, user_id=None, details=None, severity='INFO', category='SYSTEM'):
        """
        Log an audit event.
        
        Args:
            action: The action that occurred
            user_id: ID of the user who performed the action
            details: Additional details about the event
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
            category: Event category
            
        Returns:
            AuditLog: The created audit log entry
        """
        from app.models import AuditLog, db
        from flask import request
        
        try:
            audit = AuditLog(
                user_id=user_id,
                action=f"{category}:{action}",
                ip_address=get_client_ip()
            )
            
            # Add details including severity and user agent
            full_details = {
                'severity': severity,
                'category': category,
                'details': details,
                'user_agent': request.headers.get('User-Agent', 'Unknown')[:200] if request else None,
                'endpoint': request.endpoint if request else None
            }
            
            audit.details = str(full_details)
            
            db.session.add(audit)
            db.session.commit()
            
            return audit
            
        except Exception as e:
            db.session.rollback()
            # Log to file as fallback
            import logging
            logging.error(f"Failed to log audit event: {action} - {str(e)}")
            return None
    
    @staticmethod
    def get_recent_events(limit=100, user_id=None, category=None, severity=None):
        """Get recent audit events with optional filtering."""
        from app.models import AuditLog
        
        query = AuditLog.query.order_by(AuditLog.timestamp.desc())
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if category:
            query = query.filter(AuditLog.action.like(f'{category}:%'))
        
        if severity:
            query = query.filter(AuditLog.details_encrypted.like(f'%{severity}%'))
        
        return query.limit(limit).all()
    
    @staticmethod
    def get_security_events(hours=24):
        """Get security-related events from the last N hours."""
        from app.models import AuditLog
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        security_actions = [
            'LOGIN_FAILED',
            'LOGIN_ATTEMPT_LOCKED',
            'UNAUTHORIZED_ACCESS',
            'RATE_LIMIT_EXCEEDED',
            'CSRF_TOKEN_INVALID',
            'SESSION_HIJACK_ATTEMPT',
            'SQL_INJECTION_ATTEMPT',
            'XSS_ATTEMPT'
        ]
        
        events = AuditLog.query.filter(
            AuditLog.timestamp >= cutoff
        ).order_by(AuditLog.timestamp.desc()).all()
        
        return [e for e in events if any(action in e.action for action in security_actions)]
    
    @staticmethod
    def get_failed_logins(hours=24):
        """Get failed login attempts from the last N hours."""
        from app.models import AuditLog
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        return AuditLog.query.filter(
            AuditLog.action.like('%LOGIN_FAILED%'),
            AuditLog.timestamp >= cutoff
        ).order_by(AuditLog.timestamp.desc()).all()
    
    @staticmethod
    def get_user_activity(user_id, days=30):
        """Get activity history for a specific user."""
        from app.models import AuditLog
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        return AuditLog.query.filter(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= cutoff
        ).order_by(AuditLog.timestamp.desc()).all()
    
    @staticmethod
    def get_ip_activity(ip_address, hours=24):
        """Get activity from a specific IP address."""
        from app.models import AuditLog
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        return AuditLog.query.filter(
            AuditLog.ip_address == ip_address,
            AuditLog.timestamp >= cutoff
        ).order_by(AuditLog.timestamp.desc()).all()
    
    @staticmethod
    def get_suspicious_activity():
        """Detect suspicious activity patterns."""
        from app.models import AuditLog, User
        
        suspicious = []
        
        # Check for multiple failed logins
        failed_logins = AuditService.get_failed_logins(hours=1)
        ip_counts = {}
        for event in failed_logins:
            ip = event.ip_address
            ip_counts[ip] = ip_counts.get(ip, 0) + 1
        
        for ip, count in ip_counts.items():
            if count >= 5:
                suspicious.append({
                    'type': 'BRUTE_FORCE_ATTEMPT',
                    'ip_address': ip,
                    'count': count,
                    'severity': 'CRITICAL'
                })
        
        # Check for account lockouts
        locked_accounts = User.query.filter(User.failed_login_attempts >= 5).all()
        for user in locked_accounts:
            suspicious.append({
                'type': 'ACCOUNT_LOCKED',
                'user': user.username,
                'failed_attempts': user.failed_login_attempts,
                'severity': 'WARNING'
            })
        
        return suspicious
    
    @staticmethod
    def get_statistics(days=30):
        """Get audit statistics for dashboard."""
        from app.models import AuditLog
        from sqlalchemy import func
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Total events
        total = AuditLog.query.filter(AuditLog.timestamp >= cutoff).count()
        
        # Events by day
        daily_events = []
        for i in range(days, -1, -1):
            day_start = (datetime.utcnow() - timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            day_end = day_start + timedelta(days=1)
            
            count = AuditLog.query.filter(
                AuditLog.timestamp >= day_start,
                AuditLog.timestamp < day_end
            ).count()
            
            daily_events.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'count': count
            })
        
        # Top events
        events = AuditLog.query.filter(AuditLog.timestamp >= cutoff).all()
        action_counts = {}
        for event in events:
            action = event.action.split(':')[-1] if ':' in event.action else event.action
            action_counts[action] = action_counts.get(action, 0) + 1
        
        top_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_events': total,
            'daily_events': daily_events,
            'top_actions': top_actions,
            'security_events': len(AuditService.get_security_events(hours=24 * days)),
            'failed_logins': len(AuditService.get_failed_logins(hours=24 * days))
        }
    
    @staticmethod
    def cleanup_old_logs(days=90):
        """Remove audit logs older than specified days."""
        from app.models import AuditLog, db
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        deleted = AuditLog.query.filter(AuditLog.timestamp < cutoff).delete()
        db.session.commit()
        
        return deleted

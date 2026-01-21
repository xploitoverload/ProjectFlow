# app/security/audit.py
"""
Security Audit and Logging Module
Comprehensive audit trail for security events.
"""

from flask import request, session, g
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging
import json
import hashlib

# Set up audit logger
audit_logger = logging.getLogger('audit')
security_logger = logging.getLogger('security')


class SecurityEvent:
    """Security event types for audit logging."""
    
    # Authentication
    LOGIN_SUCCESS = 'LOGIN_SUCCESS'
    LOGIN_FAILED = 'LOGIN_FAILED'
    LOGOUT = 'LOGOUT'
    PASSWORD_CHANGE = 'PASSWORD_CHANGE'
    PASSWORD_RESET_REQUEST = 'PASSWORD_RESET_REQUEST'
    PASSWORD_RESET_COMPLETE = 'PASSWORD_RESET_COMPLETE'
    ACCOUNT_LOCKED = 'ACCOUNT_LOCKED'
    ACCOUNT_UNLOCKED = 'ACCOUNT_UNLOCKED'
    SESSION_INVALIDATED = 'SESSION_INVALIDATED'
    
    # Authorization
    ACCESS_DENIED = 'ACCESS_DENIED'
    PERMISSION_DENIED = 'PERMISSION_DENIED'
    UNAUTHORIZED_ACCESS = 'UNAUTHORIZED_ACCESS'
    IDOR_ATTEMPT = 'IDOR_ATTEMPT'
    PRIVILEGE_ESCALATION_ATTEMPT = 'PRIVILEGE_ESCALATION_ATTEMPT'
    
    # Data Access
    DATA_READ = 'DATA_READ'
    DATA_CREATE = 'DATA_CREATE'
    DATA_UPDATE = 'DATA_UPDATE'
    DATA_DELETE = 'DATA_DELETE'
    BULK_DATA_ACCESS = 'BULK_DATA_ACCESS'
    SENSITIVE_DATA_ACCESS = 'SENSITIVE_DATA_ACCESS'
    
    # Security Threats
    RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED'
    INJECTION_ATTEMPT = 'INJECTION_ATTEMPT'
    XSS_ATTEMPT = 'XSS_ATTEMPT'
    CSRF_VIOLATION = 'CSRF_VIOLATION'
    BRUTE_FORCE_DETECTED = 'BRUTE_FORCE_DETECTED'
    SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY'
    
    # Admin Actions
    USER_CREATED = 'USER_CREATED'
    USER_UPDATED = 'USER_UPDATED'
    USER_DELETED = 'USER_DELETED'
    ROLE_CHANGED = 'ROLE_CHANGED'
    SETTINGS_CHANGED = 'SETTINGS_CHANGED'


class AuditLogger:
    """Centralized audit logging."""
    
    # In-memory storage for recent events (use database in production)
    _events: List[Dict] = []
    _max_events = 10000
    
    @classmethod
    def log(cls, event_type: str, user_id: Optional[int] = None,
            details: Optional[Dict] = None, severity: str = 'INFO',
            target_type: Optional[str] = None, target_id: Optional[int] = None) -> None:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            user_id: ID of user performing action (or target user)
            details: Additional context
            severity: INFO, WARNING, ERROR, CRITICAL
            target_type: Type of resource affected (e.g., 'User', 'Project')
            target_id: ID of affected resource
        """
        # Get user_id from session if not provided
        if user_id is None:
            user_id = session.get('user_id')
        
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'user_id': user_id,
            'username': session.get('username'),
            'role': session.get('role'),
            'ip_address': cls._get_client_ip(),
            'user_agent': request.headers.get('User-Agent', '')[:200] if request else None,
            'endpoint': request.endpoint if request else None,
            'method': request.method if request else None,
            'path': request.path if request else None,
            'target_type': target_type,
            'target_id': target_id,
            'details': details or {}
        }
        
        # Store event
        cls._events.append(event)
        
        # Limit memory usage
        if len(cls._events) > cls._max_events:
            cls._events = cls._events[-cls._max_events:]
        
        # Log to file
        log_message = json.dumps(event, default=str)
        
        if severity == 'CRITICAL':
            audit_logger.critical(log_message)
        elif severity == 'ERROR':
            audit_logger.error(log_message)
        elif severity == 'WARNING':
            audit_logger.warning(log_message)
        else:
            audit_logger.info(log_message)
        
        # Also store in database if available
        cls._store_in_database(event)
    
    @classmethod
    def _store_in_database(cls, event: Dict) -> None:
        """Store event in database."""
        try:
            from app.models import AuditLog, db
            
            log_entry = AuditLog(
                event_type=event['event_type'],
                user_id=event['user_id'],
                ip_address=event['ip_address'],
                user_agent=event['user_agent'],
                endpoint=event['endpoint'],
                details=json.dumps(event['details']),
                severity=event['severity'],
                timestamp=datetime.fromisoformat(event['timestamp'])
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            security_logger.error(f"Failed to store audit log in database: {e}")
    
    @classmethod
    def get_events(cls, user_id: Optional[int] = None,
                   event_type: Optional[str] = None,
                   severity: Optional[str] = None,
                   hours: int = 24,
                   limit: int = 100) -> List[Dict]:
        """Get recent audit events with filtering."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        events = [
            e for e in cls._events
            if datetime.fromisoformat(e['timestamp']) > cutoff
        ]
        
        if user_id:
            events = [e for e in events if e.get('user_id') == user_id]
        
        if event_type:
            events = [e for e in events if e.get('event_type') == event_type]
        
        if severity:
            events = [e for e in events if e.get('severity') == severity]
        
        return events[-limit:]
    
    @classmethod
    def get_suspicious_activity(cls, hours: int = 24) -> List[Dict]:
        """Get suspicious activity patterns."""
        suspicious = []
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Count events by IP
        ip_counts: Dict[str, List[Dict]] = {}
        for event in cls._events:
            if datetime.fromisoformat(event['timestamp']) > cutoff:
                ip = event.get('ip_address', 'unknown')
                if ip not in ip_counts:
                    ip_counts[ip] = []
                ip_counts[ip].append(event)
        
        # Flag IPs with many failed logins
        for ip, events in ip_counts.items():
            failed_logins = [e for e in events if e['event_type'] == SecurityEvent.LOGIN_FAILED]
            if len(failed_logins) >= 5:
                suspicious.append({
                    'type': 'BRUTE_FORCE',
                    'ip': ip,
                    'count': len(failed_logins),
                    'events': failed_logins[-5:]
                })
            
            # Flag IPs with access denied events
            access_denied = [e for e in events if 'DENIED' in e['event_type'] or 'ATTEMPT' in e['event_type']]
            if len(access_denied) >= 3:
                suspicious.append({
                    'type': 'ACCESS_VIOLATION',
                    'ip': ip,
                    'count': len(access_denied),
                    'events': access_denied[-5:]
                })
        
        return suspicious
    
    @staticmethod
    def _get_client_ip() -> str:
        """Get client IP address."""
        if not request:
            return 'system'
        
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        elif request.environ.get('HTTP_X_REAL_IP'):
            return request.environ['HTTP_X_REAL_IP']
        return request.environ.get('REMOTE_ADDR', '127.0.0.1')


def log_security_event(event_type: str, user_id: Optional[int] = None,
                       details: Optional[Dict] = None, severity: str = 'INFO') -> None:
    """Convenience function for logging security events."""
    AuditLogger.log(event_type, user_id, details, severity)


def log_access_attempt(resource_type: str, resource_id: int,
                       action: str, allowed: bool) -> None:
    """Log data access attempt."""
    event_type = SecurityEvent.DATA_READ if allowed else SecurityEvent.ACCESS_DENIED
    severity = 'INFO' if allowed else 'WARNING'
    
    AuditLogger.log(
        event_type=event_type,
        details={
            'action': action,
            'allowed': allowed
        },
        severity=severity,
        target_type=resource_type,
        target_id=resource_id
    )


def log_data_access(resource_type: str, resource_id: int, action: str) -> None:
    """Log successful data access."""
    event_map = {
        'read': SecurityEvent.DATA_READ,
        'create': SecurityEvent.DATA_CREATE,
        'update': SecurityEvent.DATA_UPDATE,
        'delete': SecurityEvent.DATA_DELETE,
    }
    
    event_type = event_map.get(action.lower(), SecurityEvent.DATA_READ)
    
    AuditLogger.log(
        event_type=event_type,
        target_type=resource_type,
        target_id=resource_id,
        severity='INFO'
    )


def log_authentication(success: bool, username: str,
                       details: Optional[Dict] = None) -> None:
    """Log authentication attempt."""
    event_type = SecurityEvent.LOGIN_SUCCESS if success else SecurityEvent.LOGIN_FAILED
    severity = 'INFO' if success else 'WARNING'
    
    AuditLogger.log(
        event_type=event_type,
        details={'username': username, **(details or {})},
        severity=severity
    )


def log_admin_action(action: str, target_user_id: Optional[int] = None,
                     details: Optional[Dict] = None) -> None:
    """Log administrative action."""
    event_map = {
        'create_user': SecurityEvent.USER_CREATED,
        'update_user': SecurityEvent.USER_UPDATED,
        'delete_user': SecurityEvent.USER_DELETED,
        'change_role': SecurityEvent.ROLE_CHANGED,
        'change_settings': SecurityEvent.SETTINGS_CHANGED,
    }
    
    event_type = event_map.get(action, 'ADMIN_ACTION')
    
    AuditLogger.log(
        event_type=event_type,
        details=details,
        severity='INFO',
        target_type='User',
        target_id=target_user_id
    )

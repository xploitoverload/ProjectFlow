# app/compliance/audit.py
"""
Comprehensive Compliance & Audit Module
GDPR, HIPAA, SOC2 compliance with audit logging and data retention.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum
import uuid


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"      # EU General Data Protection Regulation
    HIPAA = "hipaa"    # Health Insurance Portability & Accountability Act
    SOC2 = "soc2"      # Service Organization Control
    CCPA = "ccpa"      # California Consumer Privacy Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard


class AuditEventType(Enum):
    """Types of audit events."""
    # Access events
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS_DENIED = "access_denied"
    PERMISSION_GRANTED = "permission_granted"
    
    # Data events
    DATA_CREATED = "data_created"
    DATA_READ = "data_read"
    DATA_MODIFIED = "data_modified"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    
    # Security events
    FAILED_AUTH = "failed_auth"
    SECURITY_ALERT = "security_alert"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    
    # Compliance events
    CONSENT_GIVEN = "consent_given"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    DATA_SUBJECT_REQUEST = "data_subject_request"
    POLICY_VIOLATION = "policy_violation"


class DataClassification(Enum):
    """Data sensitivity classification."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # PII, PHI, etc


class RetentionPolicy(Enum):
    """Data retention policies."""
    DELETE_ON_REQUEST = "delete_on_request"  # GDPR - Right to be forgotten
    KEEP_FOR_30_DAYS = "keep_30_days"
    KEEP_FOR_90_DAYS = "keep_90_days"
    KEEP_FOR_1_YEAR = "keep_1_year"
    KEEP_FOR_7_YEARS = "keep_7_years"  # HIPAA requirement
    KEEP_INDEFINITELY = "keep_indefinitely"


@dataclass
class AuditLog:
    """Audit log entry."""
    audit_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: AuditEventType = AuditEventType.LOGIN
    user_id: str = ""
    resource: str = ""
    action: str = ""
    status: str = "success"  # success, failure
    ip_address: str = ""
    user_agent: str = ""
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'audit_id': self.audit_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'resource': self.resource,
            'action': self.action,
            'status': self.status,
            'details': self.details
        }


@dataclass
class DataSubjectRight:
    """GDPR data subject rights request."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    request_type: str = ""  # access, deletion, portability, rectification
    status: str = "pending"  # pending, in_progress, completed, denied
    requested_at: datetime = field(default_factory=datetime.utcnow)
    response_deadline: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    completed_at: Optional[datetime] = None
    reason: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'request_type': self.request_type,
            'status': self.status,
            'requested_at': self.requested_at.isoformat(),
            'response_deadline': self.response_deadline.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class ConsentRecord:
    """User consent record for GDPR."""
    consent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    purpose: str = ""  # marketing, analytics, processing, etc
    given_at: datetime = field(default_factory=datetime.utcnow)
    withdrawn_at: Optional[datetime] = None
    version: str = "1.0"
    ip_address: str = ""
    
    def is_active(self) -> bool:
        """Check if consent is currently active."""
        return self.withdrawn_at is None
    
    def to_dict(self) -> Dict:
        return {
            'consent_id': self.consent_id,
            'user_id': self.user_id,
            'purpose': self.purpose,
            'given_at': self.given_at.isoformat(),
            'withdrawn_at': self.withdrawn_at.isoformat() if self.withdrawn_at else None,
            'active': self.is_active()
        }


class ComplianceAuditEngine:
    """
    Manages compliance frameworks, audit logging, and data subject rights.
    """
    
    def __init__(self):
        """Initialize compliance engine."""
        self.audit_logs: List[AuditLog] = []
        self.data_subject_requests: Dict[str, DataSubjectRight] = {}
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.retention_policies: Dict[str, RetentionPolicy] = self._default_policies()
        self.enabled_frameworks: Set[ComplianceFramework] = {
            ComplianceFramework.GDPR,
            ComplianceFramework.HIPAA,
            ComplianceFramework.SOC2
        }
    
    def _default_policies(self) -> Dict[str, RetentionPolicy]:
        """Default data retention policies."""
        return {
            'audit_logs': RetentionPolicy.KEEP_FOR_7_YEARS,
            'user_data': RetentionPolicy.DELETE_ON_REQUEST,
            'medical_records': RetentionPolicy.KEEP_FOR_7_YEARS,
            'financial_records': RetentionPolicy.KEEP_FOR_7_YEARS,
            'consent_records': RetentionPolicy.KEEP_FOR_7_YEARS,
            'activity_logs': RetentionPolicy.KEEP_FOR_90_DAYS
        }
    
    def log_event(self, event_type: AuditEventType, user_id: str, 
                 resource: str, action: str, status: str = "success",
                 ip_address: str = "", details: Dict = None) -> AuditLog:
        """Log audit event."""
        log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            resource=resource,
            action=action,
            status=status,
            ip_address=ip_address,
            details=details or {}
        )
        
        self.audit_logs.append(log)
        return log
    
    def log_data_access(self, user_id: str, resource: str, 
                       data_type: str, classification: DataClassification) -> AuditLog:
        """Log data access with classification."""
        return self.log_event(
            AuditEventType.DATA_READ,
            user_id,
            resource,
            'data_access',
            details={
                'data_type': data_type,
                'classification': classification.value
            }
        )
    
    def log_data_deletion(self, user_id: str, resource: str,
                         reason: str = "") -> AuditLog:
        """Log data deletion."""
        return self.log_event(
            AuditEventType.DATA_DELETED,
            user_id,
            resource,
            'data_deletion',
            details={'reason': reason}
        )
    
    def request_data_subject_right(self, user_id: str, request_type: str,
                                  reason: str = "") -> DataSubjectRight:
        """Request GDPR data subject right (access, deletion, portability)."""
        request = DataSubjectRight(
            user_id=user_id,
            request_type=request_type,
            reason=reason
        )
        
        self.data_subject_requests[request.request_id] = request
        
        # Log the request
        self.log_event(
            AuditEventType.DATA_SUBJECT_REQUEST,
            user_id,
            'user_account',
            request_type,
            details={
                'request_id': request.request_id,
                'deadline_days': 30
            }
        )
        
        return request
    
    def complete_data_subject_request(self, request_id: str) -> bool:
        """Mark data subject request as completed."""
        if request_id not in self.data_subject_requests:
            return False
        
        request = self.data_subject_requests[request_id]
        request.status = 'completed'
        request.completed_at = datetime.utcnow()
        
        return True
    
    def give_consent(self, user_id: str, purpose: str,
                    ip_address: str = "") -> ConsentRecord:
        """Record user consent (GDPR)."""
        consent = ConsentRecord(
            user_id=user_id,
            purpose=purpose,
            ip_address=ip_address
        )
        
        self.consent_records[consent.consent_id] = consent
        
        # Log consent
        self.log_event(
            AuditEventType.CONSENT_GIVEN,
            user_id,
            'consent_management',
            f'consent_given_{purpose}',
            details={'purpose': purpose}
        )
        
        return consent
    
    def withdraw_consent(self, user_id: str, purpose: str) -> bool:
        """Withdraw consent."""
        # Find and withdraw matching consent records
        withdrawn = False
        for consent in self.consent_records.values():
            if consent.user_id == user_id and consent.purpose == purpose and consent.is_active():
                consent.withdrawn_at = datetime.utcnow()
                withdrawn = True
        
        if withdrawn:
            self.log_event(
                AuditEventType.CONSENT_WITHDRAWN,
                user_id,
                'consent_management',
                f'consent_withdrawn_{purpose}',
                details={'purpose': purpose}
            )
        
        return withdrawn
    
    def check_consent(self, user_id: str, purpose: str) -> bool:
        """Check if user has active consent for purpose."""
        for consent in self.consent_records.values():
            if consent.user_id == user_id and consent.purpose == purpose:
                return consent.is_active()
        return False
    
    def get_user_audit_trail(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get audit log for specific user."""
        logs = [log for log in self.audit_logs if log.user_id == user_id]
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return [log.to_dict() for log in logs[:limit]]
    
    def get_audit_logs(self, event_type: AuditEventType = None,
                      start_date: datetime = None,
                      end_date: datetime = None,
                      limit: int = 1000) -> List[Dict]:
        """Get filtered audit logs."""
        logs = self.audit_logs
        
        if event_type:
            logs = [log for log in logs if log.event_type == event_type]
        
        if start_date:
            logs = [log for log in logs if log.timestamp >= start_date]
        
        if end_date:
            logs = [log for log in logs if log.timestamp <= end_date]
        
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return [log.to_dict() for log in logs[:limit]]
    
    def cleanup_expired_data(self) -> Dict:
        """Clean up expired data based on retention policies."""
        before_count = len(self.audit_logs)
        cutoff_date = datetime.utcnow() - timedelta(days=2555)  # 7 years
        
        self.audit_logs = [log for log in self.audit_logs if log.timestamp > cutoff_date]
        
        deleted_count = before_count - len(self.audit_logs)
        
        return {
            'deleted_logs': deleted_count,
            'remaining_logs': len(self.audit_logs),
            'cleanup_date': datetime.utcnow().isoformat()
        }
    
    def generate_compliance_report(self, framework: ComplianceFramework) -> Dict:
        """Generate compliance report."""
        return {
            'framework': framework.value,
            'report_date': datetime.utcnow().isoformat(),
            'total_events': len(self.audit_logs),
            'data_subject_requests': len(self.data_subject_requests),
            'active_consents': sum(1 for c in self.consent_records.values() if c.is_active()),
            'security_events': sum(1 for log in self.audit_logs if 'security' in log.event_type.value),
            'failed_authentications': sum(1 for log in self.audit_logs if log.event_type == AuditEventType.FAILED_AUTH),
            'access_denials': sum(1 for log in self.audit_logs if log.event_type == AuditEventType.ACCESS_DENIED),
            'data_deletions': sum(1 for log in self.audit_logs if log.event_type == AuditEventType.DATA_DELETED),
            'policy_violations': sum(1 for log in self.audit_logs if log.event_type == AuditEventType.POLICY_VIOLATION)
        }
    
    def get_stats(self) -> Dict:
        """Get compliance statistics."""
        return {
            'audit_logs': len(self.audit_logs),
            'data_subject_requests': len(self.data_subject_requests),
            'pending_requests': sum(1 for r in self.data_subject_requests.values() if r.status == 'pending'),
            'consent_records': len(self.consent_records),
            'active_consents': sum(1 for c in self.consent_records.values() if c.is_active()),
            'enabled_frameworks': [f.value for f in self.enabled_frameworks],
            'recent_7_days': sum(1 for log in self.audit_logs 
                                if log.timestamp > datetime.utcnow() - timedelta(days=7))
        }


# Global compliance audit engine
compliance_engine = ComplianceAuditEngine()

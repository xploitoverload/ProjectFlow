"""Zero-Trust security engine."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """User trust level."""
    UNKNOWN = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    MAXIMUM = 4


@dataclass
class SecurityContext:
    """Security context for request."""
    user_id: str
    device_id: str
    ip_address: str
    timestamp: str
    trust_score: float  # 0-100
    risk_level: str  # low, medium, high, critical
    verified: bool
    mfa_passed: bool


class ZeroTrustEngine:
    """Zero-Trust security engine."""
    
    def __init__(self):
        """Initialize zero-trust engine."""
        self.contexts: Dict[str, SecurityContext] = {}
        self.trust_scores: Dict[str, float] = {}
        self.risk_assessments: List[Dict] = []
        self.deny_count = 0
        self.allow_count = 0
    
    def evaluate_trust(self, user_id: str, device_id: str, 
                      ip_address: str, context: Dict = None) -> SecurityContext:
        """
        Evaluate trust level for request.
        
        Args:
            user_id: User ID
            device_id: Device ID
            ip_address: Source IP
            context: Additional context
            
        Returns:
            SecurityContext instance
        """
        context_id = f"ctx_{int(datetime.now().timestamp() * 1000)}"
        
        # Calculate trust score
        trust_score = self._calculate_trust_score(user_id, device_id, ip_address, context)
        risk_level = self._assess_risk(trust_score)
        
        security_ctx = SecurityContext(
            user_id=user_id,
            device_id=device_id,
            ip_address=ip_address,
            timestamp=datetime.now().isoformat(),
            trust_score=trust_score,
            risk_level=risk_level,
            verified=trust_score >= 60,
            mfa_passed=context.get('mfa_passed', False) if context else False
        )
        
        self.contexts[context_id] = security_ctx
        self.trust_scores[user_id] = trust_score
        
        logger.info(f"Trust evaluated: {user_id} - score: {trust_score}")
        
        return security_ctx
    
    def _calculate_trust_score(self, user_id: str, device_id: str,
                              ip_address: str, context: Dict = None) -> float:
        """Calculate trust score."""
        score = 50.0  # Base score
        
        # Known device bonus
        if device_id == "known_device":
            score += 20
        
        # Known IP bonus
        if ip_address.startswith("192.168"):
            score += 15
        
        # MFA bonus
        if context and context.get('mfa_passed'):
            score += 25
        
        # Risk factors
        if context:
            if context.get('suspicious_activity'):
                score -= 30
            if context.get('new_location'):
                score -= 15
        
        return min(100, max(0, score))
    
    def _assess_risk(self, score: float) -> str:
        """Assess risk level based on score."""
        if score >= 80:
            return "low"
        elif score >= 60:
            return "medium"
        elif score >= 40:
            return "high"
        else:
            return "critical"
    
    def enforce_access(self, security_ctx: SecurityContext,
                      resource: str) -> bool:
        """
        Enforce zero-trust access control.
        
        Args:
            security_ctx: Security context
            resource: Resource being accessed
            
        Returns:
            True if access allowed
        """
        # Critical risk = deny
        if security_ctx.risk_level == "critical":
            self.deny_count += 1
            logger.warning(f"Access denied: {security_ctx.user_id}")
            return False
        
        # High risk = require MFA
        if security_ctx.risk_level == "high" and not security_ctx.mfa_passed:
            self.deny_count += 1
            logger.warning(f"MFA required: {security_ctx.user_id}")
            return False
        
        # Low/medium risk = allow
        self.allow_count += 1
        logger.info(f"Access allowed: {security_ctx.user_id}")
        return True
    
    def get_stats(self) -> Dict:
        """Get zero-trust engine statistics."""
        return {
            'active_contexts': len(self.contexts),
            'allow_count': self.allow_count,
            'deny_count': self.deny_count,
            'risk_assessments': len(self.risk_assessments),
            'average_trust_score': sum(self.trust_scores.values()) / len(self.trust_scores) \
                                   if self.trust_scores else 0
        }

"""Continuous verification system."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VerificationEvent:
    """Verification event."""
    id: str
    user_id: str
    event_type: str  # auth, action, resource_access
    timestamp: str
    passed: bool
    reason: Optional[str] = None


class ContinuousVerification:
    """Continuous verification system."""
    
    def __init__(self):
        """Initialize continuous verification."""
        self.verification_events: List[VerificationEvent] = []
        self.user_risk_scores: Dict[str, float] = {}
        self.verification_rules: List[Dict] = []
        self.re_auth_threshold = 60  # minutes
    
    def verify_action(self, user_id: str, action: str,
                     context: Dict = None) -> bool:
        """
        Continuously verify user action.
        
        Args:
            user_id: User ID
            action: Action being performed
            context: Additional context
            
        Returns:
            True if action allowed
        """
        event_id = f"vfy_{int(datetime.now().timestamp() * 1000)}"
        
        # Evaluate risk
        risk_score = self._evaluate_risk(user_id, action, context)
        self.user_risk_scores[user_id] = risk_score
        
        # High risk actions require re-auth
        high_risk_actions = ['delete', 'grant_permission', 'export_data']
        requires_reauth = action in high_risk_actions and risk_score > 70
        
        event = VerificationEvent(
            id=event_id,
            user_id=user_id,
            event_type='action',
            timestamp=datetime.now().isoformat(),
            passed=not requires_reauth,
            reason='re-auth required' if requires_reauth else None
        )
        
        self.verification_events.append(event)
        logger.info(f"Action verification: {action} - {'passed' if event.passed else 'denied'}")
        
        return event.passed
    
    def _evaluate_risk(self, user_id: str, action: str,
                      context: Dict = None) -> float:
        """Evaluate risk score."""
        risk = 30  # Base risk
        
        # Action-based risk
        if action in ['delete', 'export_data', 'manage_users']:
            risk += 40
        elif action in ['read', 'view']:
            risk -= 20
        
        # Time-based risk
        hour = datetime.now().hour
        if hour < 6 or hour > 22:  # Off-hours
            risk += 20
        
        # Context-based risk
        if context:
            if context.get('new_device'):
                risk += 25
            if context.get('different_location'):
                risk += 20
        
        return min(100, max(0, risk))
    
    def require_reauthentication(self, user_id: str, reason: str = None) -> Dict:
        """
        Require user to re-authenticate.
        
        Args:
            user_id: User ID
            reason: Reason for re-auth
            
        Returns:
            Re-auth request
        """
        event = VerificationEvent(
            id=f"reauth_{int(datetime.now().timestamp() * 1000)}",
            user_id=user_id,
            event_type='reauthentication_required',
            timestamp=datetime.now().isoformat(),
            passed=False,
            reason=reason or 'continuous verification triggered'
        )
        
        self.verification_events.append(event)
        
        return {
            'required': True,
            'reason': reason,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
    
    def verify_session(self, user_id: str, session_age_minutes: int) -> bool:
        """
        Verify active session.
        
        Args:
            user_id: User ID
            session_age_minutes: Age of session in minutes
            
        Returns:
            True if session valid
        """
        # Re-auth if session old
        if session_age_minutes > self.re_auth_threshold:
            self.require_reauthentication(user_id, 'session expired')
            return False
        
        return True
    
    def get_user_risk_score(self, user_id: str) -> float:
        """Get current risk score for user."""
        return self.user_risk_scores.get(user_id, 30)
    
    def get_recent_events(self, user_id: str = None, limit: int = 50) -> List[Dict]:
        """Get recent verification events."""
        events = self.verification_events
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        events = sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]
        
        return [
            {
                'id': e.id,
                'user_id': e.user_id,
                'event_type': e.event_type,
                'timestamp': e.timestamp,
                'passed': e.passed,
                'reason': e.reason
            }
            for e in events
        ]
    
    def get_stats(self) -> Dict:
        """Get verification statistics."""
        passed = sum(1 for e in self.verification_events if e.passed)
        failed = sum(1 for e in self.verification_events if not e.passed)
        
        return {
            'total_events': len(self.verification_events),
            'passed_verifications': passed,
            'failed_verifications': failed,
            'users_monitored': len(self.user_risk_scores),
            'average_risk_score': sum(self.user_risk_scores.values()) / \
                                 len(self.user_risk_scores) if self.user_risk_scores else 0
        }

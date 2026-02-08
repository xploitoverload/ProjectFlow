"""Micro-segmentation implementation."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SegmentType(Enum):
    """Segment types."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    API = "api"
    INTERNAL = "internal"
    EXTERNAL = "external"


@dataclass
class Segment:
    """Network segment."""
    id: str
    name: str
    type: SegmentType
    members: Set[str] = None
    policies: List[Dict] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.members is None:
            self.members = set()
        if self.policies is None:
            self.policies = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class MicroSegmentation:
    """Micro-segmentation engine."""
    
    def __init__(self):
        """Initialize micro-segmentation."""
        self.segments: Dict[str, Segment] = {}
        self.user_segments: Dict[str, Set[str]] = {}  # user_id -> segment_ids
        self.access_rules: Dict[str, List[Dict]] = {}
        self._setup_default_segments()
    
    def _setup_default_segments(self):
        """Setup default segments."""
        segments = [
            Segment(id='seg_admin', name='Administrators', type=SegmentType.ADMIN),
            Segment(id='seg_users', name='Regular Users', type=SegmentType.USER),
            Segment(id='seg_guests', name='Guest Users', type=SegmentType.GUEST),
            Segment(id='seg_api', name='API Services', type=SegmentType.API),
            Segment(id='seg_internal', name='Internal Systems', type=SegmentType.INTERNAL),
        ]
        
        for segment in segments:
            self.segments[segment.id] = segment
    
    def create_segment(self, name: str, segment_type: SegmentType) -> Segment:
        """
        Create new segment.
        
        Args:
            name: Segment name
            segment_type: Segment type
            
        Returns:
            Segment instance
        """
        segment_id = f"seg_{int(datetime.now().timestamp() * 1000)}"
        
        segment = Segment(
            id=segment_id,
            name=name,
            type=segment_type
        )
        
        self.segments[segment_id] = segment
        logger.info(f"Segment created: {segment_id}")
        
        return segment
    
    def add_to_segment(self, user_id: str, segment_id: str) -> bool:
        """
        Add user to segment.
        
        Args:
            user_id: User ID
            segment_id: Segment ID
            
        Returns:
            True if successful
        """
        if segment_id not in self.segments:
            return False
        
        self.segments[segment_id].members.add(user_id)
        
        if user_id not in self.user_segments:
            self.user_segments[user_id] = set()
        
        self.user_segments[user_id].add(segment_id)
        logger.info(f"User {user_id} added to segment {segment_id}")
        
        return True
    
    def remove_from_segment(self, user_id: str, segment_id: str) -> bool:
        """Remove user from segment."""
        if segment_id not in self.segments:
            return False
        
        self.segments[segment_id].members.discard(user_id)
        
        if user_id in self.user_segments:
            self.user_segments[user_id].discard(segment_id)
        
        return True
    
    def set_access_policy(self, source_segment: str, target_segment: str,
                         allowed: bool) -> None:
        """
        Set access policy between segments.
        
        Args:
            source_segment: Source segment ID
            target_segment: Target segment ID
            allowed: Allow or deny
        """
        policy_key = f"{source_segment}->{target_segment}"
        
        if policy_key not in self.access_rules:
            self.access_rules[policy_key] = []
        
        self.access_rules[policy_key].append({
            'allowed': allowed,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Policy set: {policy_key} -> {'allow' if allowed else 'deny'}")
    
    def can_access(self, user_id: str, target_segment: str) -> bool:
        """
        Check if user can access segment.
        
        Args:
            user_id: User ID
            target_segment: Target segment ID
            
        Returns:
            True if access allowed
        """
        user_segs = self.user_segments.get(user_id, set())
        
        for source_seg in user_segs:
            policy_key = f"{source_seg}->{target_segment}"
            
            if policy_key in self.access_rules:
                rules = self.access_rules[policy_key]
                if rules:
                    latest_rule = rules[-1]
                    if latest_rule['allowed']:
                        return True
        
        return False
    
    def get_user_segments(self, user_id: str) -> List[Segment]:
        """Get segments for user."""
        segment_ids = self.user_segments.get(user_id, set())
        return [self.segments[sid] for sid in segment_ids if sid in self.segments]
    
    def get_stats(self) -> Dict:
        """Get segmentation statistics."""
        return {
            'total_segments': len(self.segments),
            'users_segmented': len(self.user_segments),
            'access_rules': len(self.access_rules),
            'segment_types': [s.type.value for s in self.segments.values()]
        }

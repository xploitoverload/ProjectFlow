# app/ml/team_collaboration.py
"""
Team Collaboration AI System
Real-time collaboration, smart suggestions, activity tracking, and team insights.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum
import uuid


class CollaborationActivityType(Enum):
    """Types of collaboration activities."""
    MESSAGE = "message"
    MENTION = "mention"
    EDIT = "edit"
    COMMENT = "comment"
    APPROVAL = "approval"
    ASSIGNMENT = "assignment"
    COMPLETION = "completion"


class SuggestionType(Enum):
    """Smart suggestion types."""
    ASSIGNMENT = "assignment"  # Suggest who should do task
    TIMING = "timing"         # Suggest best time for meeting
    EXPERTISE = "expertise"   # Suggest expert for question
    COLLABORATION = "collaboration"  # Suggest who should collaborate
    AUTOMATION = "automation" # Suggest task automation


@dataclass
class TeamMember:
    """Team member profile."""
    member_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    role: str = ""
    skills: List[str] = field(default_factory=list)
    availability: Dict = field(default_factory=dict)  # day -> hours
    activity_level: float = 0.0  # 0-1 scale
    last_active: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'member_id': self.member_id,
            'name': self.name,
            'role': self.role,
            'skills': self.skills,
            'activity_level': self.activity_level,
            'last_active': self.last_active.isoformat()
        }


@dataclass
class CollaborationActivity:
    """Collaboration activity record."""
    activity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str = ""
    activity_type: CollaborationActivityType = CollaborationActivityType.MESSAGE
    resource_id: str = ""
    resource_type: str = ""  # task, document, project
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'activity_id': self.activity_id,
            'member_id': self.member_id,
            'activity_type': self.activity_type.value,
            'resource_type': self.resource_type,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class SmartSuggestion:
    """AI-generated smart suggestion."""
    suggestion_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    suggestion_type: SuggestionType = SuggestionType.ASSIGNMENT
    context: str = ""
    suggested_members: List[str] = field(default_factory=list)
    confidence: float = 0.0
    rationale: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    accepted: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'suggestion_id': self.suggestion_id,
            'type': self.suggestion_type.value,
            'suggested_members': self.suggested_members,
            'confidence': round(self.confidence, 2),
            'rationale': self.rationale,
            'accepted': self.accepted
        }


class TeamCollaborationAI:
    """
    AI-powered team collaboration system with real-time insights.
    """
    
    def __init__(self):
        """Initialize team collaboration system."""
        self.team_members: Dict[str, TeamMember] = {}
        self.activities: List[CollaborationActivity] = []
        self.suggestions: Dict[str, SmartSuggestion] = {}
        self.team_metrics = {
            'total_activities': 0,
            'collaboration_score': 0.0,
            'response_time_avg': 0,
            'productivity_index': 0.0
        }
    
    def add_team_member(self, name: str, email: str, role: str,
                       skills: List[str] = None) -> TeamMember:
        """Add team member."""
        member = TeamMember(
            name=name,
            email=email,
            role=role,
            skills=skills or []
        )
        
        self.team_members[member.member_id] = member
        return member
    
    def log_activity(self, member_id: str, activity_type: CollaborationActivityType,
                    resource_id: str, resource_type: str,
                    details: Dict = None) -> CollaborationActivity:
        """Log collaboration activity."""
        activity = CollaborationActivity(
            member_id=member_id,
            activity_type=activity_type,
            resource_id=resource_id,
            resource_type=resource_type,
            details=details or {}
        )
        
        self.activities.append(activity)
        self.team_metrics['total_activities'] += 1
        
        # Update member's activity level
        if member_id in self.team_members:
            member = self.team_members[member_id]
            member.last_active = datetime.utcnow()
            member.activity_level = min(1.0, member.activity_level + 0.05)
        
        return activity
    
    def suggest_team_member_for_task(self, task_description: str,
                                    required_skills: List[str]) -> SmartSuggestion:
        """AI suggestion for who should be assigned to task."""
        # Find members with matching skills
        candidates = []
        for member in self.team_members.values():
            skill_match = sum(1 for skill in required_skills if skill in member.skills)
            if skill_match > 0:
                candidates.append((member, skill_match))
        
        # Sort by skill match and activity level
        candidates.sort(key=lambda x: (x[1], x[0].activity_level), reverse=True)
        
        suggested_members = [c[0].member_id for c in candidates[:3]]
        confidence = min(1.0, len(candidates) / max(len(required_skills), 1))
        
        suggestion = SmartSuggestion(
            suggestion_type=SuggestionType.ASSIGNMENT,
            context=task_description,
            suggested_members=suggested_members,
            confidence=confidence,
            rationale=f"Based on skill match and current activity level"
        )
        
        self.suggestions[suggestion.suggestion_id] = suggestion
        return suggestion
    
    def suggest_meeting_time(self, member_ids: List[str],
                           duration_minutes: int = 60) -> SmartSuggestion:
        """AI suggestion for best meeting time."""
        # Find common available slots
        available_slots = {}
        
        for hour in range(9, 18):  # 9am to 6pm
            day_key = 'all_days'
            availability = sum(
                1 for mid in member_ids 
                if mid in self.team_members and hour in self.team_members[mid].availability.get(day_key, [])
            )
            
            if availability == len(member_ids):
                available_slots[hour] = availability
        
        best_slot = max(available_slots.items(), key=lambda x: x[1])[0] if available_slots else 10
        
        suggestion = SmartSuggestion(
            suggestion_type=SuggestionType.TIMING,
            context=f"Meeting for {len(member_ids)} members ({duration_minutes} min)",
            suggested_members=member_ids,
            confidence=0.85,
            rationale=f"Suggested time: {best_slot}:00 - all participants available"
        )
        
        self.suggestions[suggestion.suggestion_id] = suggestion
        return suggestion
    
    def suggest_expert(self, topic: str, member_ids: List[str] = None) -> SmartSuggestion:
        """AI suggestion for expert on topic."""
        if not member_ids:
            member_ids = list(self.team_members.keys())
        
        topic_keywords = topic.lower().split()
        
        # Find expert by skill match
        candidates = []
        for mid in member_ids:
            if mid not in self.team_members:
                continue
            
            member = self.team_members[mid]
            skill_match = sum(1 for keyword in topic_keywords if keyword in member.skills)
            
            if skill_match > 0:
                candidates.append((mid, skill_match))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        suggested_members = [c[0] for c in candidates[:2]]
        confidence = min(1.0, (candidates[0][1] / len(topic_keywords)) if candidates else 0)
        
        suggestion = SmartSuggestion(
            suggestion_type=SuggestionType.EXPERTISE,
            context=f"Expert needed for: {topic}",
            suggested_members=suggested_members,
            confidence=confidence,
            rationale=f"Member(s) with relevant skills in {topic}"
        )
        
        self.suggestions[suggestion.suggestion_id] = suggestion
        return suggestion
    
    def get_collaboration_insights(self, member_id: str = None) -> Dict:
        """Get collaboration insights."""
        if member_id and member_id in self.team_members:
            # Individual insights
            member = self.team_members[member_id]
            member_activities = [a for a in self.activities if a.member_id == member_id]
            
            activity_by_type = {}
            for activity in member_activities:
                atype = activity.activity_type.value
                activity_by_type[atype] = activity_by_type.get(atype, 0) + 1
            
            return {
                'member_id': member_id,
                'name': member.name,
                'activity_count': len(member_activities),
                'activity_by_type': activity_by_type,
                'activity_level': member.activity_level,
                'last_active': member.last_active.isoformat()
            }
        else:
            # Team insights
            activities_by_type = {}
            for activity in self.activities:
                atype = activity.activity_type.value
                activities_by_type[atype] = activities_by_type.get(atype, 0) + 1
            
            # Calculate collaboration score
            team_members_active = sum(1 for m in self.team_members.values() if m.activity_level > 0.3)
            collaboration_score = (team_members_active / max(len(self.team_members), 1)) * 100
            
            return {
                'total_members': len(self.team_members),
                'total_activities': self.team_metrics['total_activities'],
                'activities_by_type': activities_by_type,
                'active_members': team_members_active,
                'collaboration_score': round(collaboration_score, 1),
                'recent_activities': [a.to_dict() for a in self.activities[-10:]]
            }
    
    def get_team_stats(self) -> Dict:
        """Get team statistics."""
        return {
            'total_members': len(self.team_members),
            'total_activities': self.team_metrics['total_activities'],
            'total_suggestions': len(self.suggestions),
            'accepted_suggestions': sum(1 for s in self.suggestions.values() if s.accepted),
            'team_roles': list(set(m.role for m in self.team_members.values())),
            'average_activity_level': round(
                sum(m.activity_level for m in self.team_members.values()) / max(len(self.team_members), 1), 2
            )
        }
    
    def accept_suggestion(self, suggestion_id: str) -> bool:
        """Mark suggestion as accepted."""
        if suggestion_id in self.suggestions:
            self.suggestions[suggestion_id].accepted = True
            return True
        return False
    
    def get_member_activity_timeline(self, member_id: str, 
                                     days: int = 7) -> List[Dict]:
        """Get member activity timeline."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        activities = [a for a in self.activities 
                     if a.member_id == member_id and a.timestamp > cutoff_date]
        
        return [a.to_dict() for a in activities]


# Global team collaboration AI instance
team_collab = TeamCollaborationAI()

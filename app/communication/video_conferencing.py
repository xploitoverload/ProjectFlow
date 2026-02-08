# app/communication/video_conferencing.py
"""
Video Conferencing Integration
WebRTC-based video conferencing with recording, screen sharing, and analytics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid


class MeetingStatus(Enum):
    """Meeting status."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    ENDED = "ended"


class ParticipantRole(Enum):
    """Participant role in meeting."""
    HOST = "host"
    PRESENTER = "presenter"
    PARTICIPANT = "participant"


@dataclass
class Meeting:
    """Video conference meeting."""
    meeting_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    host_id: str = ""
    tenant_id: str = ""
    status: MeetingStatus = MeetingStatus.SCHEDULED
    meeting_url: str = ""
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_minutes: int = 0
    max_participants: int = 100
    recording_enabled: bool = True
    screen_share_enabled: bool = True
    chat_enabled: bool = True
    
    def to_dict(self) -> Dict:
        return {
            'meeting_id': self.meeting_id,
            'title': self.title,
            'host_id': self.host_id,
            'status': self.status.value,
            'meeting_url': self.meeting_url,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'max_participants': self.max_participants
        }


@dataclass
class Participant:
    """Meeting participant."""
    participant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    meeting_id: str = ""
    user_id: str = ""
    name: str = ""
    email: str = ""
    role: ParticipantRole = ParticipantRole.PARTICIPANT
    joined_at: datetime = field(default_factory=datetime.utcnow)
    left_at: Optional[datetime] = None
    video_enabled: bool = True
    audio_enabled: bool = True
    screen_shared: bool = False
    
    def to_dict(self) -> Dict:
        duration = 0
        if self.left_at:
            duration = int((self.left_at - self.joined_at).total_seconds() / 60)
        else:
            duration = int((datetime.utcnow() - self.joined_at).total_seconds() / 60)
        
        return {
            'participant_id': self.participant_id,
            'user_id': self.user_id,
            'name': self.name,
            'role': self.role.value,
            'joined_at': self.joined_at.isoformat(),
            'duration_minutes': duration,
            'video_enabled': self.video_enabled,
            'audio_enabled': self.audio_enabled,
            'screen_shared': self.screen_shared
        }


@dataclass
class Recording:
    """Meeting recording."""
    recording_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    meeting_id: str = ""
    filename: str = ""
    file_size_mb: int = 0
    duration_minutes: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    download_url: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'recording_id': self.recording_id,
            'meeting_id': self.meeting_id,
            'filename': self.filename,
            'file_size_mb': self.file_size_mb,
            'duration_minutes': self.duration_minutes,
            'created_at': self.created_at.isoformat(),
            'download_url': self.download_url
        }


@dataclass
class ChatMessage:
    """Meeting chat message."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    meeting_id: str = ""
    sender_id: str = ""
    sender_name: str = ""
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'message_id': self.message_id,
            'sender_name': self.sender_name,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }


class VideoConferencingEngine:
    """
    Manages video conferencing meetings and WebRTC infrastructure.
    """
    
    def __init__(self):
        """Initialize video conferencing engine."""
        self.meetings: Dict[str, Meeting] = {}
        self.participants: Dict[str, Participant] = {}
        self.meeting_participants: Dict[str, List[str]] = {}
        self.recordings: Dict[str, Recording] = {}
        self.chat_messages: Dict[str, List[str]] = {}
        self.stats = {
            'total_meetings': 0,
            'meetings_in_progress': 0,
            'total_participants': 0,
            'total_recordings': 0
        }
    
    def create_meeting(self, host_id: str, tenant_id: str, title: str,
                      start_time: datetime = None) -> Meeting:
        """Create new meeting."""
        meeting = Meeting(
            host_id=host_id,
            tenant_id=tenant_id,
            title=title,
            start_time=start_time or datetime.utcnow(),
            status=MeetingStatus.SCHEDULED,
            meeting_url=f"https://meet.app/{uuid.uuid4().hex}"
        )
        
        self.meetings[meeting.meeting_id] = meeting
        self.meeting_participants[meeting.meeting_id] = []
        self.chat_messages[meeting.meeting_id] = []
        
        self.stats['total_meetings'] += 1
        
        return meeting
    
    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """Get meeting details."""
        return self.meetings.get(meeting_id)
    
    def start_meeting(self, meeting_id: str) -> bool:
        """Start meeting."""
        if meeting_id not in self.meetings:
            return False
        
        meeting = self.meetings[meeting_id]
        meeting.status = MeetingStatus.IN_PROGRESS
        meeting.start_time = datetime.utcnow()
        
        self.stats['meetings_in_progress'] += 1
        return True
    
    def end_meeting(self, meeting_id: str) -> bool:
        """End meeting."""
        if meeting_id not in self.meetings:
            return False
        
        meeting = self.meetings[meeting_id]
        meeting.status = MeetingStatus.ENDED
        meeting.end_time = datetime.utcnow()
        meeting.duration_minutes = int((meeting.end_time - meeting.start_time).total_seconds() / 60)
        
        self.stats['meetings_in_progress'] = max(0, self.stats['meetings_in_progress'] - 1)
        
        return True
    
    def add_participant(self, meeting_id: str, user_id: str, name: str,
                       email: str = "", role: str = "participant") -> Optional[Participant]:
        """Add participant to meeting."""
        if meeting_id not in self.meetings:
            return None
        
        try:
            role_enum = ParticipantRole[role.upper()]
        except KeyError:
            role_enum = ParticipantRole.PARTICIPANT
        
        participant = Participant(
            meeting_id=meeting_id,
            user_id=user_id,
            name=name,
            email=email,
            role=role_enum
        )
        
        self.participants[participant.participant_id] = participant
        self.meeting_participants[meeting_id].append(participant.participant_id)
        
        self.stats['total_participants'] += 1
        
        return participant
    
    def remove_participant(self, participant_id: str) -> bool:
        """Remove participant from meeting."""
        if participant_id not in self.participants:
            return False
        
        participant = self.participants[participant_id]
        participant.left_at = datetime.utcnow()
        
        return True
    
    def get_meeting_participants(self, meeting_id: str) -> List[Dict]:
        """Get all participants in meeting."""
        if meeting_id not in self.meeting_participants:
            return []
        
        return [self.participants[pid].to_dict() for pid in self.meeting_participants[meeting_id]
               if pid in self.participants]
    
    def toggle_screen_share(self, participant_id: str, enabled: bool) -> bool:
        """Toggle screen sharing for participant."""
        if participant_id not in self.participants:
            return False
        
        self.participants[participant_id].screen_shared = enabled
        return True
    
    def toggle_audio(self, participant_id: str, enabled: bool) -> bool:
        """Toggle audio for participant."""
        if participant_id not in self.participants:
            return False
        
        self.participants[participant_id].audio_enabled = enabled
        return True
    
    def toggle_video(self, participant_id: str, enabled: bool) -> bool:
        """Toggle video for participant."""
        if participant_id not in self.participants:
            return False
        
        self.participants[participant_id].video_enabled = enabled
        return True
    
    def add_chat_message(self, meeting_id: str, sender_id: str, sender_name: str,
                        content: str) -> Optional[ChatMessage]:
        """Add chat message to meeting."""
        if meeting_id not in self.meetings:
            return None
        
        message = ChatMessage(
            meeting_id=meeting_id,
            sender_id=sender_id,
            sender_name=sender_name,
            content=content
        )
        
        if meeting_id not in self.chat_messages:
            self.chat_messages[meeting_id] = []
        
        self.chat_messages[meeting_id].append(message.message_id)
        
        return message
    
    def get_chat_messages(self, meeting_id: str) -> List[Dict]:
        """Get chat messages from meeting."""
        if meeting_id not in self.chat_messages:
            return []
        
        # Return last 50 messages
        message_ids = self.chat_messages[meeting_id][-50:]
        return [self.participants[mid].to_dict() if mid in self.participants 
               else {} for mid in message_ids]
    
    def start_recording(self, meeting_id: str) -> Optional[Recording]:
        """Start recording meeting."""
        if meeting_id not in self.meetings:
            return None
        
        recording = Recording(
            meeting_id=meeting_id,
            filename=f"meeting_{meeting_id}_{datetime.utcnow().timestamp()}.mp4"
        )
        
        self.recordings[recording.recording_id] = recording
        self.stats['total_recordings'] += 1
        
        return recording
    
    def get_recordings(self, meeting_id: str) -> List[Dict]:
        """Get recordings for meeting."""
        recordings = []
        
        for recording in self.recordings.values():
            if recording.meeting_id == meeting_id:
                recordings.append(recording.to_dict())
        
        return recordings
    
    def get_meeting_analytics(self, meeting_id: str) -> Dict:
        """Get analytics for meeting."""
        if meeting_id not in self.meetings:
            return {'error': 'Meeting not found'}
        
        meeting = self.meetings[meeting_id]
        participants = self.get_meeting_participants(meeting_id)
        recordings = self.get_recordings(meeting_id)
        
        return {
            'meeting_id': meeting_id,
            'title': meeting.title,
            'duration_minutes': meeting.duration_minutes,
            'participant_count': len(participants),
            'recordings_count': len(recordings),
            'status': meeting.status.value
        }
    
    def get_stats(self) -> Dict:
        """Get video conferencing statistics."""
        return {
            'total_meetings': self.stats['total_meetings'],
            'meetings_in_progress': self.stats['meetings_in_progress'],
            'total_participants': self.stats['total_participants'],
            'total_recordings': self.stats['total_recordings']
        }


# Global video conferencing engine
video_conferencing_engine = VideoConferencingEngine()

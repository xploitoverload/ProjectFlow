# app/routes/video_conferencing_routes.py
"""
Video Conferencing API Routes
Meeting management, participant management, and recording endpoints.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime
from app.communication.video_conferencing import video_conferencing_engine


def require_auth(f):
    """Require authentication for video conferencing endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


video_bp = Blueprint('video', __name__, url_prefix='/api/v1/video')


@video_bp.route('/meetings/create', methods=['POST'])
@require_auth
def create_meeting():
    """Create new video meeting."""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        meeting = video_conferencing_engine.create_meeting(
            host_id=user_id,
            tenant_id=data.get('tenant_id', ''),
            title=data.get('title', ''),
            start_time=datetime.fromisoformat(data.get('start_time')) if data.get('start_time') else None
        )
        
        return jsonify({
            'status': 'success',
            'meeting': meeting.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/meetings/<meeting_id>', methods=['GET'])
@require_auth
def get_meeting(meeting_id):
    """Get meeting details."""
    try:
        meeting = video_conferencing_engine.get_meeting(meeting_id)
        
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        return jsonify({
            'status': 'success',
            'meeting': meeting.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/meetings/<meeting_id>/start', methods=['POST'])
@require_auth
def start_meeting(meeting_id):
    """Start meeting."""
    try:
        success = video_conferencing_engine.start_meeting(meeting_id)
        
        if not success:
            return jsonify({'error': 'Failed to start meeting'}), 400
        
        meeting = video_conferencing_engine.get_meeting(meeting_id)
        
        return jsonify({
            'status': 'success',
            'meeting': meeting.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/meetings/<meeting_id>/end', methods=['POST'])
@require_auth
def end_meeting(meeting_id):
    """End meeting."""
    try:
        success = video_conferencing_engine.end_meeting(meeting_id)
        
        if not success:
            return jsonify({'error': 'Failed to end meeting'}), 400
        
        meeting = video_conferencing_engine.get_meeting(meeting_id)
        
        return jsonify({
            'status': 'success',
            'meeting': meeting.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/meetings/<meeting_id>/participants/add', methods=['POST'])
@require_auth
def add_participant(meeting_id):
    """Add participant to meeting."""
    try:
        data = request.get_json()
        
        participant = video_conferencing_engine.add_participant(
            meeting_id=meeting_id,
            user_id=data.get('user_id', ''),
            name=data.get('name', ''),
            email=data.get('email', ''),
            role=data.get('role', 'participant')
        )
        
        if not participant:
            return jsonify({'error': 'Meeting not found'}), 404
        
        return jsonify({
            'status': 'success',
            'participant': participant.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/meetings/<meeting_id>/participants', methods=['GET'])
@require_auth
def get_meeting_participants(meeting_id):
    """Get all participants in meeting."""
    try:
        participants = video_conferencing_engine.get_meeting_participants(meeting_id)
        
        return jsonify({
            'status': 'success',
            'participants': participants,
            'total': len(participants)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/participants/<participant_id>/remove', methods=['POST'])
@require_auth
def remove_participant(participant_id):
    """Remove participant from meeting."""
    try:
        success = video_conferencing_engine.remove_participant(participant_id)
        
        if not success:
            return jsonify({'error': 'Participant not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Participant removed'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/participants/<participant_id>/screen-share', methods=['PUT'])
@require_auth
def toggle_screen_share(participant_id):
    """Toggle screen sharing."""
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        success = video_conferencing_engine.toggle_screen_share(participant_id, enabled)
        
        if not success:
            return jsonify({'error': 'Participant not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': f'Screen share {"enabled" if enabled else "disabled"}'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/participants/<participant_id>/audio', methods=['PUT'])
@require_auth
def toggle_audio(participant_id):
    """Toggle audio."""
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        success = video_conferencing_engine.toggle_audio(participant_id, enabled)
        
        if not success:
            return jsonify({'error': 'Participant not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': f'Audio {"enabled" if enabled else "disabled"}'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/participants/<participant_id>/video', methods=['PUT'])
@require_auth
def toggle_video(participant_id):
    """Toggle video."""
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        success = video_conferencing_engine.toggle_video(participant_id, enabled)
        
        if not success:
            return jsonify({'error': 'Participant not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': f'Video {"enabled" if enabled else "disabled"}'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/meetings/<meeting_id>/chat', methods=['POST'])
@require_auth
def add_chat_message(meeting_id):
    """Add chat message to meeting."""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        message = video_conferencing_engine.add_chat_message(
            meeting_id=meeting_id,
            sender_id=user_id,
            sender_name=data.get('sender_name', ''),
            content=data.get('content', '')
        )
        
        if not message:
            return jsonify({'error': 'Meeting not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': message.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/meetings/<meeting_id>/chat', methods=['GET'])
@require_auth
def get_chat_messages(meeting_id):
    """Get chat messages from meeting."""
    try:
        messages = video_conferencing_engine.get_chat_messages(meeting_id)
        
        return jsonify({
            'status': 'success',
            'messages': messages,
            'total': len(messages)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/meetings/<meeting_id>/recordings/start', methods=['POST'])
@require_auth
def start_recording(meeting_id):
    """Start recording meeting."""
    try:
        recording = video_conferencing_engine.start_recording(meeting_id)
        
        if not recording:
            return jsonify({'error': 'Meeting not found'}), 404
        
        return jsonify({
            'status': 'success',
            'recording': recording.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/meetings/<meeting_id>/recordings', methods=['GET'])
@require_auth
def get_recordings(meeting_id):
    """Get recordings for meeting."""
    try:
        recordings = video_conferencing_engine.get_recordings(meeting_id)
        
        return jsonify({
            'status': 'success',
            'recordings': recordings,
            'total': len(recordings)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/meetings/<meeting_id>/analytics', methods=['GET'])
@require_auth
def get_meeting_analytics(meeting_id):
    """Get meeting analytics."""
    try:
        analytics = video_conferencing_engine.get_meeting_analytics(meeting_id)
        
        return jsonify({
            'status': 'success',
            'analytics': analytics
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@video_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get video conferencing statistics."""
    try:
        stats = video_conferencing_engine.get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

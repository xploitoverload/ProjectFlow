# app/routes/team_collaboration_routes.py
"""
Team Collaboration AI API Routes
Real-time collaboration, smart suggestions, and team insights.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

from app.ml.team_collaboration import (
    team_collab,
    CollaborationActivityType,
    SuggestionType
)

logger = logging.getLogger(__name__)

# Create blueprint
team_bp = Blueprint('team_collaboration', __name__, url_prefix='/api/v1/team')


def require_auth(f):
    """Require authentication for endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# TEAM MEMBER ROUTES
# ============================================================================

@team_bp.route('/members', methods=['GET', 'POST'])
@require_auth
def team_members():
    """List or add team members."""
    if request.method == 'POST':
        data = request.get_json()
        member = team_collab.add_team_member(
            name=data.get('name'),
            email=data.get('email'),
            role=data.get('role'),
            skills=data.get('skills', [])
        )
        return jsonify(member.to_dict()), 201
    
    # GET - list members
    members = [m.to_dict() for m in team_collab.team_members.values()]
    return jsonify({
        'total': len(members),
        'members': members
    })


@team_bp.route('/members/<member_id>', methods=['GET'])
@require_auth
def get_member(member_id):
    """Get member details."""
    if member_id not in team_collab.team_members:
        return jsonify({'error': 'Member not found'}), 404
    
    member = team_collab.team_members[member_id]
    return jsonify(member.to_dict())


# ============================================================================
# ACTIVITY LOGGING ROUTES
# ============================================================================

@team_bp.route('/activity/log', methods=['POST'])
@require_auth
def log_activity():
    """Log collaboration activity."""
    data = request.get_json()
    member_id = data.get('member_id')
    activity_type_str = data.get('activity_type', 'MESSAGE').upper()
    
    try:
        activity_type = CollaborationActivityType[activity_type_str]
    except KeyError:
        return jsonify({'error': 'Invalid activity_type'}), 400
    
    activity = team_collab.log_activity(
        member_id=member_id,
        activity_type=activity_type,
        resource_id=data.get('resource_id'),
        resource_type=data.get('resource_type'),
        details=data.get('details')
    )
    
    return jsonify(activity.to_dict()), 201


@team_bp.route('/activity/<member_id>', methods=['GET'])
@require_auth
def get_member_activity(member_id):
    """Get member's activity timeline."""
    days = request.args.get('days', 7, type=int)
    activities = team_collab.get_member_activity_timeline(member_id, days)
    
    return jsonify({
        'member_id': member_id,
        'period_days': days,
        'total_activities': len(activities),
        'activities': activities
    })


# ============================================================================
# SMART SUGGESTIONS ROUTES
# ============================================================================

@team_bp.route('/suggest/assignment', methods=['POST'])
@require_auth
def suggest_assignment():
    """Get AI suggestion for task assignment."""
    data = request.get_json()
    task_description = data.get('task_description')
    required_skills = data.get('required_skills', [])
    
    if not task_description:
        return jsonify({'error': 'task_description required'}), 400
    
    suggestion = team_collab.suggest_team_member_for_task(task_description, required_skills)
    return jsonify(suggestion.to_dict()), 201


@team_bp.route('/suggest/meeting-time', methods=['POST'])
@require_auth
def suggest_meeting():
    """Get AI suggestion for meeting time."""
    data = request.get_json()
    member_ids = data.get('member_ids', [])
    duration = data.get('duration_minutes', 60)
    
    if not member_ids:
        return jsonify({'error': 'member_ids required'}), 400
    
    suggestion = team_collab.suggest_meeting_time(member_ids, duration)
    return jsonify(suggestion.to_dict()), 201


@team_bp.route('/suggest/expert', methods=['POST'])
@require_auth
def suggest_expert():
    """Get AI suggestion for expert on topic."""
    data = request.get_json()
    topic = data.get('topic')
    member_ids = data.get('member_ids')
    
    if not topic:
        return jsonify({'error': 'topic required'}), 400
    
    suggestion = team_collab.suggest_expert(topic, member_ids)
    return jsonify(suggestion.to_dict()), 201


@team_bp.route('/suggestion/<suggestion_id>/accept', methods=['POST'])
@require_auth
def accept_suggestion(suggestion_id):
    """Accept a suggestion."""
    success = team_collab.accept_suggestion(suggestion_id)
    
    if not success:
        return jsonify({'error': 'Suggestion not found'}), 404
    
    return jsonify({
        'status': 'success',
        'suggestion_id': suggestion_id,
        'accepted': True
    })


# ============================================================================
# INSIGHTS & ANALYTICS ROUTES
# ============================================================================

@team_bp.route('/insights/member/<member_id>', methods=['GET'])
@require_auth
def member_insights(member_id):
    """Get insights for specific member."""
    insights = team_collab.get_collaboration_insights(member_id)
    
    if 'error' in insights:
        return jsonify(insights), 404
    
    return jsonify(insights)


@team_bp.route('/insights/team', methods=['GET'])
@require_auth
def team_insights():
    """Get team collaboration insights."""
    insights = team_collab.get_collaboration_insights()
    return jsonify(insights)


@team_bp.route('/stats', methods=['GET'])
@require_auth
def team_stats():
    """Get team statistics."""
    stats = team_collab.get_team_stats()
    return jsonify(stats)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@team_bp.route('/health', methods=['GET'])
def health():
    """Health check for team collaboration."""
    stats = team_collab.get_team_stats()
    return jsonify({
        'status': 'healthy',
        'stats': stats
    })

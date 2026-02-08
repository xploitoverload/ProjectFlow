# app/routes/integrations_routes.py
"""
Third-Party Integration API Routes
Endpoints for managing Slack, GitHub, Jira, webhooks, and sync operations.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from typing import Dict, Any
import logging

from app.integrations import (
    SlackIntegration,
    GitHubIntegration,
    JiraIntegration,
    WebhookManager,
    SyncManager
)

logger = logging.getLogger(__name__)

# Create blueprint
integrations_bp = Blueprint('integrations', __name__, url_prefix='/api/v1/integrations')

# Initialize integration services (in production, these would be injected)
slack_service = SlackIntegration()
github_service = GitHubIntegration()
jira_service = JiraIntegration()
webhook_manager = WebhookManager()
sync_manager = SyncManager()


def require_auth(f):
    """Require authentication for endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In production, implement proper auth checking
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# SLACK INTEGRATION ROUTES
# ============================================================================

@integrations_bp.route('/slack/config', methods=['GET', 'POST'])
@require_auth
def slack_config():
    """Get or update Slack configuration."""
    if request.method == 'POST':
        data = request.get_json()
        slack_service.config.workspace_url = data.get('workspace_url')
        slack_service.config.token = data.get('token')
        slack_service.config.bot_user_id = data.get('bot_user_id')
        return jsonify({
            'status': 'success',
            'message': 'Slack configuration updated'
        })
    
    return jsonify({
        'workspace_url': slack_service.config.workspace_url,
        'bot_user_id': slack_service.config.bot_user_id
    })


@integrations_bp.route('/slack/send-message', methods=['POST'])
@require_auth
def slack_send_message():
    """Send Slack message."""
    data = request.get_json()
    text = data.get('text')
    channel = data.get('channel')
    
    result = slack_service.send_message(text, channel)
    return jsonify(result), 200 if result.get('status') == 'sent' else 400


@integrations_bp.route('/slack/issue-notification', methods=['POST'])
@require_auth
def slack_issue_notification():
    """Send issue notification to Slack."""
    data = request.get_json()
    issue_title = data.get('issue_title')
    issue_description = data.get('issue_description')
    priority = data.get('priority', 'medium')
    
    result = slack_service.send_issue_notification(
        issue_title, issue_description, priority
    )
    return jsonify(result), 200 if result.get('status') == 'sent' else 400


@integrations_bp.route('/slack/project-update', methods=['POST'])
@require_auth
def slack_project_update():
    """Send project update to Slack."""
    data = request.get_json()
    project_name = data.get('project_name')
    update_text = data.get('update_text')
    milestone = data.get('milestone')
    
    result = slack_service.send_project_update(project_name, update_text, milestone)
    return jsonify(result), 200 if result.get('status') == 'sent' else 400


@integrations_bp.route('/slack/stats', methods=['GET'])
@require_auth
def slack_stats():
    """Get Slack integration statistics."""
    stats = slack_service.get_stats()
    return jsonify(stats)


# ============================================================================
# GITHUB INTEGRATION ROUTES
# ============================================================================

@integrations_bp.route('/github/config', methods=['GET', 'POST'])
@require_auth
def github_config():
    """Get or update GitHub configuration."""
    if request.method == 'POST':
        data = request.get_json()
        github_service.config.repo_url = data.get('repo_url')
        github_service.config.token = data.get('token')
        github_service.config.owner = data.get('owner')
        return jsonify({
            'status': 'success',
            'message': 'GitHub configuration updated'
        })
    
    return jsonify({
        'repo_url': github_service.config.repo_url,
        'owner': github_service.config.owner
    })


@integrations_bp.route('/github/webhook', methods=['POST'])
@require_auth
def github_webhook():
    """Handle GitHub webhook."""
    data = request.get_json()
    result = github_service.handle_webhook(data)
    return jsonify(result)


@integrations_bp.route('/github/sync-commits', methods=['POST'])
@require_auth
def github_sync_commits():
    """Sync commits from GitHub."""
    result = github_service.sync_commits()
    return jsonify(result)


@integrations_bp.route('/github/create-issue', methods=['POST'])
@require_auth
def github_create_issue():
    """Create GitHub issue."""
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    labels = data.get('labels', [])
    
    result = github_service.create_issue(title, description, labels)
    return jsonify(result)


@integrations_bp.route('/github/stats', methods=['GET'])
@require_auth
def github_stats():
    """Get GitHub integration statistics."""
    stats = github_service.get_stats()
    return jsonify(stats)


# ============================================================================
# JIRA INTEGRATION ROUTES
# ============================================================================

@integrations_bp.route('/jira/config', methods=['GET', 'POST'])
@require_auth
def jira_config():
    """Get or update Jira configuration."""
    if request.method == 'POST':
        data = request.get_json()
        jira_service.config.instance_url = data.get('instance_url')
        jira_service.config.username = data.get('username')
        jira_service.config.api_token = data.get('api_token')
        jira_service.config.project_key = data.get('project_key')
        return jsonify({
            'status': 'success',
            'message': 'Jira configuration updated'
        })
    
    return jsonify({
        'instance_url': jira_service.config.instance_url,
        'project_key': jira_service.config.project_key
    })


@integrations_bp.route('/jira/sync-issue', methods=['POST'])
@require_auth
def jira_sync_issue():
    """Sync Jira issue."""
    data = request.get_json()
    issue_key = data.get('issue_key')
    
    result = jira_service.sync_issue(issue_key)
    return jsonify(result)


@integrations_bp.route('/jira/issues', methods=['GET'])
@require_auth
def jira_get_issues():
    """Get Jira issues."""
    jql = request.args.get('jql', 'project = {}'.format(jira_service.config.project_key))
    result = jira_service.get_jira_issues(jql)
    return jsonify(result)


@integrations_bp.route('/jira/update-status', methods=['POST'])
@require_auth
def jira_update_status():
    """Update Jira issue status."""
    data = request.get_json()
    issue_key = data.get('issue_key')
    new_status = data.get('new_status')
    
    result = jira_service.update_status(issue_key, new_status)
    return jsonify(result)


@integrations_bp.route('/jira/stats', methods=['GET'])
@require_auth
def jira_stats():
    """Get Jira integration statistics."""
    stats = jira_service.get_stats()
    return jsonify(stats)


# ============================================================================
# WEBHOOK MANAGEMENT ROUTES
# ============================================================================

@integrations_bp.route('/webhooks', methods=['GET', 'POST'])
@require_auth
def webhooks():
    """List or create webhooks."""
    if request.method == 'POST':
        data = request.get_json()
        event_type = data.get('event_type')
        target_url = data.get('target_url')
        
        webhook = webhook_manager.register_webhook(
            event_type=event_type,
            target_url=target_url,
            active=True
        )
        return jsonify(webhook.to_dict()), 201
    
    webhooks_list = [w.to_dict() for w in webhook_manager.webhooks.values()]
    return jsonify({'webhooks': webhooks_list})


@integrations_bp.route('/webhooks/<webhook_id>', methods=['GET', 'DELETE'])
@require_auth
def webhook_detail(webhook_id):
    """Get or delete webhook."""
    if request.method == 'DELETE':
        webhook_manager.delete_webhook(webhook_id)
        return jsonify({'status': 'success'}), 204
    
    if webhook_id in webhook_manager.webhooks:
        return jsonify(webhook_manager.webhooks[webhook_id].to_dict())
    
    return jsonify({'error': 'Webhook not found'}), 404


@integrations_bp.route('/webhooks/<webhook_id>/test', methods=['POST'])
@require_auth
def webhook_test(webhook_id):
    """Test webhook delivery."""
    if webhook_id not in webhook_manager.webhooks:
        return jsonify({'error': 'Webhook not found'}), 404
    
    webhook = webhook_manager.webhooks[webhook_id]
    result = webhook_manager.deliver(webhook, {'test': True})
    return jsonify(result)


@integrations_bp.route('/webhooks/handlers', methods=['GET', 'POST'])
@require_auth
def webhook_handlers():
    """Register webhook handlers."""
    if request.method == 'POST':
        data = request.get_json()
        event_type = data.get('event_type')
        handler_name = data.get('handler_name')
        
        webhook_manager.register_handler(event_type, handler_name)
        return jsonify({'status': 'success'}), 201
    
    handlers = {e.value: len(webhook_manager.handlers.get(e.value, []))
               for e in webhook_manager.handlers.keys()}
    return jsonify({'handlers': handlers})


@integrations_bp.route('/webhooks/stats', methods=['GET'])
@require_auth
def webhooks_stats():
    """Get webhook statistics."""
    stats = webhook_manager.get_stats()
    return jsonify(stats)


# ============================================================================
# SYNC MANAGEMENT ROUTES
# ============================================================================

@integrations_bp.route('/sync/jobs', methods=['GET', 'POST'])
@require_auth
def sync_jobs():
    """List or schedule sync jobs."""
    if request.method == 'POST':
        data = request.get_json()
        source_system = data.get('source_system')
        target_system = data.get('target_system')
        direction = data.get('direction', 'bidirectional')
        
        job = sync_manager.schedule_sync(
            source_system=source_system,
            target_system=target_system,
            direction=direction,
            schedule=data.get('schedule')
        )
        return jsonify(job.to_dict()), 201
    
    jobs = sync_manager.get_sync_jobs()
    return jsonify({'jobs': [j.to_dict() for j in jobs]})


@integrations_bp.route('/sync/execute', methods=['POST'])
@require_auth
def sync_execute():
    """Execute synchronization."""
    data = request.get_json()
    source_system = data.get('source_system')
    target_system = data.get('target_system')
    
    result = sync_manager.sync(source_system, target_system)
    return jsonify(result)


@integrations_bp.route('/sync/schedule', methods=['GET'])
@require_auth
def sync_schedule():
    """Get sync schedule."""
    schedule = sync_manager.get_sync_schedule()
    return jsonify(schedule)


@integrations_bp.route('/sync/last/<source>/<target>', methods=['GET'])
@require_auth
def sync_last(source, target):
    """Get last sync details."""
    last_sync = sync_manager.get_last_sync(source, target)
    if last_sync:
        return jsonify(last_sync.to_dict())
    return jsonify({'error': 'No sync found'}), 404


@integrations_bp.route('/sync/stats', methods=['GET'])
@require_auth
def sync_stats():
    """Get sync statistics."""
    stats = sync_manager.get_stats()
    return jsonify(stats)


# ============================================================================
# HEALTH & STATUS
# ============================================================================

@integrations_bp.route('/health', methods=['GET'])
def integrations_health():
    """Health check for integrations."""
    return jsonify({
        'status': 'healthy',
        'services': {
            'slack': {'configured': slack_service.config.workspace_url is not None},
            'github': {'configured': github_service.config.repo_url is not None},
            'jira': {'configured': jira_service.config.instance_url is not None},
            'webhooks': {'active': len(webhook_manager.webhooks)},
            'sync': {'jobs': len(sync_manager.sync_jobs)}
        }
    })

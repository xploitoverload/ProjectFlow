# app/routes/integrations_routes.py
"""
Third-Party Integration API Routes
Endpoints for managing Slack, GitHub, Jira, webhooks, and sync operations.
All endpoints require authentication and handle async operations safely.
"""

import asyncio
import inspect
import logging
from typing import Dict, Any
from flask import Blueprint, request, jsonify

from app.middleware.auth import api_auth_required
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

# Initialize integration services
slack_service = SlackIntegration()
github_service = GitHubIntegration()
jira_service = JiraIntegration()
webhook_manager = WebhookManager()
sync_manager = SyncManager()


def _run_async(coro_or_val):
    """Safely execute coroutines from synchronous Flask routes."""
    if inspect.iscoroutine(coro_or_val):
        try:
            return asyncio.run(coro_or_val)
        except RuntimeError:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, coro_or_val).result()
    return coro_or_val


# ============================================================================
# SLACK INTEGRATION ROUTES
# ============================================================================

@integrations_bp.route('/slack/config', methods=['GET', 'POST'])
@api_auth_required
def slack_config():
    """Get or update Slack configuration."""
    if request.method == 'POST':
        data = request.get_json() or {}
        webhook_url = data.get('webhook_url') or data.get('workspace_url', '')
        bot_token = data.get('token') or data.get('bot_token')
        channel = data.get('channel', '#general')
        
        slack_service.configure(
            webhook_url=webhook_url,
            bot_token=bot_token,
            channel=channel
        )
        return jsonify({
            'status': 'success',
            'message': 'Slack configuration updated'
        })
    
    return jsonify({
        'is_configured': slack_service.is_configured,
        'webhook_url': slack_service.config.webhook_url if slack_service.config else None,
        'channel': slack_service.config.channel if slack_service.config else None
    })


@integrations_bp.route('/slack/send-message', methods=['POST'])
@api_auth_required
def slack_send_message():
    """Send Slack message."""
    data = request.get_json() or {}
    text = data.get('text', '')
    channel = data.get('channel')
    
    result = _run_async(slack_service.send_message(text, channel))
    return jsonify(result), 200 if isinstance(result, dict) and result.get('status') == 'sent' else 400


@integrations_bp.route('/slack/issue-notification', methods=['POST'])
@api_auth_required
def slack_issue_notification():
    """Send issue notification to Slack."""
    data = request.get_json() or {}
    issue_data = {
        'id': data.get('issue_id') or data.get('id', 'N/A'),
        'title': data.get('issue_title') or data.get('title', ''),
        'status': data.get('status', 'Open'),
        'priority': data.get('priority', 'medium')
    }
    
    result = _run_async(slack_service.send_issue_notification(issue_data))
    return jsonify(result), 200 if isinstance(result, dict) and result.get('status') == 'sent' else 400


@integrations_bp.route('/slack/project-update', methods=['POST'])
@api_auth_required
def slack_project_update():
    """Send project update to Slack."""
    data = request.get_json() or {}
    project_data = {
        'name': data.get('project_name') or data.get('name', ''),
        'completion_rate': data.get('completion_rate', 0),
        'members': data.get('members', [])
    }
    
    result = _run_async(slack_service.send_project_update(project_data))
    return jsonify(result), 200 if isinstance(result, dict) and result.get('status') == 'sent' else 400


@integrations_bp.route('/slack/stats', methods=['GET'])
@api_auth_required
def slack_stats():
    """Get Slack integration statistics."""
    stats = slack_service.get_stats()
    return jsonify(stats)


# ============================================================================
# GITHUB INTEGRATION ROUTES
# ============================================================================

@integrations_bp.route('/github/config', methods=['GET', 'POST'])
@api_auth_required
def github_config():
    """Get or update GitHub configuration."""
    if request.method == 'POST':
        data = request.get_json() or {}
        personal_token = data.get('token') or data.get('personal_token', '')
        repo_owner = data.get('owner') or data.get('repo_owner', '')
        repo_name = data.get('repo') or data.get('repo_name', '')
        webhook_secret = data.get('webhook_secret')
        
        github_service.configure(
            personal_token=personal_token,
            repo_owner=repo_owner,
            repo_name=repo_name,
            webhook_secret=webhook_secret
        )
        return jsonify({
            'status': 'success',
            'message': 'GitHub configuration updated'
        })
    
    return jsonify({
        'is_configured': github_service.is_configured,
        'repo_owner': github_service.config.repo_owner if github_service.config else None,
        'repo_name': github_service.config.repo_name if github_service.config else None
    })


@integrations_bp.route('/github/webhook', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook."""
    data = request.get_json() or {}
    result = github_service.handle_webhook(data)
    return jsonify(result)


@integrations_bp.route('/github/sync-commits', methods=['POST'])
@api_auth_required
def github_sync_commits():
    """Sync commits from GitHub."""
    result = _run_async(github_service.sync_commits())
    return jsonify(result)


@integrations_bp.route('/github/create-issue', methods=['POST'])
@api_auth_required
def github_create_issue():
    """Create GitHub issue."""
    data = request.get_json() or {}
    title = data.get('title', '')
    description = data.get('description', '')
    labels = data.get('labels', [])
    
    result = _run_async(github_service.create_issue(title, description, labels))
    return jsonify(result)


@integrations_bp.route('/github/stats', methods=['GET'])
@api_auth_required
def github_stats():
    """Get GitHub integration statistics."""
    stats = github_service.get_stats()
    return jsonify(stats)


# ============================================================================
# JIRA INTEGRATION ROUTES
# ============================================================================

@integrations_bp.route('/jira/config', methods=['GET', 'POST'])
@api_auth_required
def jira_config():
    """Get or update Jira configuration."""
    if request.method == 'POST':
        data = request.get_json() or {}
        url = data.get('instance_url') or data.get('url', '')
        username = data.get('username', '')
        api_token = data.get('api_token', '')
        project_key = data.get('project_key', '')
        
        jira_service.configure(
            url=url,
            username=username,
            api_token=api_token,
            project_key=project_key
        )
        return jsonify({
            'status': 'success',
            'message': 'Jira configuration updated'
        })
    
    return jsonify({
        'is_configured': jira_service.is_configured,
        'instance_url': jira_service.config.url if jira_service.config else None,
        'project_key': jira_service.config.project_key if jira_service.config else None
    })


@integrations_bp.route('/jira/sync-issue', methods=['POST'])
@api_auth_required
def jira_sync_issue():
    """Sync Jira issue."""
    data = request.get_json() or {}
    issue_data = {'key': data.get('issue_key', '')}
    
    result = _run_async(jira_service.sync_issue(issue_data))
    return jsonify(result)


@integrations_bp.route('/jira/issues', methods=['GET'])
@api_auth_required
def jira_get_issues():
    """Get Jira issues."""
    project_key = jira_service.config.project_key if jira_service.config else ''
    jql = request.args.get('jql', f'project = {project_key}' if project_key else '')
    result = _run_async(jira_service.get_jira_issues(jql))
    return jsonify(result)


@integrations_bp.route('/jira/update-status', methods=['POST'])
@api_auth_required
def jira_update_status():
    """Update Jira issue status."""
    data = request.get_json() or {}
    issue_key = data.get('issue_key', '')
    new_status = data.get('new_status', '')
    
    result = _run_async(jira_service.update_status(issue_key, new_status))
    return jsonify(result)


@integrations_bp.route('/jira/stats', methods=['GET'])
@api_auth_required
def jira_stats():
    """Get Jira integration statistics."""
    stats = jira_service.get_stats()
    return jsonify(stats)


# ============================================================================
# WEBHOOK MANAGEMENT ROUTES
# ============================================================================

@integrations_bp.route('/webhooks', methods=['GET', 'POST'])
@api_auth_required
def webhooks():
    """List or create webhooks."""
    if request.method == 'POST':
        data = request.get_json() or {}
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
@api_auth_required
def webhook_detail(webhook_id):
    """Get or delete webhook."""
    if request.method == 'DELETE':
        webhook_manager.delete_webhook(webhook_id)
        return jsonify({'status': 'success'}), 204
    
    if webhook_id in webhook_manager.webhooks:
        return jsonify(webhook_manager.webhooks[webhook_id].to_dict())
    
    return jsonify({'error': 'Webhook not found'}), 404


@integrations_bp.route('/webhooks/<webhook_id>/test', methods=['POST'])
@api_auth_required
def webhook_test(webhook_id):
    """Test webhook delivery."""
    if webhook_id not in webhook_manager.webhooks:
        return jsonify({'error': 'Webhook not found'}), 404
    
    result = _run_async(webhook_manager.deliver(webhook_id, {'test': True}))
    return jsonify(result)


@integrations_bp.route('/webhooks/handlers', methods=['GET', 'POST'])
@api_auth_required
def webhook_handlers():
    """Register webhook handlers."""
    if request.method == 'POST':
        data = request.get_json() or {}
        event_type = data.get('event_type')
        handler_name = data.get('handler_name')
        
        webhook_manager.register_handler(event_type, handler_name)
        return jsonify({'status': 'success'}), 201
    
    handlers = {str(e): len(webhook_manager.handlers.get(e, []))
                for e in webhook_manager.handlers.keys()}
    return jsonify({'handlers': handlers})


@integrations_bp.route('/webhooks/stats', methods=['GET'])
@api_auth_required
def webhooks_stats():
    """Get webhook statistics."""
    stats = webhook_manager.get_stats()
    return jsonify(stats)


# ============================================================================
# SYNC MANAGEMENT ROUTES
# ============================================================================

@integrations_bp.route('/sync/jobs', methods=['GET', 'POST'])
@api_auth_required
def sync_jobs():
    """List or schedule sync jobs."""
    if request.method == 'POST':
        data = request.get_json() or {}
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
@api_auth_required
def sync_execute():
    """Execute synchronization."""
    data = request.get_json() or {}
    source_system = data.get('source_system')
    target_system = data.get('target_system')
    
    result = _run_async(sync_manager.sync(source_system, target_system))
    return jsonify(result)


@integrations_bp.route('/sync/schedule', methods=['GET'])
@api_auth_required
def sync_schedule():
    """Get sync schedule."""
    schedule = sync_manager.get_sync_schedule()
    return jsonify(schedule)


@integrations_bp.route('/sync/last/<source>/<target>', methods=['GET'])
@api_auth_required
def sync_last(source, target):
    """Get last sync details."""
    last_sync = sync_manager.get_last_sync(source, target)
    if last_sync:
        return jsonify(last_sync.to_dict())
    return jsonify({'error': 'No sync found'}), 404


@integrations_bp.route('/sync/stats', methods=['GET'])
@api_auth_required
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
            'slack': {'configured': slack_service.is_configured},
            'github': {'configured': github_service.is_configured},
            'jira': {'configured': jira_service.is_configured},
            'webhooks': {'active': len(webhook_manager.webhooks)},
            'sync': {'jobs': len(sync_manager.sync_jobs)}
        }
    })

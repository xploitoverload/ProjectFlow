# app/routes/compliance_routes.py
"""
Compliance & Audit API Routes
GDPR, HIPAA, SOC2 compliance and audit logging endpoints.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging
from datetime import datetime

from app.compliance.audit import (
    compliance_engine,
    AuditEventType,
    DataClassification,
    ComplianceFramework
)

logger = logging.getLogger(__name__)

# Create blueprint
compliance_bp = Blueprint('compliance', __name__, url_prefix='/api/v1/compliance')


def require_auth(f):
    """Require authentication for endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# AUDIT LOGGING ROUTES
# ============================================================================

@compliance_bp.route('/audit/log', methods=['POST'])
@require_auth
def log_audit_event():
    """Log audit event."""
    data = request.get_json()
    
    try:
        event_type = AuditEventType[data.get('event_type', 'LOGIN').upper()]
    except KeyError:
        return jsonify({'error': 'Invalid event_type'}), 400
    
    log = compliance_engine.log_event(
        event_type=event_type,
        user_id=data.get('user_id'),
        resource=data.get('resource'),
        action=data.get('action'),
        status=data.get('status', 'success'),
        ip_address=data.get('ip_address'),
        details=data.get('details')
    )
    
    return jsonify(log.to_dict()), 201


@compliance_bp.route('/audit/data-access', methods=['POST'])
@require_auth
def log_data_access():
    """Log data access event."""
    data = request.get_json()
    
    try:
        classification = DataClassification[data.get('classification', 'INTERNAL').upper()]
    except KeyError:
        return jsonify({'error': 'Invalid classification'}), 400
    
    log = compliance_engine.log_data_access(
        user_id=data.get('user_id'),
        resource=data.get('resource'),
        data_type=data.get('data_type'),
        classification=classification
    )
    
    return jsonify(log.to_dict()), 201


@compliance_bp.route('/audit/data-deletion', methods=['POST'])
@require_auth
def log_data_deletion():
    """Log data deletion event."""
    data = request.get_json()
    
    log = compliance_engine.log_data_deletion(
        user_id=data.get('user_id'),
        resource=data.get('resource'),
        reason=data.get('reason', '')
    )
    
    return jsonify(log.to_dict()), 201


@compliance_bp.route('/audit/logs', methods=['GET'])
@require_auth
def get_audit_logs():
    """Get audit logs."""
    event_type_str = request.args.get('event_type')
    event_type = None
    
    if event_type_str:
        try:
            event_type = AuditEventType[event_type_str.upper()]
        except KeyError:
            return jsonify({'error': 'Invalid event_type'}), 400
    
    limit = request.args.get('limit', 1000, type=int)
    logs = compliance_engine.get_audit_logs(event_type=event_type, limit=limit)
    
    return jsonify({
        'total': len(logs),
        'logs': logs
    })


@compliance_bp.route('/audit/user/<user_id>/trail', methods=['GET'])
@require_auth
def get_user_audit_trail(user_id):
    """Get audit trail for specific user."""
    limit = request.args.get('limit', 100, type=int)
    logs = compliance_engine.get_user_audit_trail(user_id, limit)
    
    return jsonify({
        'user_id': user_id,
        'total': len(logs),
        'logs': logs
    })


# ============================================================================
# DATA SUBJECT RIGHTS ROUTES (GDPR)
# ============================================================================

@compliance_bp.route('/gdpr/request', methods=['POST'])
@require_auth
def create_data_subject_request():
    """Create GDPR data subject right request."""
    data = request.get_json()
    user_id = data.get('user_id')
    request_type = data.get('request_type')  # access, deletion, portability, rectification
    reason = data.get('reason', '')
    
    if not user_id or not request_type:
        return jsonify({'error': 'user_id and request_type required'}), 400
    
    req = compliance_engine.request_data_subject_right(user_id, request_type, reason)
    
    return jsonify(req.to_dict()), 201


@compliance_bp.route('/gdpr/request/<request_id>', methods=['GET'])
@require_auth
def get_data_subject_request(request_id):
    """Get data subject request."""
    if request_id not in compliance_engine.data_subject_requests:
        return jsonify({'error': 'Request not found'}), 404
    
    req = compliance_engine.data_subject_requests[request_id]
    return jsonify(req.to_dict())


@compliance_bp.route('/gdpr/request/<request_id>/complete', methods=['POST'])
@require_auth
def complete_data_subject_request(request_id):
    """Mark request as completed."""
    if not compliance_engine.complete_data_subject_request(request_id):
        return jsonify({'error': 'Request not found'}), 404
    
    return jsonify({
        'status': 'success',
        'request_id': request_id,
        'completed_at': datetime.utcnow().isoformat()
    })


@compliance_bp.route('/gdpr/requests', methods=['GET'])
@require_auth
def get_data_subject_requests():
    """Get pending data subject requests."""
    user_id = request.args.get('user_id')
    status = request.args.get('status', 'pending')
    
    reqs = [r for r in compliance_engine.data_subject_requests.values()
            if (not user_id or r.user_id == user_id) and 
               (not status or r.status == status)]
    
    return jsonify({
        'total': len(reqs),
        'requests': [r.to_dict() for r in reqs]
    })


# ============================================================================
# CONSENT MANAGEMENT ROUTES (GDPR)
# ============================================================================

@compliance_bp.route('/consent/give', methods=['POST'])
@require_auth
def give_consent():
    """Record user consent."""
    data = request.get_json()
    user_id = data.get('user_id')
    purpose = data.get('purpose')  # marketing, analytics, processing, etc
    
    if not user_id or not purpose:
        return jsonify({'error': 'user_id and purpose required'}), 400
    
    consent = compliance_engine.give_consent(
        user_id,
        purpose,
        data.get('ip_address', '')
    )
    
    return jsonify(consent.to_dict()), 201


@compliance_bp.route('/consent/withdraw', methods=['POST'])
@require_auth
def withdraw_consent():
    """Withdraw user consent."""
    data = request.get_json()
    user_id = data.get('user_id')
    purpose = data.get('purpose')
    
    if not user_id or not purpose:
        return jsonify({'error': 'user_id and purpose required'}), 400
    
    success = compliance_engine.withdraw_consent(user_id, purpose)
    
    return jsonify({
        'status': 'success' if success else 'not_found',
        'user_id': user_id,
        'purpose': purpose
    }), 200 if success else 404


@compliance_bp.route('/consent/check', methods=['POST'])
@require_auth
def check_consent():
    """Check if user has active consent."""
    data = request.get_json()
    user_id = data.get('user_id')
    purpose = data.get('purpose')
    
    if not user_id or not purpose:
        return jsonify({'error': 'user_id and purpose required'}), 400
    
    has_consent = compliance_engine.check_consent(user_id, purpose)
    
    return jsonify({
        'user_id': user_id,
        'purpose': purpose,
        'has_consent': has_consent
    })


@compliance_bp.route('/consent/list/<user_id>', methods=['GET'])
@require_auth
def list_user_consents(user_id):
    """Get all consents for user."""
    consents = [c.to_dict() for c in compliance_engine.consent_records.values()
               if c.user_id == user_id]
    
    return jsonify({
        'user_id': user_id,
        'total': len(consents),
        'consents': consents
    })


# ============================================================================
# COMPLIANCE REPORTING ROUTES
# ============================================================================

@compliance_bp.route('/report/gdpr', methods=['GET'])
@require_auth
def gdpr_compliance_report():
    """Generate GDPR compliance report."""
    report = compliance_engine.generate_compliance_report(ComplianceFramework.GDPR)
    return jsonify(report)


@compliance_bp.route('/report/hipaa', methods=['GET'])
@require_auth
def hipaa_compliance_report():
    """Generate HIPAA compliance report."""
    report = compliance_engine.generate_compliance_report(ComplianceFramework.HIPAA)
    return jsonify(report)


@compliance_bp.route('/report/soc2', methods=['GET'])
@require_auth
def soc2_compliance_report():
    """Generate SOC2 compliance report."""
    report = compliance_engine.generate_compliance_report(ComplianceFramework.SOC2)
    return jsonify(report)


@compliance_bp.route('/report/all', methods=['GET'])
@require_auth
def all_compliance_reports():
    """Generate all compliance reports."""
    reports = {}
    for framework in [ComplianceFramework.GDPR, ComplianceFramework.HIPAA, ComplianceFramework.SOC2]:
        reports[framework.value] = compliance_engine.generate_compliance_report(framework)
    
    return jsonify(reports)


# ============================================================================
# DATA RETENTION & CLEANUP ROUTES
# ============================================================================

@compliance_bp.route('/cleanup/expired', methods=['POST'])
@require_auth
def cleanup_expired_data():
    """Clean up expired data."""
    result = compliance_engine.cleanup_expired_data()
    return jsonify(result)


@compliance_bp.route('/retention/policies', methods=['GET'])
@require_auth
def get_retention_policies():
    """Get data retention policies."""
    policies = {k: v.value for k, v in compliance_engine.retention_policies.items()}
    return jsonify(policies)


@compliance_bp.route('/retention/policy/<data_type>', methods=['GET'])
@require_auth
def get_retention_policy(data_type):
    """Get specific retention policy."""
    if data_type not in compliance_engine.retention_policies:
        return jsonify({'error': 'Policy not found'}), 404
    
    policy = compliance_engine.retention_policies[data_type]
    return jsonify({
        'data_type': data_type,
        'policy': policy.value
    })


# ============================================================================
# STATISTICS & MONITORING
# ============================================================================

@compliance_bp.route('/stats', methods=['GET'])
@require_auth
def compliance_stats():
    """Get compliance statistics."""
    stats = compliance_engine.get_stats()
    return jsonify(stats)


@compliance_bp.route('/health', methods=['GET'])
def compliance_health():
    """Health check for compliance system."""
    stats = compliance_engine.get_stats()
    return jsonify({
        'status': 'healthy',
        'stats': stats
    })

"""ML/AI Integration Routes - Expose ML functionality via API"""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from datetime import datetime
import logging

from app.ml.ml_pipeline import ml_pipeline
from app.ml.anomaly_detector import anomaly_detector
from app.ml.recommendations import recommendation_engine
from app.ml.forecasting import task_duration_predictor, burndown_forecaster, time_series_forecaster
from app.ml.nlp_processor import nlp_processor

logger = logging.getLogger(__name__)

ml_bp = Blueprint('ml', __name__, url_prefix='/api/v1/ml')


def require_auth(f):
    """Require authentication for ML endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Basic auth check - in production use proper auth
        token = request.headers.get('Authorization', '')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# ML Pipeline Endpoints
# ============================================================================

@ml_bp.route('/pipeline/initialize', methods=['POST'])
@require_auth
def initialize_pipeline():
    """Initialize ML pipeline"""
    try:
        ml_pipeline.initialize()
        return jsonify({
            'status': 'success',
            'message': 'ML pipeline initialized',
            'stats': ml_pipeline.get_pipeline_stats(),
        }), 200
    except Exception as e:
        logger.error(f"Pipeline init error: {e}")
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/pipeline/stats', methods=['GET'])
@require_auth
def get_pipeline_stats():
    """Get pipeline statistics"""
    try:
        stats = ml_pipeline.get_pipeline_stats()
        return jsonify({
            'status': 'success',
            'stats': stats,
        }), 200
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/predict', methods=['POST'])
@require_auth
def predict():
    """Make prediction on data"""
    try:
        data = request.get_json()
        
        model_name = data.get('model')
        obj_data = data.get('data', {})
        obj_type = data.get('type', 'project')
        
        if not model_name or not obj_data:
            return jsonify({'error': 'Missing model or data'}), 400
        
        prediction = ml_pipeline.predict(model_name, obj_data, obj_type)
        
        return jsonify({
            'status': 'success',
            'model': model_name,
            'prediction': prediction,
            'timestamp': datetime.now().isoformat(),
        }), 200
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Anomaly Detection Endpoints
# ============================================================================

@ml_bp.route('/anomalies/detect', methods=['POST'])
@require_auth
def detect_anomalies():
    """Detect anomalies in project data"""
    try:
        data = request.get_json()
        project_data = data.get('data', {})
        
        alerts = anomaly_detector.detect_all_anomalies(project_data)
        
        return jsonify({
            'status': 'success',
            'total_alerts': len(alerts),
            'alerts': [a.to_dict() for a in alerts],
            'summary': anomaly_detector.get_alerts_summary(),
        }), 200
    except Exception as e:
        logger.error(f"Anomaly detection error: {e}")
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/anomalies/active', methods=['GET'])
@require_auth
def get_active_anomalies():
    """Get all active anomalies"""
    try:
        alerts = anomaly_detector.get_active_alerts()
        
        return jsonify({
            'status': 'success',
            'total_active': len(alerts),
            'alerts': [a.to_dict() for a in alerts],
        }), 200
    except Exception as e:
        logger.error(f"Error getting anomalies: {e}")
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/anomalies/<alert_id>/acknowledge', methods=['POST'])
@require_auth
def acknowledge_anomaly(alert_id):
    """Acknowledge an anomaly alert"""
    try:
        success = anomaly_detector.acknowledge_alert(alert_id)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'alert_id': alert_id,
            'acknowledged': success,
        }), 200 if success else 404
    except Exception as e:
        logger.error(f"Acknowledge error: {e}")
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/anomalies/summary', methods=['GET'])
@require_auth
def get_anomalies_summary():
    """Get anomalies summary"""
    try:
        summary = anomaly_detector.get_alerts_summary()
        
        return jsonify({
            'status': 'success',
            'summary': summary,
        }), 200
    except Exception as e:
        logger.error(f"Summary error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Recommendations Endpoints
# ============================================================================

@ml_bp.route('/recommendations/issue', methods=['POST'])
@require_auth
def get_issue_recommendations():
    """Get recommendations for an issue"""
    try:
        data = request.get_json()
        issue = data.get('issue', {})
        all_issues = data.get('all_issues', [])
        all_users = data.get('all_users', [])
        
        recommendations = recommendation_engine.get_issue_recommendations(
            issue, all_issues, all_users
        )
        
        result = {}
        for rec_type, recs in recommendations.items():
            result[rec_type] = [
                {
                    'id': r.id,
                    'title': r.title,
                    'description': r.description,
                    'type': r.type,
                    'confidence_score': r.confidence_score,
                    'reason': r.reason,
                }
                for r in recs
            ]
        
        return jsonify({
            'status': 'success',
            'recommendations': result,
        }), 200
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/recommendations/project', methods=['POST'])
@require_auth
def get_project_recommendations():
    """Get recommendations for a project"""
    try:
        data = request.get_json()
        project = data.get('project', {})
        templates = data.get('templates', [])
        
        recommendations = recommendation_engine.get_project_recommendations(
            project, templates
        )
        
        result = {}
        for rec_type, recs in recommendations.items():
            result[rec_type] = [
                {
                    'id': r.id,
                    'title': r.title,
                    'description': r.description,
                    'type': r.type,
                    'confidence_score': r.confidence_score,
                    'reason': r.reason,
                }
                for r in recs
            ]
        
        return jsonify({
            'status': 'success',
            'recommendations': result,
        }), 200
    except Exception as e:
        logger.error(f"Project recommendation error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Forecasting Endpoints
# ============================================================================

@ml_bp.route('/forecast/task-duration', methods=['POST'])
@require_auth
def forecast_task_duration():
    """Forecast task duration"""
    try:
        data = request.get_json()
        issue = data.get('issue', {})
        
        prediction = task_duration_predictor.predict_duration(issue)
        
        return jsonify({
            'status': 'success',
            'predicted_days': prediction,
            'issue_id': issue.get('id'),
        }), 200
    except Exception as e:
        logger.error(f"Duration forecast error: {e}")
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/forecast/batch-completion', methods=['POST'])
@require_auth
def forecast_batch_completion():
    """Forecast batch completion time"""
    try:
        data = request.get_json()
        issues = data.get('issues', [])
        
        forecast = task_duration_predictor.estimate_batch_completion(issues)
        
        return jsonify({
            'status': 'success',
            'forecast': forecast,
        }), 200
    except Exception as e:
        logger.error(f"Batch forecast error: {e}")
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/forecast/burndown', methods=['POST'])
@require_auth
def forecast_burndown():
    """Forecast project burndown"""
    try:
        data = request.get_json()
        remaining = data.get('remaining_issues', 0)
        velocity = data.get('velocity', [])
        
        forecast = burndown_forecaster.forecast_completion(remaining, velocity)
        
        return jsonify({
            'status': 'success',
            'forecast': forecast,
        }), 200
    except Exception as e:
        logger.error(f"Burndown forecast error: {e}")
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/forecast/metric', methods=['POST'])
@require_auth
def forecast_metric():
    """Forecast metric trend"""
    try:
        data = request.get_json()
        values = data.get('values', [])
        periods = data.get('periods_ahead', 7)
        metric_type = data.get('metric_type', 'generic')
        
        forecast = time_series_forecaster.forecast_metric(values, periods)
        
        return jsonify({
            'status': 'success',
            'forecast': forecast,
            'periods_ahead': periods,
        }), 200
    except Exception as e:
        logger.error(f"Metric forecast error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# NLP Endpoints
# ============================================================================

@ml_bp.route('/nlp/process', methods=['POST'])
@require_auth
def process_nlp():
    """Process text with NLP"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        result = nlp_processor.process(text)
        
        return jsonify({
            'status': 'success',
            'text': result.text,
            'sentiment': result.sentiment.name,
            'sentiment_score': result.sentiment_score,
            'entities': result.entities,
            'tags': result.tags,
            'keywords': result.keywords,
            'summary': result.summary,
        }), 200
    except Exception as e:
        logger.error(f"NLP error: {e}")
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/nlp/analyze-comments', methods=['POST'])
@require_auth
def analyze_comments():
    """Analyze multiple comments"""
    try:
        data = request.get_json()
        comments = data.get('comments', [])
        
        analysis = nlp_processor.analyze_comments(comments)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis,
        }), 200
    except Exception as e:
        logger.error(f"Comment analysis error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Health Check
# ============================================================================

@ml_bp.route('/health', methods=['GET'])
def ml_health():
    """ML system health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'components': {
                'ml_pipeline': 'ready',
                'anomaly_detector': 'ready',
                'recommendation_engine': 'ready',
                'forecasting': 'ready',
                'nlp_processor': 'ready',
            },
            'timestamp': datetime.now().isoformat(),
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

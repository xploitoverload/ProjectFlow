"""Machine Learning Module - AI/ML Integration for Project Management

This module provides ML/AI capabilities including:
- Anomaly detection
- Smart recommendations
- Predictive analytics
- NLP processing
"""

from app.ml.ml_pipeline import MLPipeline, ModelManager
from app.ml.anomaly_detector import AnomalyDetector, AnomalyAlert
from app.ml.recommendations import RecommendationEngine
from app.ml.forecasting import TimeSeriesForecaster, TaskDurationPredictor
from app.ml.nlp_processor import NLPProcessor

__all__ = [
    'MLPipeline',
    'ModelManager',
    'AnomalyDetector',
    'AnomalyAlert',
    'RecommendationEngine',
    'TimeSeriesForecaster',
    'TaskDurationPredictor',
    'NLPProcessor',
]

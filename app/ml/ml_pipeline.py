"""ML Pipeline Infrastructure - Model Management and Feature Engineering"""

import os
import pickle
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Extract and engineer features from project data"""
    
    @staticmethod
    def extract_project_features(project: Dict) -> Dict[str, float]:
        """Extract ML features from project data"""
        return {
            'age_days': (datetime.now() - project.get('created_at', datetime.now())).days,
            'team_size': len(project.get('members', [])),
            'issue_count': len(project.get('issues', [])),
            'completion_rate': project.get('completion_rate', 0.0),
            'avg_issue_duration': project.get('avg_issue_duration', 0.0),
            'activity_score': project.get('activity_score', 0.0),
        }
    
    @staticmethod
    def extract_user_features(user: Dict) -> Dict[str, float]:
        """Extract ML features from user data"""
        return {
            'account_age_days': (datetime.now() - user.get('created_at', datetime.now())).days,
            'project_count': user.get('project_count', 0),
            'issue_count': user.get('issue_count', 0),
            'avg_response_time': user.get('avg_response_time', 0.0),
            'completion_rate': user.get('completion_rate', 0.0),
            'collaboration_score': user.get('collaboration_score', 0.0),
        }
    
    @staticmethod
    def extract_issue_features(issue: Dict) -> Dict[str, float]:
        """Extract ML features from issue data"""
        created_at = issue.get('created_at', datetime.now())
        closed_at = issue.get('closed_at')
        
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if isinstance(closed_at, str) and closed_at:
            closed_at = datetime.fromisoformat(closed_at)
        
        duration = (closed_at - created_at).days if closed_at else (datetime.now() - created_at).days
        
        return {
            'priority': self._priority_to_score(issue.get('priority', 'medium')),
            'age_days': (datetime.now() - created_at).days,
            'duration_days': max(duration, 0),
            'assignee_count': len(issue.get('assignees', [])),
            'comment_count': len(issue.get('comments', [])),
            'attachment_count': len(issue.get('attachments', [])),
            'is_overdue': 1 if issue.get('status') != 'closed' and duration > 14 else 0,
        }
    
    @staticmethod
    def _priority_to_score(priority: str) -> float:
        """Convert priority to numeric score"""
        scores = {'critical': 4.0, 'high': 3.0, 'medium': 2.0, 'low': 1.0}
        return scores.get(priority.lower(), 2.0)


class ModelCache:
    """In-memory and disk cache for ML models"""
    
    def __init__(self, cache_dir: str = '/tmp/ml_models'):
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, Any] = {}
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached model or data"""
        # Check memory cache first
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Check disk cache
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                self.memory_cache[key] = data
                return data
            except Exception as e:
                logger.error(f"Cache read error for {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl_hours: int = 24) -> None:
        """Cache model or data"""
        self.memory_cache[key] = value
        
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            logger.error(f"Cache write error for {key}: {e}")
    
    def clear(self, pattern: str = None) -> None:
        """Clear cache"""
        if pattern:
            keys_to_delete = [k for k in self.memory_cache if pattern in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
        else:
            self.memory_cache.clear()


class PredictionCache:
    """Cache for predictions with TTL"""
    
    def __init__(self, ttl_hours: int = 1):
        self.ttl = timedelta(hours=ttl_hours)
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached prediction"""
        if key in self.cache:
            value, expiry = self.cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Cache prediction"""
        self.cache[key] = (value, datetime.now() + self.ttl)
    
    def invalidate(self, pattern: str = None) -> None:
        """Invalidate cache entries"""
        if pattern:
            keys_to_delete = [k for k in self.cache if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]
        else:
            self.cache.clear()


class ModelManager:
    """Manage ML model lifecycle"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.model_cache = ModelCache()
        self.prediction_cache = PredictionCache(ttl_hours=1)
        self.model_metadata: Dict[str, Dict] = {}
    
    def register_model(self, name: str, model: Any, metadata: Dict = None) -> None:
        """Register a trained model"""
        self.models[name] = model
        self.model_metadata[name] = metadata or {}
        self.model_metadata[name]['registered_at'] = datetime.now().isoformat()
        
        # Cache model
        self.model_cache.set(f"model_{name}", model)
        logger.info(f"Model registered: {name}")
    
    def get_model(self, name: str) -> Optional[Any]:
        """Get registered model"""
        if name in self.models:
            return self.models[name]
        
        # Try to load from cache
        model = self.model_cache.get(f"model_{name}")
        if model:
            self.models[name] = model
            return model
        
        return None
    
    def predict(self, model_name: str, features: Dict, cache_key: str = None) -> Optional[Any]:
        """Make prediction using registered model"""
        # Check prediction cache
        if cache_key:
            cached = self.prediction_cache.get(cache_key)
            if cached is not None:
                return cached
        
        model = self.get_model(model_name)
        if not model:
            logger.error(f"Model not found: {model_name}")
            return None
        
        try:
            # Convert features dict to array if needed
            if hasattr(model, 'predict'):
                features_array = np.array([list(features.values())])
                prediction = model.predict(features_array)[0]
            else:
                prediction = model(features)
            
            # Cache prediction
            if cache_key:
                self.prediction_cache.set(cache_key, prediction)
            
            return prediction
        except Exception as e:
            logger.error(f"Prediction error for {model_name}: {e}")
            return None
    
    def get_model_info(self, name: str) -> Dict:
        """Get model metadata"""
        return {
            'name': name,
            'is_loaded': name in self.models,
            'metadata': self.model_metadata.get(name, {}),
            'cached': self.model_cache.get(f"model_{name}") is not None,
        }


class MLPipeline:
    """Main ML pipeline for project management"""
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.feature_engineer = FeatureEngineer()
        self.prediction_cache = PredictionCache(ttl_hours=2)
    
    def initialize(self) -> None:
        """Initialize ML pipeline"""
        logger.info("ML Pipeline initialized")
    
    def extract_features(self, data_type: str, data: Dict) -> Dict[str, float]:
        """Extract features from various data types"""
        if data_type == 'project':
            return self.feature_engineer.extract_project_features(data)
        elif data_type == 'user':
            return self.feature_engineer.extract_user_features(data)
        elif data_type == 'issue':
            return self.feature_engineer.extract_issue_features(data)
        else:
            return {}
    
    def predict(self, model_name: str, data: Dict, data_type: str = 'project') -> Optional[Any]:
        """Make prediction on data"""
        # Extract features
        features = self.extract_features(data_type, data)
        
        # Create cache key
        feature_hash = hashlib.md5(json.dumps(features, sort_keys=True).encode()).hexdigest()
        cache_key = f"{model_name}_{feature_hash}"
        
        # Use model manager to predict (with caching)
        return self.model_manager.predict(model_name, features, cache_key)
    
    def batch_predict(self, model_name: str, data_list: List[Dict], data_type: str = 'project') -> List[Any]:
        """Make predictions on multiple data points"""
        predictions = []
        for data in data_list:
            pred = self.predict(model_name, data, data_type)
            predictions.append(pred)
        return predictions
    
    def get_pipeline_stats(self) -> Dict:
        """Get pipeline statistics"""
        return {
            'models_loaded': len(self.model_manager.models),
            'cache_entries': len(self.model_manager.prediction_cache.cache),
            'feature_engineer': 'ready',
            'initialized_at': datetime.now().isoformat(),
        }


# Global pipeline instance
ml_pipeline = MLPipeline()


def with_ml_prediction(model_name: str, data_type: str = 'project'):
    """Decorator to add ML predictions to functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Add predictions if result is dict-like
            if isinstance(result, dict):
                features = ml_pipeline.extract_features(data_type, result)
                result['_ml_features'] = features
                result['_prediction'] = ml_pipeline.predict(model_name, result, data_type)
            
            return result
        return wrapper
    return decorator

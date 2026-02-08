"""Forecasting Module - Time series and duration predictions"""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)


class SimpleLinearRegression:
    """Simple linear regression for trend forecasting"""
    
    def __init__(self):
        self.slope = 0
        self.intercept = 0
        self.fitted = False
    
    def fit(self, x: List[float], y: List[float]) -> None:
        """Fit linear regression model"""
        if len(x) < 2 or len(y) != len(x):
            return
        
        n = len(x)
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator != 0:
            self.slope = numerator / denominator
            self.intercept = y_mean - self.slope * x_mean
            self.fitted = True
    
    def predict(self, x: float) -> Optional[float]:
        """Make prediction"""
        if not self.fitted:
            return None
        return self.slope * x + self.intercept
    
    def predict_sequence(self, x_values: List[float]) -> List[Optional[float]]:
        """Predict multiple values"""
        return [self.predict(x) for x in x_values]


class ExponentialMovingAverage:
    """Exponential moving average for trend analysis"""
    
    def __init__(self, alpha: float = 0.2):
        self.alpha = alpha  # Smoothing factor
        self.ema = None
    
    def update(self, value: float) -> float:
        """Update EMA with new value"""
        if self.ema is None:
            self.ema = value
        else:
            self.ema = self.alpha * value + (1 - self.alpha) * self.ema
        return self.ema
    
    def fit(self, values: List[float]) -> List[float]:
        """Fit EMA to series of values"""
        ema_values = []
        self.ema = None
        for value in values:
            ema_values.append(self.update(value))
        return ema_values


class TaskDurationPredictor:
    """Predict task/issue duration based on historical data"""
    
    def __init__(self):
        self.model = SimpleLinearRegression()
        self.historical_durations: Dict[str, List[float]] = {}
    
    def add_historical_data(self, issue_type: str, duration_days: float) -> None:
        """Add historical issue duration"""
        if issue_type not in self.historical_durations:
            self.historical_durations[issue_type] = []
        self.historical_durations[issue_type].append(duration_days)
    
    def predict_duration(self, issue: Dict) -> Optional[float]:
        """Predict issue duration"""
        issue_type = issue.get('type', 'bug')
        priority = issue.get('priority', 'medium')
        
        # Get historical data for this type
        if issue_type not in self.historical_durations:
            return None
        
        durations = self.historical_durations[issue_type]
        if not durations:
            return None
        
        # Base prediction on mean
        base_duration = statistics.mean(durations)
        
        # Adjust by priority
        priority_multiplier = {
            'critical': 0.5,
            'high': 0.7,
            'medium': 1.0,
            'low': 1.5,
        }
        
        multiplier = priority_multiplier.get(priority.lower(), 1.0)
        predicted_duration = base_duration * multiplier
        
        return predicted_duration
    
    def estimate_batch_completion(self, issues: List[Dict]) -> Optional[Dict]:
        """Estimate completion time for batch of issues"""
        if not issues:
            return None
        
        total_days = 0
        completed = 0
        
        for issue in issues:
            duration = self.predict_duration(issue)
            if duration:
                total_days += duration
                completed += 1
        
        if completed == 0:
            return None
        
        avg_duration = total_days / completed
        
        return {
            'estimated_total_days': total_days,
            'average_duration_per_issue': avg_duration,
            'completion_date': datetime.now() + timedelta(days=total_days),
            'issues_estimated': completed,
            'confidence': 'medium' if completed > 3 else 'low',
        }
    
    def get_duration_statistics(self, issue_type: str) -> Optional[Dict]:
        """Get statistics for issue type"""
        if issue_type not in self.historical_durations:
            return None
        
        durations = self.historical_durations[issue_type]
        if not durations:
            return None
        
        return {
            'count': len(durations),
            'min': min(durations),
            'max': max(durations),
            'mean': statistics.mean(durations),
            'median': statistics.median(durations),
            'stdev': statistics.stdev(durations) if len(durations) > 1 else 0,
        }


class BurndownForecaster:
    """Forecast burndown/velocity trends"""
    
    def __init__(self):
        self.model = SimpleLinearRegression()
    
    def calculate_velocity(self, issues_closed_by_day: List[int]) -> Optional[float]:
        """Calculate velocity (issues per day)"""
        if not issues_closed_by_day:
            return None
        return statistics.mean(issues_closed_by_day)
    
    def forecast_completion(self, remaining_issues: int, 
                           historical_velocity: List[int]) -> Optional[Dict]:
        """Forecast project completion date"""
        if not historical_velocity or remaining_issues <= 0:
            return None
        
        velocity = self.calculate_velocity(historical_velocity)
        if not velocity or velocity <= 0:
            return None
        
        days_to_completion = remaining_issues / velocity
        completion_date = datetime.now() + timedelta(days=days_to_completion)
        
        return {
            'estimated_days': days_to_completion,
            'estimated_completion_date': completion_date.isoformat(),
            'velocity': velocity,
            'remaining_issues': remaining_issues,
            'confidence': 'high' if len(historical_velocity) > 10 else 'medium',
        }
    
    def forecast_sprint(self, sprint_days: int, 
                       historical_velocity: List[int]) -> Optional[Dict]:
        """Forecast sprint completion"""
        velocity = self.calculate_velocity(historical_velocity)
        if not velocity:
            return None
        
        expected_issues = velocity * sprint_days
        
        return {
            'expected_issues': expected_issues,
            'velocity': velocity,
            'sprint_days': sprint_days,
            'confidence': 'high' if len(historical_velocity) > 5 else 'medium',
        }


class TimeSeriesForecaster:
    """Forecast time series data"""
    
    def __init__(self):
        self.linear_model = SimpleLinearRegression()
        self.ema_model = ExponentialMovingAverage()
    
    def forecast_metric(self, historical_values: List[float], 
                       periods_ahead: int = 7) -> Optional[List[float]]:
        """Forecast metric for future periods"""
        if len(historical_values) < 3:
            return None
        
        # Use EMA for smoothing
        smoothed = self.ema_model.fit(historical_values)
        
        # Fit linear regression
        x_values = list(range(len(smoothed)))
        self.linear_model.fit(x_values, smoothed)
        
        # Forecast ahead
        forecast_x = list(range(len(smoothed), len(smoothed) + periods_ahead))
        forecast = self.linear_model.predict_sequence([float(x) for x in forecast_x])
        
        return forecast
    
    def forecast_project_success_rate(self, historical_success_rates: List[float],
                                     periods_ahead: int = 4) -> Optional[Dict]:
        """Forecast project success rate trend"""
        forecast = self.forecast_metric(historical_success_rates, periods_ahead)
        
        if not forecast:
            return None
        
        # Cap at 0-1
        forecast = [max(0, min(1, v)) for v in forecast]
        
        return {
            'forecast': forecast,
            'trend': 'improving' if forecast[-1] > historical_success_rates[-1] else 'declining',
            'periods_ahead': periods_ahead,
            'current_rate': historical_success_rates[-1],
            'forecasted_rate': forecast[-1],
        }
    
    def forecast_issue_volume(self, historical_volumes: List[int],
                             periods_ahead: int = 4) -> Optional[Dict]:
        """Forecast issue volume trend"""
        forecast = self.forecast_metric([float(v) for v in historical_volumes], periods_ahead)
        
        if not forecast:
            return None
        
        forecast = [max(0, int(v)) for v in forecast]
        
        return {
            'forecast': forecast,
            'trend': 'increasing' if forecast[-1] > historical_volumes[-1] else 'decreasing',
            'periods_ahead': periods_ahead,
            'current_volume': historical_volumes[-1],
            'forecasted_volume': forecast[-1],
        }


# Global instances
task_duration_predictor = TaskDurationPredictor()
burndown_forecaster = BurndownForecaster()
time_series_forecaster = TimeSeriesForecaster()

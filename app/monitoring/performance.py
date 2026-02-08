# app/monitoring/performance.py
"""
Performance monitoring and benchmarking system.
Tracks endpoint performance, bottlenecks, and provides optimization recommendations.
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
import statistics

logger = logging.getLogger('performance')


class PerformanceMetric:
    """Single performance metric."""
    
    def __init__(self, operation: str, duration_ms: float, timestamp: Optional[datetime] = None):
        """Initialize metric."""
        self.operation = operation
        self.duration_ms = duration_ms
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'operation': self.operation,
            'duration_ms': self.duration_ms,
            'timestamp': self.timestamp.isoformat()
        }


class PerformanceStats:
    """Performance statistics for an operation."""
    
    def __init__(self, operation: str):
        """Initialize stats."""
        self.operation = operation
        self.metrics: List[PerformanceMetric] = []
        self.call_count = 0
        self.total_duration_ms = 0
        self.min_duration_ms = float('inf')
        self.max_duration_ms = 0
        self.errors = 0
        self.last_called: Optional[datetime] = None
    
    def add_metric(self, metric: PerformanceMetric):
        """Add performance metric."""
        self.metrics.append(metric)
        self.call_count += 1
        self.total_duration_ms += metric.duration_ms
        self.min_duration_ms = min(self.min_duration_ms, metric.duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, metric.duration_ms)
        self.last_called = metric.timestamp
    
    def get_average_ms(self) -> float:
        """Get average duration."""
        return self.total_duration_ms / self.call_count if self.call_count > 0 else 0
    
    def get_median_ms(self) -> float:
        """Get median duration."""
        if not self.metrics:
            return 0
        durations = [m.duration_ms for m in self.metrics]
        return statistics.median(durations)
    
    def get_stddev_ms(self) -> float:
        """Get standard deviation."""
        if len(self.metrics) < 2:
            return 0
        durations = [m.duration_ms for m in self.metrics]
        return statistics.stdev(durations)
    
    def get_p95_ms(self) -> float:
        """Get 95th percentile."""
        if not self.metrics:
            return 0
        durations = sorted([m.duration_ms for m in self.metrics])
        idx = int(len(durations) * 0.95)
        return durations[idx] if idx < len(durations) else durations[-1]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'operation': self.operation,
            'call_count': self.call_count,
            'total_duration_ms': self.total_duration_ms,
            'average_duration_ms': self.get_average_ms(),
            'median_duration_ms': self.get_median_ms(),
            'stddev_ms': self.get_stddev_ms(),
            'p95_duration_ms': self.get_p95_ms(),
            'min_duration_ms': self.min_duration_ms if self.min_duration_ms != float('inf') else 0,
            'max_duration_ms': self.max_duration_ms,
            'errors': self.errors,
            'last_called': self.last_called.isoformat() if self.last_called else None
        }


class PerformanceMonitor:
    """Monitors application performance."""
    
    def __init__(self, history_limit: int = 10000):
        """
        Initialize monitor.
        
        Args:
            history_limit: Maximum metrics to keep in memory
        """
        self.stats: Dict[str, PerformanceStats] = {}
        self.metrics_history: List[PerformanceMetric] = []
        self.history_limit = history_limit
        self.slow_threshold_ms = 1000  # 1 second default
        self.thresholds: Dict[str, float] = {}  # operation -> threshold_ms
    
    def record_metric(self, operation: str, duration_ms: float, success: bool = True):
        """Record performance metric."""
        metric = PerformanceMetric(operation, duration_ms)
        
        if operation not in self.stats:
            self.stats[operation] = PerformanceStats(operation)
        
        self.stats[operation].add_metric(metric)
        
        if not success:
            self.stats[operation].errors += 1
        
        # Keep metrics history limited
        self.metrics_history.append(metric)
        if len(self.metrics_history) > self.history_limit:
            self.metrics_history.pop(0)
        
        # Log slow operations
        threshold = self.thresholds.get(operation, self.slow_threshold_ms)
        if duration_ms > threshold:
            logger.warning(f"Slow operation: {operation} took {duration_ms:.2f}ms (threshold: {threshold}ms)")
    
    def set_threshold(self, operation: str, threshold_ms: float):
        """Set performance threshold for operation."""
        self.thresholds[operation] = threshold_ms
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance stats."""
        if operation:
            if operation in self.stats:
                return self.stats[operation].to_dict()
            return None
        
        return {
            op: stats.to_dict() for op, stats in self.stats.items()
        }
    
    def get_slowest_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest operations by average duration."""
        operations = sorted(
            self.stats.values(),
            key=lambda s: s.get_average_ms(),
            reverse=True
        )
        
        return [ops.to_dict() for ops in operations[:limit]]
    
    def get_most_called_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently called operations."""
        operations = sorted(
            self.stats.values(),
            key=lambda s: s.call_count,
            reverse=True
        )
        
        return [ops.to_dict() for ops in operations[:limit]]
    
    def get_recent_slow_operations(self, limit: int = 20, threshold_ms: Optional[float] = None) -> List[Dict[str, Any]]:
        """Get recent slow operations."""
        if threshold_ms is None:
            threshold_ms = self.slow_threshold_ms
        
        slow = [m.to_dict() for m in self.metrics_history if m.duration_ms > threshold_ms]
        return slow[-limit:]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        total_operations = sum(s.call_count for s in self.stats.values())
        total_errors = sum(s.errors for s in self.stats.values())
        total_duration = sum(s.total_duration_ms for s in self.stats.values())
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_operations': total_operations,
            'unique_operations': len(self.stats),
            'total_errors': total_errors,
            'error_rate': (total_errors / total_operations * 100) if total_operations > 0 else 0,
            'total_duration_ms': total_duration,
            'average_operation_duration_ms': total_duration / total_operations if total_operations > 0 else 0,
            'slowest_operations': self.get_slowest_operations(5),
            'most_called_operations': self.get_most_called_operations(5),
            'recent_slow_operations': self.get_recent_slow_operations(10)
        }
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on performance data."""
        recommendations = []
        
        slowest = self.get_slowest_operations(3)
        for op in slowest:
            recommendations.append(
                f"Operation '{op['operation']}' is slow ({op['average_duration_ms']:.2f}ms average). "
                f"Consider optimization or caching."
            )
        
        # Find operations with high error rates
        for op, stats in self.stats.items():
            if stats.call_count > 10:
                error_rate = (stats.errors / stats.call_count * 100)
                if error_rate > 5:
                    recommendations.append(
                        f"Operation '{op}' has high error rate ({error_rate:.1f}%). "
                        f"Investigate error handling."
                    )
        
        return recommendations


def track_performance(operation_name: str, threshold_ms: Optional[float] = None):
    """
    Decorator to track performance of functions.
    
    Usage:
        @track_performance('db.query.users')
        def get_users():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            if not monitor:
                return func(*args, **kwargs)
            
            start_time = time.perf_counter()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                monitor.record_metric(operation_name, duration_ms, success)
        
        return wrapper
    return decorator


# Global monitor instance
_monitor: Optional[PerformanceMonitor] = None


def init_performance_monitor(history_limit: int = 10000) -> PerformanceMonitor:
    """Initialize performance monitor."""
    global _monitor
    _monitor = PerformanceMonitor(history_limit)
    logger.info("✓ Performance monitor initialized")
    return _monitor


def get_performance_monitor() -> Optional[PerformanceMonitor]:
    """Get performance monitor instance."""
    return _monitor

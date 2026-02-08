# app/optimization/performance.py
"""
Performance Optimization and Advanced Caching
Multi-level caching strategies, query optimization, and performance monitoring.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import time


class CacheStrategy(Enum):
    """Cache strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    key: str = ""
    value: Any = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl_seconds: int = 3600
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.ttl_seconds <= 0:
            return False
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds
    
    def to_dict(self) -> Dict:
        return {
            'key': self.key,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'access_count': self.access_count
        }


@dataclass
class QueryPlan:
    """Database query optimization plan."""
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query: str = ""
    execution_time_ms: float = 0.0
    estimated_rows: int = 0
    indexes_available: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'query_id': self.query_id,
            'execution_time_ms': round(self.execution_time_ms, 2),
            'estimated_rows': self.estimated_rows,
            'optimization_suggestions': self.optimization_suggestions
        }


@dataclass
class PerformanceMetric:
    """Performance metric."""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str = ""
    value: float = 0.0
    unit: str = ""
    recorded_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'metric_name': self.metric_name,
            'value': round(self.value, 2),
            'unit': self.unit,
            'recorded_at': self.recorded_at.isoformat()
        }


class PerformanceOptimizationEngine:
    """
    Manages caching, query optimization, and performance monitoring.
    """
    
    def __init__(self):
        """Initialize performance engine."""
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_strategy = CacheStrategy.LRU
        self.query_plans: Dict[str, QueryPlan] = {}
        self.performance_metrics: Dict[str, PerformanceMetric] = {}
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_queries': 0,
            'slow_queries': 0,
            'avg_response_time_ms': 0.0
        }
    
    def set_cache_strategy(self, strategy: str) -> bool:
        """Set cache strategy."""
        try:
            self.cache_strategy = CacheStrategy[strategy.upper()]
            return True
        except KeyError:
            return False
    
    def cache_set(self, key: str, value: Any, ttl_seconds: int = 3600) -> CacheEntry:
        """Set cache entry."""
        entry = CacheEntry(
            key=key,
            value=value,
            ttl_seconds=ttl_seconds
        )
        
        self.cache[key] = entry
        return entry
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get cache entry."""
        if key not in self.cache:
            self.stats['cache_misses'] += 1
            return None
        
        entry = self.cache[key]
        
        if entry.is_expired():
            del self.cache[key]
            self.stats['cache_misses'] += 1
            return None
        
        # Update access metadata
        entry.last_accessed = datetime.utcnow()
        entry.access_count += 1
        
        self.stats['cache_hits'] += 1
        return entry.value
    
    def cache_invalidate(self, key: str = None) -> int:
        """Invalidate cache entries."""
        if key is None:
            # Invalidate all
            count = len(self.cache)
            self.cache.clear()
            return count
        else:
            if key in self.cache:
                del self.cache[key]
                return 1
            return 0
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        total = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_rate = (self.stats['cache_hits'] / total * 100) if total > 0 else 0
        
        return {
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'hit_rate_percent': round(hit_rate, 1),
            'total_entries': len(self.cache),
            'strategy': self.cache_strategy.value
        }
    
    def analyze_query(self, query: str, execution_time_ms: float) -> QueryPlan:
        """Analyze query for optimization opportunities."""
        plan = QueryPlan(
            query=query,
            execution_time_ms=execution_time_ms,
            estimated_rows=100  # Simulated
        )
        
        # Simulate query analysis
        suggestions = []
        
        if execution_time_ms > 1000:
            suggestions.append("Consider adding indexes on frequently searched columns")
            self.stats['slow_queries'] += 1
        
        if 'SELECT *' in query.upper():
            suggestions.append("Avoid SELECT *, specify required columns instead")
        
        if 'OR' in query.upper():
            suggestions.append("Consider using UNION instead of OR for better performance")
        
        if 'NOT IN' in query.upper():
            suggestions.append("Consider using NOT EXISTS instead of NOT IN")
        
        plan.optimization_suggestions = suggestions
        self.query_plans[plan.query_id] = plan
        self.stats['total_queries'] += 1
        
        return plan
    
    def record_metric(self, metric_name: str, value: float, unit: str = "") -> PerformanceMetric:
        """Record performance metric."""
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            unit=unit
        )
        
        self.performance_metrics[metric.metric_id] = metric
        
        # Update average response time
        if metric_name == 'response_time_ms':
            n = sum(1 for m in self.performance_metrics.values() if m.metric_name == 'response_time_ms')
            if n > 0:
                total = sum(m.value for m in self.performance_metrics.values() if m.metric_name == 'response_time_ms')
                self.stats['avg_response_time_ms'] = total / n
        
        return metric
    
    def get_optimization_recommendations(self, threshold_ms: int = 1000) -> Dict:
        """Get optimization recommendations based on analysis."""
        slow_queries = [p for p in self.query_plans.values() if p.execution_time_ms > threshold_ms]
        
        recommendations = {
            'total_recommendations': 0,
            'recommendations': []
        }
        
        if len(slow_queries) > 5:
            recommendations['recommendations'].append({
                'priority': 'high',
                'suggestion': f'{len(slow_queries)} slow queries detected. Consider query optimization.',
                'affected_queries': len(slow_queries)
            })
        
        cache_miss_rate = (self.stats['cache_misses'] / max(1, self.stats['cache_hits'] + self.stats['cache_misses']))
        if cache_miss_rate > 0.5:
            recommendations['recommendations'].append({
                'priority': 'medium',
                'suggestion': f'Cache miss rate is {cache_miss_rate*100:.1f}%. Increase TTL or cache size.',
                'current_miss_rate': round(cache_miss_rate * 100, 1)
            })
        
        if self.stats['avg_response_time_ms'] > threshold_ms:
            recommendations['recommendations'].append({
                'priority': 'high',
                'suggestion': f'Average response time is {self.stats["avg_response_time_ms"]:.0f}ms. Optimize hot paths.',
                'current_avg_ms': round(self.stats['avg_response_time_ms'], 2)
            })
        
        recommendations['total_recommendations'] = len(recommendations['recommendations'])
        return recommendations
    
    def get_stats(self) -> Dict:
        """Get performance statistics."""
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_rate = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        slow_query_rate = (self.stats['slow_queries'] / self.stats['total_queries'] * 100) if self.stats['total_queries'] > 0 else 0
        
        return {
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'hit_rate_percent': round(hit_rate, 1),
            'slow_queries': self.stats['slow_queries'],
            'slow_query_rate_percent': round(slow_query_rate, 1),
            'avg_response_time_ms': round(self.stats['avg_response_time_ms'], 2),
            'total_cached_entries': len(self.cache)
        }


# Global performance optimization engine
performance_engine = PerformanceOptimizationEngine()

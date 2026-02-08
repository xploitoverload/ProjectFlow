# app/cache/redis_cache.py
"""
Redis caching configuration and utilities.
Provides centralized caching for queries, computations, and session data.
"""

import redis
import json
import pickle
from functools import wraps
from typing import Any, Callable, Optional
import logging

logger = logging.getLogger('cache')


class RedisCache:
    """Redis cache manager with connection pooling and error handling."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, 
                 decode_responses: bool = True, socket_timeout: int = 5):
        """
        Initialize Redis cache connection.
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Database number
            decode_responses: Automatically decode responses
            socket_timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.db = db
        self.decode_responses = decode_responses
        self.socket_timeout = socket_timeout
        self.client = None
        self.pool = None
        
    def connect(self):
        """Establish Redis connection with connection pooling."""
        try:
            self.pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=self.decode_responses,
                socket_timeout=self.socket_timeout,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 1,  # TCP_KEEPINTVL
                    3: 1   # TCP_KEEPCNT
                },
                max_connections=10
            )
            self.client = redis.StrictRedis(connection_pool=self.pool)
            self.client.ping()
            logger.info(f"✓ Redis cache connected: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.warning(f"✗ Redis connection failed ({self.host}:{self.port}): {str(e)}")
            logger.info("→ Continuing with in-memory fallback")
            return False
    
    def set(self, key: str, value: Any, ttl: int = 3600, serializer: str = 'json') -> bool:
        """
        Set cache value with automatic expiration.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)
            serializer: 'json' or 'pickle'
        """
        if not self.client:
            return False
        
        try:
            if serializer == 'json':
                serialized = json.dumps(value)
            else:
                serialized = pickle.dumps(value)
            
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache SET error for key '{key}': {str(e)}")
            return False
    
    def get(self, key: str, serializer: str = 'json') -> Optional[Any]:
        """
        Get cached value.
        
        Args:
            key: Cache key
            serializer: 'json' or 'pickle'
        """
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            if serializer == 'json':
                return json.loads(value)
            else:
                return pickle.loads(value)
        except Exception as e:
            logger.error(f"Cache GET error for key '{key}': {str(e)}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache key."""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache DELETE error for key '{key}': {str(e)}")
            return False
    
    def clear(self, pattern: str = '*') -> int:
        """
        Clear cache by pattern.
        
        Args:
            pattern: Key pattern (e.g., 'projects:*')
        """
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
            return len(keys)
        except Exception as e:
            logger.error(f"Cache CLEAR error for pattern '{pattern}': {str(e)}")
            return 0
    
    def get_or_set(self, key: str, callback: Callable, ttl: int = 3600) -> Any:
        """
        Get value from cache or compute and cache.
        
        Args:
            key: Cache key
            callback: Function to call if cache miss
            ttl: Time to live in seconds
        """
        # Try to get from cache
        cached = self.get(key)
        if cached is not None:
            return cached
        
        # Cache miss - compute value
        value = callback()
        
        # Cache the result
        self.set(key, value, ttl)
        return value
    
    def health_check(self) -> dict:
        """Check Redis health."""
        if not self.client:
            return {'status': 'disconnected', 'details': 'No Redis connection'}
        
        try:
            info = self.client.info('server')
            return {
                'status': 'healthy',
                'server': info.get('redis_version', 'unknown'),
                'used_memory': info.get('used_memory_human', 'unknown'),
                'connected_clients': info.get('connected_clients', 0)
            }
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def close(self):
        """Close Redis connection."""
        if self.pool:
            self.pool.disconnect()
            logger.info("Redis connection closed")


def cache_result(ttl: int = 3600, key_prefix: str = None):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Custom key prefix (uses function name if not provided)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            # Simple cache key - doesn't include args for demo
            cache_key = prefix
            
            # Try cache first
            if hasattr(cache_result, '_cache') and cache_result._cache:
                cached = cache_result._cache.get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return cached
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            if hasattr(cache_result, '_cache') and cache_result._cache:
                cache_result._cache.set(cache_key, result, ttl)
                logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
_cache_instance: Optional[RedisCache] = None


def init_cache(app, host: str = 'localhost', port: int = 6379):
    """Initialize cache system in Flask app."""
    global _cache_instance
    
    host = app.config.get('REDIS_HOST', host)
    port = app.config.get('REDIS_PORT', port)
    
    _cache_instance = RedisCache(host=host, port=port)
    _cache_instance.connect()
    
    # Store on app for access
    app.redis_cache = _cache_instance
    
    # Store reference for decorator
    cache_result._cache = _cache_instance
    
    return _cache_instance


def get_cache() -> Optional[RedisCache]:
    """Get global cache instance."""
    return _cache_instance


# Cache key generators
class CacheKeys:
    """Standard cache key patterns."""
    
    @staticmethod
    def user_projects(user_id: int) -> str:
        """Projects cache key for user."""
        return f"user:{user_id}:projects"
    
    @staticmethod
    def project_issues(project_id: int, status: str = 'all') -> str:
        """Issues cache key for project."""
        return f"project:{project_id}:issues:{status}"
    
    @staticmethod
    def project_stats(project_id: int) -> str:
        """Project statistics cache key."""
        return f"project:{project_id}:stats"
    
    @staticmethod
    def user_stats(user_id: int) -> str:
        """User statistics cache key."""
        return f"user:{user_id}:stats"
    
    @staticmethod
    def dashboard_summary(user_id: int) -> str:
        """Dashboard summary cache key."""
        return f"dashboard:{user_id}:summary"
    
    @staticmethod
    def search_results(query: str, limit: int = 50) -> str:
        """Search results cache key."""
        return f"search:{query[:20]}:{limit}"


# Cache invalidation helpers
class CacheInvalidator:
    """Handle cache invalidation for related data."""
    
    @staticmethod
    def invalidate_project(project_id: int):
        """Invalidate all caches related to a project."""
        cache = get_cache()
        if not cache:
            return
        
        # Clear project-related caches
        patterns = [
            f"project:{project_id}:*",
            f"search:*",  # Clear search cache too
        ]
        
        for pattern in patterns:
            count = cache.clear(pattern)
            if count > 0:
                logger.debug(f"Invalidated {count} cache entries matching: {pattern}")
    
    @staticmethod
    def invalidate_user(user_id: int):
        """Invalidate all caches related to a user."""
        cache = get_cache()
        if not cache:
            return
        
        patterns = [
            f"user:{user_id}:*",
            f"dashboard:{user_id}:*"
        ]
        
        for pattern in patterns:
            count = cache.clear(pattern)
            if count > 0:
                logger.debug(f"Invalidated {count} cache entries matching: {pattern}")
    
    @staticmethod
    def invalidate_issue(project_id: int):
        """Invalidate caches when issue changes."""
        cache = get_cache()
        if not cache:
            return
        
        patterns = [
            f"project:{project_id}:issues:*",
            f"project:{project_id}:stats",
        ]
        
        for pattern in patterns:
            count = cache.clear(pattern)
            if count > 0:
                logger.debug(f"Invalidated {count} cache entries matching: {pattern}")

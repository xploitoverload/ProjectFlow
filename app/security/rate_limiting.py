# app/security/rate_limiting.py
"""
Rate Limiting Module
Prevents brute force, DoS, and abuse.
"""

from functools import wraps
from flask import request, abort, session, g
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable
import threading
import logging

security_logger = logging.getLogger('security')

# In-memory storage (use Redis in production)
_rate_limit_storage: Dict[str, list] = {}
_storage_lock = threading.Lock()


class RateLimiter:
    """
    Thread-safe rate limiter implementation.
    Uses sliding window algorithm.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Unique identifier (e.g., IP + endpoint)
            
        Returns:
            bool: True if request is allowed
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        with _storage_lock:
            # Initialize or get existing timestamps
            if key not in _rate_limit_storage:
                _rate_limit_storage[key] = []
            
            # Remove old timestamps
            _rate_limit_storage[key] = [
                ts for ts in _rate_limit_storage[key]
                if ts > window_start
            ]
            
            # Check if limit exceeded
            if len(_rate_limit_storage[key]) >= self.max_requests:
                return False
            
            # Add current timestamp
            _rate_limit_storage[key].append(now)
            
            return True
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests in current window."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        with _storage_lock:
            if key not in _rate_limit_storage:
                return self.max_requests
            
            current = len([
                ts for ts in _rate_limit_storage[key]
                if ts > window_start
            ])
            
            return max(0, self.max_requests - current)
    
    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        with _storage_lock:
            if key in _rate_limit_storage:
                del _rate_limit_storage[key]
    
    @staticmethod
    def cleanup_old_entries():
        """Remove old entries to prevent memory bloat."""
        cutoff = datetime.utcnow() - timedelta(hours=1)
        
        with _storage_lock:
            keys_to_remove = []
            
            for key, timestamps in _rate_limit_storage.items():
                # Remove if all timestamps are old
                if all(ts < cutoff for ts in timestamps):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del _rate_limit_storage[key]


def get_client_identifier() -> str:
    """
    Get unique client identifier for rate limiting.
    Uses IP + User-Agent fingerprint.
    """
    ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', '')[:50]
    user_id = session.get('user_id', 'anon')
    
    return f"{ip}:{user_id}:{hash(user_agent) % 10000}"


def get_client_ip() -> str:
    """Get client IP address, handling proxies."""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        ip = request.environ['HTTP_X_REAL_IP']
    else:
        ip = request.environ.get('REMOTE_ADDR', '127.0.0.1')
    
    return ip


# Pre-configured rate limiters
_login_limiter = RateLimiter(max_requests=5, window_seconds=300)  # 5 attempts per 5 min
_api_limiter = RateLimiter(max_requests=100, window_seconds=60)  # 100 requests per min
_sensitive_limiter = RateLimiter(max_requests=3, window_seconds=60)  # 3 per min for sensitive


def login_rate_limit(f: Callable) -> Callable:
    """
    Decorator for login rate limiting.
    Strict limits to prevent brute force.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = get_client_ip()
        key = f"login:{ip}"
        
        if not _login_limiter.is_allowed(key):
            security_logger.warning(f"Login rate limit exceeded for IP: {ip}")
            abort(429, description="Too many login attempts. Please try again later.")
        
        return f(*args, **kwargs)
    return decorated_function


def api_rate_limit(f: Callable) -> Callable:
    """
    Decorator for API rate limiting.
    Moderate limits for general API use.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = f"api:{get_client_identifier()}"
        
        if not _api_limiter.is_allowed(key):
            remaining = _api_limiter.get_remaining(key)
            security_logger.warning(f"API rate limit exceeded: {key}")
            
            response = abort(429, description="Rate limit exceeded. Please slow down.")
            return response
        
        return f(*args, **kwargs)
    return decorated_function


def sensitive_action_rate_limit(f: Callable) -> Callable:
    """
    Decorator for sensitive action rate limiting.
    Very strict limits for password changes, etc.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = f"sensitive:{get_client_identifier()}"
        
        if not _sensitive_limiter.is_allowed(key):
            security_logger.warning(f"Sensitive action rate limit exceeded: {key}")
            abort(429, description="Too many attempts. Please wait before trying again.")
        
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """
    Decorator factory for custom rate limiting.
    
    Usage:
        @rate_limit(max_requests=10, window_seconds=60)
        def my_endpoint():
            ...
    """
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = f"{request.endpoint}:{get_client_identifier()}"
            
            if not limiter.is_allowed(key):
                security_logger.warning(f"Rate limit exceeded: {key}")
                abort(429, description="Rate limit exceeded")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    """
    Check rate limit without decorator.
    Returns True if allowed.
    """
    limiter = RateLimiter(max_requests, window_seconds)
    return limiter.is_allowed(key)


def reset_login_attempts(ip: str) -> None:
    """Reset login rate limit for an IP after successful login."""
    key = f"login:{ip}"
    _login_limiter.reset(key)

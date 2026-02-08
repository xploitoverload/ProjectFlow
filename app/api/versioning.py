# app/api/versioning.py
"""
API versioning system supporting multiple API versions.
Provides backward compatibility and gradual migration paths.
"""

import logging
from functools import wraps
from typing import Callable, Optional, Dict, Any
from flask import request, jsonify

logger = logging.getLogger('api_versioning')


class APIVersion:
    """Represents an API version."""
    
    def __init__(self, version: str, deprecated: bool = False, 
                 sunset_date: Optional[str] = None):
        """
        Initialize API version.
        
        Args:
            version: Version string (e.g., 'v1', 'v2')
            deprecated: Whether version is deprecated
            sunset_date: Date when version will be removed (ISO format)
        """
        self.version = version
        self.deprecated = deprecated
        self.sunset_date = sunset_date
        self.endpoints = {}
    
    def register_endpoint(self, name: str, handler: Callable):
        """Register endpoint for this version."""
        self.endpoints[name] = handler
    
    def is_deprecated(self) -> bool:
        """Check if version is deprecated."""
        return self.deprecated
    
    def get_deprecation_header(self) -> Optional[str]:
        """Get deprecation header value."""
        if not self.deprecated:
            return None
        
        header = f'version {self.version} is deprecated'
        if self.sunset_date:
            header += f', sunset date is {self.sunset_date}'
        return header


class VersionedAPIRouter:
    """Route API requests to appropriate version handlers."""
    
    def __init__(self):
        """Initialize versioned API router."""
        self.versions: Dict[str, APIVersion] = {}
        self.default_version: Optional[str] = None
    
    def register_version(self, version: str, deprecated: bool = False,
                        sunset_date: Optional[str] = None) -> APIVersion:
        """Register new API version."""
        api_version = APIVersion(version, deprecated, sunset_date)
        self.versions[version] = api_version
        
        if self.default_version is None:
            self.default_version = version
        
        logger.info(f"Registered API version: {version}")
        return api_version
    
    def get_version(self, version: str) -> Optional[APIVersion]:
        """Get API version by string."""
        return self.versions.get(version)
    
    def get_request_version(self) -> str:
        """
        Extract API version from request.
        
        Supports:
        - URL path: /api/v1/endpoint
        - Header: X-API-Version: v1
        - Query param: ?api-version=v1
        
        Returns:
            Version string (e.g., 'v1')
        """
        # Check URL path first (highest priority)
        path = request.path
        for version in self.versions.keys():
            if f'/api/{version}/' in path:
                return version
        
        # Check header
        header_version = request.headers.get('X-API-Version')
        if header_version and header_version in self.versions:
            return header_version
        
        # Check query param
        param_version = request.args.get('api-version')
        if param_version and param_version in self.versions:
            return param_version
        
        # Use default version
        return self.default_version or 'v1'
    
    def version_endpoint(self, versions: list = None):
        """
        Decorator for versioned endpoints.
        
        Usage:
            @router.version_endpoint(['v1', 'v2'])
            def get_issues():
                return jsonify(issues)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                current_version = self.get_request_version()
                
                # Get version object
                version_obj = self.get_version(current_version)
                if not version_obj:
                    return jsonify({'error': f'API version {current_version} not found'}), 404
                
                # Execute handler
                result = func(*args, **kwargs)
                
                # Add version headers
                if isinstance(result, tuple):
                    response_data, status_code = result[0], result[1] if len(result) > 1 else 200
                    headers = result[2] if len(result) > 2 else {}
                else:
                    response_data = result
                    status_code = 200
                    headers = {}
                
                # Add API version headers
                headers['X-API-Version'] = current_version
                
                if version_obj.is_deprecated():
                    headers['Deprecation'] = 'true'
                    headers['Sunset'] = version_obj.sunset_date or ''
                    logger.warning(f"Deprecated API version used: {current_version}")
                
                if isinstance(result, tuple):
                    return response_data, status_code, headers
                else:
                    from flask import make_response
                    response = make_response(response_data)
                    for key, value in headers.items():
                        response.headers[key] = value
                    return response
            
            return wrapper
        return decorator


# Global router instance
_router = VersionedAPIRouter()


def init_api_versioning(app) -> VersionedAPIRouter:
    """Initialize API versioning in Flask app."""
    
    # Register versions
    v1 = _router.register_version('v1', deprecated=False)
    v2 = _router.register_version('v2', deprecated=False)
    v0 = _router.register_version('v0', deprecated=True, sunset_date='2026-08-01')
    
    logger.info("✓ API versioning initialized with v0, v1, v2")
    
    app.api_router = _router
    return _router


def get_api_router() -> VersionedAPIRouter:
    """Get global API router."""
    return _router


class VersionMigrationGuide:
    """Guide for migrating between API versions."""
    
    MIGRATIONS = {
        'v0_to_v1': {
            'breaking_changes': [
                'POST /api/v0/issues → POST /api/v1/issues (response format changed)',
                'GET /api/v0/projects → GET /api/v1/projects (added pagination)',
                'Removed: /api/v0/users/search (use /api/v1/search instead)'
            ],
            'new_features': [
                'Search endpoint: GET /api/v1/search',
                'Export: GET /api/v1/issues/export?format=csv',
                'Filtering: GET /api/v1/issues?status=open&priority=high'
            ],
            'deprecated': [
                'Field: issue.assigned_user (use issue.assigned_to)',
                'Endpoint: GET /api/v1/users/old-format'
            ]
        },
        'v1_to_v2': {
            'breaking_changes': [
                'Authentication: Bearer tokens required (removed session auth)',
                'Response format: All errors now return {error, details, code}',
                'Pagination: Default page size changed from 25 to 50'
            ],
            'new_features': [
                'GraphQL endpoint: POST /api/v2/graphql',
                'Real-time: WebSocket /api/v2/ws',
                'Batch operations: POST /api/v2/batch',
                'Rate limiting: 1000 req/hour (v1: 100 req/hour)'
            ],
            'deprecated': [
                'Endpoint: GET /api/v2/issues/legacy-format',
                'Header: X-Session-Token (use Authorization: Bearer)'
            ]
        }
    }
    
    @staticmethod
    def get_migration_guide(from_version: str, to_version: str) -> Dict[str, Any]:
        """Get migration guide between versions."""
        key = f"{from_version}_to_{to_version}"
        return VersionMigrationGuide.MIGRATIONS.get(key, {})
    
    @staticmethod
    def list_all_changes() -> Dict[str, Any]:
        """List all breaking changes and migrations."""
        return VersionMigrationGuide.MIGRATIONS


class VersionCompatibility:
    """Check API compatibility."""
    
    @staticmethod
    def is_compatible(version: str, required_version: str) -> bool:
        """Check if version is compatible with required version."""
        # Simplified: same major version is compatible
        return version.split('.')[0] == required_version.split('.')[0]
    
    @staticmethod
    def get_compatible_versions(version: str) -> list:
        """Get all compatible versions."""
        major_version = version.split('.')[0]
        return [v for v in ['v1', 'v2'] if v.startswith(major_version)]

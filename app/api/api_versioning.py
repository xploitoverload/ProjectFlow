# app/api/api_versioning.py
"""
API Versioning and GraphQL Support
Support multiple API versions and GraphQL endpoints.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid


class APIVersion(Enum):
    """API versions."""
    V1 = "v1"
    V2 = "v2"


@dataclass
class APIEndpoint:
    """API endpoint definition."""
    endpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    path: str = ""
    method: str = "GET"
    version: APIVersion = APIVersion.V2
    description: str = ""
    deprecated: bool = False
    replacement_path: Optional[str] = None
    request_schema: Dict = field(default_factory=dict)
    response_schema: Dict = field(default_factory=dict)
    rate_limit_per_hour: int = 1000
    authentication_required: bool = True
    
    def to_dict(self) -> Dict:
        return {
            'path': self.path,
            'method': self.method,
            'version': self.version.value,
            'description': self.description,
            'deprecated': self.deprecated,
            'rate_limit_per_hour': self.rate_limit_per_hour,
            'authentication_required': self.authentication_required
        }


@dataclass
class GraphQLQuery:
    """GraphQL query."""
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query: str = ""
    variables: Dict = field(default_factory=dict)
    user_id: str = ""
    executed_at: datetime = field(default_factory=datetime.utcnow)
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'query_id': self.query_id,
            'execution_time_ms': round(self.execution_time_ms, 2),
            'executed_at': self.executed_at.isoformat()
        }


@dataclass
class APIUsage:
    """API usage tracking."""
    usage_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    endpoint_path: str = ""
    method: str = ""
    version: str = "v1"
    status_code: int = 200
    response_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'endpoint': self.endpoint_path,
            'method': self.method,
            'version': self.version,
            'status_code': self.status_code,
            'response_time_ms': round(self.response_time_ms, 2),
            'timestamp': self.timestamp.isoformat()
        }


class APIVersioningManager:
    """
    Manages API versions, GraphQL, and endpoint definitions.
    """
    
    def __init__(self):
        """Initialize API versioning manager."""
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.graphql_queries: Dict[str, GraphQLQuery] = {}
        self.api_usage: Dict[str, APIUsage] = {}
        self.stats = {
            'total_endpoints': 0,
            'v1_endpoints': 0,
            'v2_endpoints': 0,
            'total_graphql_queries': 0,
            'total_api_calls': 0
        }
    
    def register_endpoint(self, path: str, method: str, version: str,
                         description: str = "", auth_required: bool = True) -> APIEndpoint:
        """Register API endpoint."""
        try:
            version_enum = APIVersion[version.upper()]
        except KeyError:
            version_enum = APIVersion.V2
        
        endpoint = APIEndpoint(
            path=path,
            method=method,
            version=version_enum,
            description=description,
            authentication_required=auth_required
        )
        
        key = f"{method}:{path}:{version}"
        self.endpoints[key] = endpoint
        
        self.stats['total_endpoints'] += 1
        if version == 'v1':
            self.stats['v1_endpoints'] += 1
        else:
            self.stats['v2_endpoints'] += 1
        
        return endpoint
    
    def get_endpoint(self, method: str, path: str, version: str) -> Optional[APIEndpoint]:
        """Get endpoint definition."""
        key = f"{method}:{path}:{version}"
        return self.endpoints.get(key)
    
    def deprecate_endpoint(self, method: str, path: str, version: str,
                          replacement_path: str = None) -> bool:
        """Deprecate API endpoint."""
        key = f"{method}:{path}:{version}"
        
        if key not in self.endpoints:
            return False
        
        endpoint = self.endpoints[key]
        endpoint.deprecated = True
        endpoint.replacement_path = replacement_path
        
        return True
    
    def execute_graphql_query(self, user_id: str, query: str,
                             variables: Dict = None) -> GraphQLQuery:
        """Execute GraphQL query."""
        graphql_query = GraphQLQuery(
            query=query,
            variables=variables or {},
            user_id=user_id,
            execution_time_ms=50.0  # Simulated
        )
        
        self.graphql_queries[graphql_query.query_id] = graphql_query
        self.stats['total_graphql_queries'] += 1
        
        return graphql_query
    
    def get_graphql_introspection(self) -> Dict:
        """Get GraphQL schema introspection."""
        return {
            'types': [
                {'name': 'Query', 'kind': 'OBJECT'},
                {'name': 'Project', 'kind': 'OBJECT'},
                {'name': 'Task', 'kind': 'OBJECT'},
                {'name': 'User', 'kind': 'OBJECT'},
                {'name': 'Team', 'kind': 'OBJECT'},
                {'name': 'String', 'kind': 'SCALAR'},
                {'name': 'Int', 'kind': 'SCALAR'},
                {'name': 'Boolean', 'kind': 'SCALAR'},
                {'name': 'DateTime', 'kind': 'SCALAR'}
            ],
            'queryType': 'Query',
            'mutationType': 'Mutation'
        }
    
    def record_api_call(self, user_id: str, endpoint_path: str, method: str,
                       version: str, status_code: int, response_time_ms: float) -> APIUsage:
        """Record API call for analytics."""
        usage = APIUsage(
            user_id=user_id,
            endpoint_path=endpoint_path,
            method=method,
            version=version,
            status_code=status_code,
            response_time_ms=response_time_ms
        )
        
        self.api_usage[usage.usage_id] = usage
        self.stats['total_api_calls'] += 1
        
        return usage
    
    def get_api_usage_report(self, version: str = None, limit: int = 100) -> List[Dict]:
        """Get API usage report."""
        usage_list = list(self.api_usage.values())
        
        if version:
            usage_list = [u for u in usage_list if u.version == version]
        
        # Sort by timestamp (most recent first)
        usage_list.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [u.to_dict() for u in usage_list[:limit]]
    
    def get_endpoint_coverage(self) -> Dict:
        """Get API endpoint coverage metrics."""
        total = self.stats['total_endpoints']
        deprecated = sum(1 for e in self.endpoints.values() if e.deprecated)
        auth_required = sum(1 for e in self.endpoints.values() if e.authentication_required)
        
        return {
            'total_endpoints': total,
            'v1_endpoints': self.stats['v1_endpoints'],
            'v2_endpoints': self.stats['v2_endpoints'],
            'deprecated_endpoints': deprecated,
            'auth_required_endpoints': auth_required,
            'auth_coverage_percent': round((auth_required / total * 100) if total > 0 else 0, 1)
        }
    
    def get_stats(self) -> Dict:
        """Get API versioning statistics."""
        return {
            'total_endpoints': self.stats['total_endpoints'],
            'v1_endpoints': self.stats['v1_endpoints'],
            'v2_endpoints': self.stats['v2_endpoints'],
            'total_graphql_queries': self.stats['total_graphql_queries'],
            'total_api_calls': self.stats['total_api_calls'],
            'api_versions': ['v1', 'v2'],
            'graphql_enabled': True
        }


# Global API versioning manager
api_versioning_manager = APIVersioningManager()

# tests/test_phase6_integration.py
"""
Phase 6 Integration Tests - Comprehensive test suite for enterprise systems.
Tests WebSocket, batch operations, backups, GraphQL, and performance monitoring.
"""

import pytest
import json
from datetime import datetime


class TestBatchOperations:
    """Test batch operations system."""
    
    def test_batch_builder_create(self):
        """Test batch builder create operation."""
        from app.operations import BatchBuilder
        
        builder = BatchBuilder()
        builder.create('issue', {'title': 'Test Issue', 'description': 'Test'})
        operations = builder.build()
        
        assert len(operations) == 1
        assert operations[0].operation_type.value == 'create'
        assert operations[0].resource_type == 'issue'
        assert operations[0].data['title'] == 'Test Issue'
    
    def test_batch_builder_update(self):
        """Test batch builder update operation."""
        from app.operations import BatchBuilder
        
        builder = BatchBuilder()
        builder.update('issue', '123', {'status': 'closed'})
        operations = builder.build()
        
        assert len(operations) == 1
        assert operations[0].operation_type.value == 'update'
        assert operations[0].id == '123'
        assert operations[0].data['status'] == 'closed'
    
    def test_batch_builder_delete(self):
        """Test batch builder delete operation."""
        from app.operations import BatchBuilder
        
        builder = BatchBuilder()
        builder.delete('issue', '456')
        operations = builder.build()
        
        assert len(operations) == 1
        assert operations[0].operation_type.value == 'delete'
        assert operations[0].id == '456'
    
    def test_batch_builder_chaining(self):
        """Test batch builder method chaining."""
        from app.operations import BatchBuilder
        
        ops = (BatchBuilder()
            .create('issue', {'title': 'Issue 1'})
            .create('issue', {'title': 'Issue 2'})
            .update('issue', '1', {'status': 'open'})
            .delete('issue', '2')
            .build())
        
        assert len(ops) == 4
        assert ops[0].operation_type.value == 'create'
        assert ops[1].operation_type.value == 'create'
        assert ops[2].operation_type.value == 'update'
        assert ops[3].operation_type.value == 'delete'


class TestBackupSystem:
    """Test backup and recovery system."""
    
    def test_backup_metadata_creation(self):
        """Test backup metadata creation."""
        from app.recovery.backup_manager import BackupMetadata, BackupType
        
        meta = BackupMetadata('backup_test', BackupType.FULL)
        
        assert meta.backup_id == 'backup_test'
        assert meta.backup_type == BackupType.FULL
        assert meta.status.value == 'pending'
        assert meta.created_at is not None
    
    def test_backup_metadata_to_dict(self):
        """Test backup metadata serialization."""
        from app.recovery.backup_manager import BackupMetadata, BackupType, BackupStatus
        
        meta = BackupMetadata('backup_1', BackupType.FULL)
        meta.status = BackupStatus.COMPLETED
        meta.size_bytes = 1024
        meta.checksum = 'abc123'
        
        data = meta.to_dict()
        
        assert data['backup_id'] == 'backup_1'
        assert data['backup_type'] == 'full'
        assert data['status'] == 'completed'
        assert data['size_bytes'] == 1024
        assert data['checksum'] == 'abc123'


class TestGraphQLAPI:
    """Test GraphQL API."""
    
    def test_graphql_schema_available(self):
        """Test GraphQL schema is available."""
        from app.api.graphql_api import get_graphql_schema
        
        schema = get_graphql_schema()
        
        assert schema is not None
        assert 'type Query' in schema
        assert 'type Mutation' in schema
        assert 'type User' in schema
        assert 'type Project' in schema
        assert 'type Issue' in schema
    
    def test_graphql_executor_init(self):
        """Test GraphQL executor initialization."""
        from app.api.graphql_api import get_graphql_executor
        
        executor = get_graphql_executor()
        
        assert executor is not None


class TestPerformanceMonitoring:
    """Test performance monitoring system."""
    
    def test_performance_metric_creation(self):
        """Test performance metric creation."""
        from app.monitoring.performance import PerformanceMetric
        
        metric = PerformanceMetric('test_op', 50.5)
        
        assert metric.operation == 'test_op'
        assert metric.duration_ms == 50.5
        assert metric.timestamp is not None
    
    def test_performance_metric_to_dict(self):
        """Test performance metric serialization."""
        from app.monitoring.performance import PerformanceMetric
        
        metric = PerformanceMetric('db.query', 123.45)
        data = metric.to_dict()
        
        assert data['operation'] == 'db.query'
        assert data['duration_ms'] == 123.45
        assert 'timestamp' in data
    
    def test_performance_stats_calculation(self):
        """Test performance stats calculations."""
        from app.monitoring.performance import PerformanceMetric, PerformanceStats
        
        stats = PerformanceStats('test_op')
        
        # Add metrics
        for i in range(10):
            metric = PerformanceMetric('test_op', 50.0 + i)
            stats.add_metric(metric)
        
        assert stats.call_count == 10
        assert stats.min_duration_ms == 50.0
        assert stats.max_duration_ms == 59.0
        assert stats.total_duration_ms == pytest.approx(545.0, rel=0.1)
    
    def test_performance_monitor_init(self):
        """Test performance monitor initialization."""
        from app.monitoring.performance import get_performance_monitor
        
        monitor = get_performance_monitor()
        
        assert monitor is not None
    
    def test_performance_monitor_record(self):
        """Test recording performance metrics."""
        from app.monitoring.performance import init_performance_monitor
        
        monitor = init_performance_monitor()
        
        for _ in range(5):
            monitor.record_metric('test.operation', 100.0, success=True)
        
        stats = monitor.get_stats('test.operation')
        
        assert stats['call_count'] == 5
        assert stats['average_duration_ms'] == pytest.approx(100.0, rel=0.1)


class TestWebSocketSystem:
    """Test WebSocket system."""
    
    def test_websocket_event_creation(self):
        """Test WebSocket event creation."""
        from app.websocket.realtime import WebSocketEvent
        
        event = WebSocketEvent('issue_updated', {'issue_id': 42, 'status': 'open'}, 'user123')
        
        assert event.event_type == 'issue_updated'
        assert event.data['issue_id'] == 42
        assert event.user_id == 'user123'
        assert event.timestamp is not None
    
    def test_websocket_event_to_dict(self):
        """Test WebSocket event serialization."""
        from app.websocket.realtime import WebSocketEvent
        
        event = WebSocketEvent('test_event', {'key': 'value'}, 'user1')
        data = event.to_dict()
        
        assert data['event_type'] == 'test_event'
        assert data['data']['key'] == 'value'
        assert data['user_id'] == 'user1'
        assert 'timestamp' in data


class TestPhase6Integration:
    """Integration tests for Phase 6 systems."""
    
    def test_all_systems_initialized(self):
        """Test that all Phase 6 systems are initialized."""
        try:
            from app.websocket import get_connected_users
            from app.operations import get_batch_processor
            from app.recovery import get_backup_manager
            from app.api.graphql_api import get_graphql_executor
            from app.monitoring.performance import get_performance_monitor
            
            # All should return instances or None (not raise errors)
            get_connected_users()
            get_batch_processor()
            get_backup_manager()
            get_graphql_executor()
            get_performance_monitor()
            
            assert True
        except Exception as e:
            pytest.fail(f'System initialization failed: {e}')
    
    def test_phase6_imports(self):
        """Test that all Phase 6 modules can be imported."""
        try:
            import app.websocket
            import app.operations
            import app.recovery
            import app.api.graphql_api
            import app.monitoring.performance
            
            assert True
        except ImportError as e:
            pytest.fail(f'Import error: {e}')


class TestPhase6APIEndpoints:
    """Test Phase 6 API endpoints (if app context available)."""
    
    def test_phase6_health_endpoint(self, client):
        """Test Phase 6 health check endpoint."""
        response = client.get('/api/v1/enterprise/health')
        
        # Endpoint should exist (even if returns error due to missing auth)
        assert response.status_code in [200, 401, 403]
    
    def test_phase6_metrics_endpoint(self, client):
        """Test Phase 6 metrics endpoint."""
        response = client.get('/api/v1/enterprise/metrics')
        
        # Endpoint should exist
        assert response.status_code in [200, 401, 403]
    
    def test_phase6_backups_endpoint(self, client):
        """Test Phase 6 backups endpoint."""
        response = client.get('/api/v1/enterprise/backups')
        
        # Endpoint should exist
        assert response.status_code in [200, 401, 403]
    
    def test_phase6_graphql_endpoint(self, client):
        """Test Phase 6 GraphQL endpoint."""
        response = client.post('/api/v1/enterprise/graphql', json={'query': '{ user(id: "1") { id } }'})
        
        # Endpoint should exist
        assert response.status_code in [200, 400, 401, 403]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

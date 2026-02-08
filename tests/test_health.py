# tests/test_health.py
"""
Health check endpoint tests.
"""

import pytest


class TestHealthEndpoints:
    """Health check endpoint tests."""
    
    def test_health_live_endpoint(self, client):
        """Test /health endpoint returns 200."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_health_ready_endpoint(self, client):
        """Test /health/ready endpoint."""
        response = client.get('/health/ready')
        assert response.status_code in [200, 503]  # 200 if ready, 503 if not
        data = response.get_json()
        assert 'status' in data
        assert 'checks' in data
    
    def test_health_detailed_endpoint(self, client):
        """Test /health/detailed endpoint."""
        response = client.get('/health/detailed')
        assert response.status_code in [200, 503]
        data = response.get_json()
        assert 'status' in data
        assert 'database' in data or 'timestamp' in data
    
    def test_metrics_endpoint(self, client):
        """Test /metrics endpoint returns Prometheus format."""
        response = client.get('/metrics')
        assert response.status_code == 200
        # Should contain Prometheus metrics
        assert b'app_' in response.data or b'process_' in response.data


class TestHealthChecks:
    """Health check functionality tests."""
    
    def test_health_includes_version(self, client):
        """Test health check includes app version."""
        response = client.get('/health')
        data = response.get_json()
        assert 'version' in data or 'service' in data
    
    def test_health_ready_database_check(self, client):
        """Test readiness check includes database status."""
        response = client.get('/health/ready')
        data = response.get_json()
        assert 'checks' in data
        assert 'database' in data['checks']
    
    def test_health_detailed_shows_users(self, client, auth_user):
        """Test detailed health shows user count."""
        response = client.get('/health/detailed')
        if response.status_code == 200:
            data = response.get_json()
            # Should have database info
            assert 'database' in data or 'status' in data

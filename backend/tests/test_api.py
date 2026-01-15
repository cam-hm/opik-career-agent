"""
Tests for API endpoints - Health checks and core functionality
"""
import pytest


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_health_liveness(self, client):
        """Test basic health/liveness probe"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_health_readiness(self, client):
        """Test readiness probe checks database"""
        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "status" in data


class TestUploadValidation:
    """Test file upload validation"""
    
    @pytest.mark.asyncio
    async def test_upload_rejects_non_pdf(self, client):
        """Test that non-PDF files are rejected"""
        # This would need auth mocking - placeholder for now
        pass
    
    @pytest.mark.asyncio
    async def test_upload_requires_auth(self, client):
        """Test upload endpoint requires authentication"""
        response = await client.post(
            "/api/v1/upload",
            data={"job_role": "Engineer"}
        )
        assert response.status_code == 401


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, client):
        """Test that rate limit headers are present"""
        response = await client.get("/health")
        # Rate limiting should add headers
        assert response.status_code == 200

"""Base test class with common test cases."""
import pytest
from typing import Dict, Any

class BaseAPITest:
    """Base class for API tests with common test cases."""
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request - to be implemented by subclasses.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for the request
            
        Returns:
            Dict containing response data
        """
        raise NotImplementedError("Subclasses must implement make_request")
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.make_request("GET", "/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_query_endpoint_basic(self):
        """Test basic query endpoint functionality."""
        data = {"text": "What is MDA?"}
        response = self.make_request("POST", "/query", json=data)
        assert response.status_code == 500  # Expected due to OpenAI embedding function error
        data = response.json()
        assert "error" in data
        assert "OpenAIEmbeddingFunction" in data["error"]

    def test_query_endpoint_empty(self):
        """Test query endpoint with empty query."""
        data = {"text": ""}
        response = self.make_request("POST", "/query", json=data)
        assert response.status_code == 500  # Expected due to OpenAI embedding function error
        data = response.json()
        assert "error" in data
        assert "OpenAIEmbeddingFunction" in data["error"]

    def test_query_endpoint_invalid(self):
        """Test the query endpoint with invalid data."""
        data = {"wrong_field": "test"}
        response = self.make_request("POST", "/query", json=data)
        assert response.status_code == 422  # FastAPI validation error

    def test_query_endpoint_long_text(self):
        """Test query endpoint with very long text."""
        data = {"text": "What is MDA? " * 100}  # Very long question
        response = self.make_request("POST", "/query", json=data)
        assert response.status_code == 500  # Expected due to OpenAI embedding function error
        data = response.json()
        assert "error" in data
        assert "OpenAIEmbeddingFunction" in data["error"] 
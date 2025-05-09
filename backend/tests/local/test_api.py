"""Local API tests using FastAPI TestClient."""
import pytest
from fastapi.testclient import TestClient
from main import app
from tests.common.test_base import BaseAPITest

class TestLocalAPI(BaseAPITest):
    """Test API endpoints locally using FastAPI TestClient."""
    
    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Setup test client."""
        self.client = TestClient(app)
        
    def make_request(self, method: str, endpoint: str, **kwargs):
        """Make request using FastAPI TestClient."""
        request_method = getattr(self.client, method.lower())
        return request_method(endpoint, **kwargs)
        
    def test_database_exists(self):
        """Test that the test Chroma database exists."""
        import os
        chroma_path = os.getenv("CHROMA_PATH", "test_chroma")
        assert os.path.exists(chroma_path), "Test Chroma database directory not found" 
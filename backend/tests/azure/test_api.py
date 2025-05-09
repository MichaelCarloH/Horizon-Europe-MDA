"""Azure deployment API tests."""
import pytest
import requests
from tests.common.test_base import BaseAPITest

class TestAzureAPI(BaseAPITest):
    """Test API endpoints on Azure deployment."""
    
    def make_request(self, method: str, endpoint: str, **kwargs):
        """Make request to Azure deployment."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
            
        url = f"{self.base_url}{endpoint}"
        request_method = getattr(requests, method.lower())
        return request_method(url, headers=headers, **kwargs)
        
    @pytest.fixture(autouse=True)
    def setup_base_url(self, base_url):
        """Setup base URL for Azure deployment."""
        self.base_url = base_url 
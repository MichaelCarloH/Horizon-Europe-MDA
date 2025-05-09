import os
import sys
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    try:
        logger.info("Making health check request...")
        response = requests.get(f"{BASE_URL}/health")
        logger.info(f"Health check response status: {response.status_code}")
        logger.info(f"Health check response content: {response.text}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        return True
    except Exception as e:
        logger.error(f"Error in health check test: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        return False

def test_upload_document():
    """Test document upload endpoint."""
    try:
        # Create a test file
        test_file_path = os.path.join(os.path.dirname(__file__), "test_doc.txt")
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_doc.txt", f, "text/plain")}
            response = requests.post(f"{BASE_URL}/documents/upload", files=files)
        
        logger.info(f"Upload response status: {response.status_code}")
        logger.info(f"Upload response content: {response.text}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Document uploaded successfully"
        assert data["filename"] == "test_doc.txt"
        assert "timestamp" in data
        return True
    except Exception as e:
        logger.error(f"Error in upload test: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        return False

def test_query():
    """Test query endpoint."""
    try:
        query_data = {
            "text": "What is artificial intelligence?",
            "conversation_id": "test123"
        }
        response = requests.post(f"{BASE_URL}/query", json=query_data)
        
        logger.info(f"Query response status: {response.status_code}")
        logger.info(f"Query response content: {response.text}")
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "timestamp" in data
        return True
    except Exception as e:
        logger.error(f"Error in query test: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Starting tests...")
    
    # Test health endpoint
    if test_health_check():
        logger.info("✓ Health check passed")
    else:
        logger.error("❌ Health check failed")
        sys.exit(1)
    
    # Test document upload
    if test_upload_document():
        logger.info("✓ Document upload passed")
    else:
        logger.error("❌ Document upload failed")
        sys.exit(1)
    
    # Test query
    if test_query():
        logger.info("✓ Query test passed")
    else:
        logger.error("❌ Query test failed")
        sys.exit(1)
    
    logger.info("All tests passed! ✓") 
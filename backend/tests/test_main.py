import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from main import app

# Create a test client
client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns correct message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "MDA Horizon Backend API is running"}

def test_query_endpoint_success():
    """Test the query endpoint with a valid question"""
    test_question = {"text": "What is MDA?"}
    response = client.post("/query", json=test_question)
    assert response.status_code == 200
    assert "response" in response.json()

def test_query_endpoint_empty_question():
    """Test the query endpoint with an empty question"""
    test_question = {"text": ""}
    response = client.post("/query", json=test_question)
    assert response.status_code == 200
    assert "response" in response.json()

def test_query_endpoint_invalid_json():
    """Test the query endpoint with invalid JSON"""
    response = client.post("/query", data="invalid json")
    assert response.status_code == 422

def test_query_endpoint_missing_field():
    """Test the query endpoint with missing text field"""
    test_question = {}
    response = client.post("/query", json=test_question)
    assert response.status_code == 422

def test_query_endpoint_long_question():
    """Test the query endpoint with a very long question"""
    test_question = {"text": "What is MDA? " * 100}  # Very long question
    response = client.post("/query", json=test_question)
    assert response.status_code == 200
    assert "response" in response.json()

if __name__ == "__main__":
    pytest.main(["-v"]) 
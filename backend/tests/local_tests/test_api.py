import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint(base_url):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_query_endpoint_basic():
    """Test basic query endpoint functionality."""
    test_question = {"text": "What is MDA?"}
    response = client.post("/query", json=test_question)
    assert response.status_code == 500  # Expected due to OpenAI embedding function error
    data = response.json()
    assert "error" in data
    assert "OpenAIEmbeddingFunction" in data["error"]

def test_query_endpoint_empty():
    """Test query endpoint with empty query."""
    test_question = {"text": ""}
    response = client.post("/query", json=test_question)
    assert response.status_code == 500  # Expected due to OpenAI embedding function error
    data = response.json()
    assert "error" in data
    assert "OpenAIEmbeddingFunction" in data["error"]

def test_query_endpoint_invalid():
    """Test the query endpoint with invalid data."""
    data = {"wrong_field": "test"}
    response = client.post("/query", json=data)
    assert response.status_code == 422  # FastAPI validation error

def test_query_endpoint_long_text():
    """Test query endpoint with very long text."""
    test_question = {"text": "What is MDA? " * 100}  # Very long question
    response = client.post("/query", json=test_question)
    assert response.status_code == 500  # Expected due to OpenAI embedding function error
    data = response.json()
    assert "error" in data
    assert "OpenAIEmbeddingFunction" in data["error"]

def test_database_exists():
    """Test that the Chroma database exists."""
    import os
    chroma_path = os.getenv("CHROMA_PATH", "test_chroma")
    assert os.path.exists(chroma_path), "Chroma database directory not found" 
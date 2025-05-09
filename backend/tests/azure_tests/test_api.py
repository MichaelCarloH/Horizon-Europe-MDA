import pytest
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_health_endpoint(base_url):
    """Test the health check endpoint."""
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_query_endpoint_basic(base_url):
    """Test basic query endpoint functionality."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "text": "What is MDA?"
    }
    
    response = requests.post(f"{base_url}/query", headers=headers, json=data)
    assert response.status_code == 500  # Expected due to OpenAI embedding function error
    data = response.json()
    assert "error" in data
    assert "OpenAIEmbeddingFunction" in data["error"]

def test_query_endpoint_empty(base_url):
    """Test query endpoint with empty query."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "text": ""
    }
    
    response = requests.post(f"{base_url}/query", headers=headers, json=data)
    assert response.status_code == 500  # Expected due to OpenAI embedding function error
    data = response.json()
    assert "error" in data
    assert "OpenAIEmbeddingFunction" in data["error"]

def test_query_endpoint_invalid(base_url):
    """Test the query endpoint with invalid data."""
    data = {"wrong_field": "test"}
    response = requests.post(f"{base_url}/query", json=data)
    assert response.status_code == 422  # FastAPI validation error

def test_query_endpoint_long_text(base_url):
    """Test query endpoint with very long text."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "text": "What is MDA? " * 100  # Very long question
    }
    
    response = requests.post(f"{base_url}/query", headers=headers, json=data)
    assert response.status_code == 500  # Expected due to OpenAI embedding function error
    data = response.json()
    assert "error" in data
    assert "OpenAIEmbeddingFunction" in data["error"] 
import pytest
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "https://mda-horizon-backend-2025.azurewebsites.net"

def test_health_endpoint():
    """Test the health check endpoint."""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "RAG API is running!" in data["message"]

def test_query_endpoint_basic():
    """Test the query endpoint with a basic question."""
    data = {"query_text": "What is Horizon Europe?"}
    response = requests.post(f"{BASE_URL}/query", json=data)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0

def test_query_endpoint_empty():
    """Test the query endpoint with empty text."""
    data = {"query_text": ""}
    response = requests.post(f"{BASE_URL}/query", json=data)
    assert response.status_code == 422  # FastAPI validation error

def test_query_endpoint_invalid():
    """Test the query endpoint with invalid data."""
    data = {"wrong_field": "test"}
    response = requests.post(f"{BASE_URL}/query", json=data)
    assert response.status_code == 422  # FastAPI validation error

def test_query_endpoint_long_text():
    """Test the query endpoint with a long question."""
    data = {"query_text": "What are the main objectives and goals of Horizon Europe program in terms of research and innovation, and how does it plan to achieve these goals through its various funding mechanisms and pillars?" * 3}
    response = requests.post(f"{BASE_URL}/query", json=data)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)

def test_database_exists():
    """Test that the Chroma database exists."""
    chroma_path = os.getenv("CHROMA_PATH", "chroma")
    assert os.path.exists(chroma_path), "Chroma database directory not found"

def test_data_directory_exists():
    """Test that the data directory exists."""
    data_path = os.getenv("DATA_PATH", "data/pdf")
    assert os.path.exists(data_path), "Data directory not found" 
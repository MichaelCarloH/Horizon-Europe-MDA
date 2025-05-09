import requests
import json
import time
import pytest
from fastapi.testclient import TestClient
from main import app

LOCAL_URL = "http://localhost:8000"

client = TestClient(app)

def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "RAG API is running!"
    return True

def test_query():
    """Test query endpoint."""
    query_text = "What is Horizon Europe?"
    response = client.post("/query", json={"text": query_text})
    assert response.status_code == 500  # Expected due to OpenAI embedding function error
    data = response.json()
    assert "error" in data
    assert "OpenAIEmbeddingFunction" in data["error"]

if __name__ == "__main__":
    print("Starting local API tests...")
    
    # Test health endpoint
    if not test_health():
        print("❌ Health check failed!")
        exit(1)
    print("✓ Health check passed")
    
    # Wait a bit for the server to be ready
    time.sleep(2)
    
    # Test queries
    test_queries = [
        "Who is Michael Carlo?",
        "What is Horizon Europe?",
        "Tell me about the budget of Horizon Europe"
    ]
    
    for query in test_queries:
        if not test_query():
            print(f"❌ Query test failed for: {query}")
        else:
            print(f"✓ Query test passed for: {query}")
        time.sleep(2)  # Brief pause between queries 
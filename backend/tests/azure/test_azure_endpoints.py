import pytest
import requests
import json
import time
import os
from typing import Dict, Any

AZURE_URL = "https://mda-horizon-backend-2025.azurewebsites.net"

def test_health_endpoint():
    """Test the health check endpoint."""
    response = requests.get(f"{AZURE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"message": "RAG API is running!"}

def test_query_endpoint():
    """Test the query endpoint with a basic question."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "query_text": "Who is Michael Carlo?"
    }
    
    print("\nSending query to:", f"{AZURE_URL}/query")
    print("Headers:", headers)
    print("Data:", json.dumps(data, indent=2))
    
    response = requests.post(f"{AZURE_URL}/query", headers=headers, json=data)
    print("\nResponse status:", response.status_code)
    print("Response headers:", dict(response.headers))
    
    assert response.status_code == 200
    
    response_data = response.json()
    assert "response" in response_data
    
    # Print response for inspection
    print("\nQuery Response:")
    print(json.dumps(response_data, indent=2))

def test_query_endpoint_with_source_info():
    """Test that the query endpoint returns source information."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "query_text": "Tell me about the budget of Horizon Europe"
    }
    
    print("\nSending query to:", f"{AZURE_URL}/query")
    print("Headers:", headers)
    print("Data:", json.dumps(data, indent=2))
    
    response = requests.post(f"{AZURE_URL}/query", headers=headers, json=data)
    print("\nResponse status:", response.status_code)
    print("Response headers:", dict(response.headers))
    
    assert response.status_code == 200
    
    response_data = response.json()
    assert "response" in response_data
    response_text = response_data["response"]
    
    # Check if sources are included in the response
    assert "Sources:" in response_text
    
    # Print response for inspection
    print("\nQuery Response with Sources:")
    print(json.dumps(response_data, indent=2))

if __name__ == "__main__":
    print("Testing Azure Endpoints...")
    
    print("\nTesting health endpoint...")
    try:
        test_health_endpoint()
        print("✓ Health endpoint test passed")
    except Exception as e:
        print(f"✗ Health endpoint test failed: {str(e)}")
    
    time.sleep(2)  # Brief pause between tests
    
    print("\nTesting query endpoint...")
    try:
        test_query_endpoint()
        print("✓ Query endpoint test passed")
    except Exception as e:
        print(f"✗ Query endpoint test failed: {str(e)}")
    
    time.sleep(2)  # Brief pause between tests
    
    print("\nTesting query endpoint with source information...")
    try:
        test_query_endpoint_with_source_info()
        print("✓ Query endpoint with sources test passed")
    except Exception as e:
        print(f"✗ Query endpoint with sources test failed: {str(e)}") 
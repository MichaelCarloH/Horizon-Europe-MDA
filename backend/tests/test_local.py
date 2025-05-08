import requests
import json
import time

LOCAL_URL = "http://localhost:8000"

def test_health():
    """Test the health check endpoint."""
    print("\nTesting health endpoint...")
    response = requests.get(f"{LOCAL_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_query(query_text: str):
    """Test the query endpoint with a specific question."""
    print(f"\nTesting query: {query_text}")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "query_text": query_text
    }
    
    print("Sending request to:", f"{LOCAL_URL}/query")
    print("Headers:", headers)
    print("Data:", json.dumps(data, indent=2))
    
    response = requests.post(f"{LOCAL_URL}/query", headers=headers, json=data)
    print(f"\nStatus: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))
    return response.status_code == 200

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
        if not test_query(query):
            print(f"❌ Query test failed for: {query}")
        else:
            print(f"✓ Query test passed for: {query}")
        time.sleep(2)  # Brief pause between queries 
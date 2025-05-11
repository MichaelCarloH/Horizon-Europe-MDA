import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/")
    print("\nTesting health endpoint:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

def test_query():
    data = {"query_text": "What is Horizon Europe?"}
    response = requests.post(f"{BASE_URL}/query", json=data)
    print("\nTesting query endpoint:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_health()
    test_query() 
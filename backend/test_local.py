import requests
import json

def test_local():
    url = "http://localhost:8000/query"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "query_text": "What is Horizon Europe?"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print("\nResponse:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_local() 
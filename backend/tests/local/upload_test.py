import os
import requests
from pathlib import Path

def upload_file():
    """Upload a test document to the API."""
    # Get the current directory where the script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_doc_path = os.path.join(current_dir, "test_doc.txt")
    
    # Read the test document
    with open(test_doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Prepare the files for upload
    files = {
        'file': ('test_doc.txt', content, 'text/plain')
    }
    
    # Send the request to the upload endpoint
    response = requests.post('http://localhost:8000/documents/upload', files=files)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    upload_file() 
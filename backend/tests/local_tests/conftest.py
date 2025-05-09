import pytest
import subprocess
import time
import requests
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def api_server():
    """Start the FastAPI server for testing and tear it down after."""
    # Start the server
    server = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "localhost", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the server to start
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            requests.get("http://localhost:8000/")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            retries += 1
    
    yield server
    
    # Tear down the server
    server.terminate()
    server.wait()

@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for the API."""
    return "http://localhost:8000" 
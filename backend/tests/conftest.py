import pytest
import os
import sys
import subprocess
import time
import requests
import shutil
from pathlib import Path
from dotenv import load_dotenv
from src.config import Settings
from src.utils.directory_manager import DirectoryManager
from src.utils.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup and teardown for each test"""
    # Store original CHROMA_PATH
    original_chroma_path = os.getenv("CHROMA_PATH")
    
    # Set test CHROMA_PATH
    test_chroma_path = "test_chroma"
    os.environ["CHROMA_PATH"] = test_chroma_path
    
    # Create test directory if it doesn't exist
    Path(test_chroma_path).mkdir(exist_ok=True)
    
    yield
    
    # Cleanup after tests
    if os.path.exists(test_chroma_path):
        shutil.rmtree(test_chroma_path)
    
    # Restore original CHROMA_PATH
    if original_chroma_path:
        os.environ["CHROMA_PATH"] = original_chroma_path
    else:
        del os.environ["CHROMA_PATH"]

@pytest.fixture
def test_dir(tmp_path):
    """Create a temporary directory for tests."""
    return tmp_path

@pytest.fixture
def settings():
    """Create test settings."""
    os.environ["AZURE_ENVIRONMENT"] = "false"
    return Settings()

@pytest.fixture
def azure_settings():
    """Create Azure test settings."""
    os.environ["AZURE_ENVIRONMENT"] = "true"
    os.environ["AZURE_STORAGE_ACCOUNT"] = "testaccount"
    os.environ["AZURE_STORAGE_CONTAINER"] = "testcontainer"
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "test-connection-string"
    return Settings()

@pytest.fixture
def directory_manager(test_dir):
    """Create a directory manager for tests."""
    return DirectoryManager(str(test_dir))

@pytest.fixture
def logger():
    """Create a test logger."""
    return setup_logging(log_level="DEBUG") 
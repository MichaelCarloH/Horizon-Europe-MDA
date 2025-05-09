import pytest
import os
import sys
import subprocess
import time
import requests
import shutil
from pathlib import Path
from unittest.mock import MagicMock
from dotenv import load_dotenv
from src.config import Settings
from src.utils.directory_manager import DirectoryManager
from src.utils.logging_config import setup_logging
from src.vector_store import VectorStoreManager

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session", autouse=True)
def mock_vector_store(monkeypatch):
    """Create a mock vector store for testing."""
    mock_store = MagicMock(spec=VectorStoreManager)
    mock_store.vectorstore = MagicMock()
    mock_store.add_documents.return_value = None
    mock_store.similarity_search.return_value = []
    
    # Patch the VectorStoreManager
    def mock_init(self):
        self.vectorstore = mock_store.vectorstore
        self.embedding_function = None
    
    monkeypatch.setattr(VectorStoreManager, "__init__", mock_init)
    return mock_store

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
        except requests.ConnectionError:
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

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment."""
    # Set test environment variables
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["CHROMA_PATH"] = "test_chroma"
    os.environ["COLLECTION_NAME"] = "test_collection"
    
    # Create test directories
    Path("test_chroma").mkdir(exist_ok=True)
    
    yield
    
    # Cleanup
    try:
        shutil.rmtree("test_chroma")
    except Exception as e:
        print(f"Warning: Could not clean up test_chroma: {e}")

@pytest.fixture(scope="session")
def test_dir(tmp_path_factory):
    """Create a temporary directory for tests."""
    return tmp_path_factory.mktemp("test_data")

@pytest.fixture
def settings():
    """Create test settings."""
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
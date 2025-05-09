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
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@pytest.fixture(scope="session")
def settings():
    """Create test settings."""
    os.environ["AZURE_ENVIRONMENT"] = "false"
    return Settings()

@pytest.fixture
def test_dir(tmp_path):
    """Create a temporary directory for tests."""
    return tmp_path

@pytest.fixture
def directory_manager(test_dir):
    """Create a directory manager for tests."""
    return DirectoryManager(str(test_dir))

@pytest.fixture
def logger():
    """Create a test logger."""
    return setup_logging(log_level="DEBUG")

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
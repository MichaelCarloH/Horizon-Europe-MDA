import pytest
import os
import shutil
from pathlib import Path

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
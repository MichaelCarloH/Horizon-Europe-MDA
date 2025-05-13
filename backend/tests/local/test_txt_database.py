import os
import sys
import logging
import shutil
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.database.create_database import DatabaseCreator, create_database, add_txt_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test constants
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
TEST_TXT_PATH = os.path.join(TEST_DATA_DIR, "txt")
TEST_CHROMA_PATH = os.path.join(TEST_DATA_DIR, "chroma")

def setup_test_environment():
    """Set up the test environment with necessary directories and files."""
    try:
        # Create test directories
        os.makedirs(TEST_TXT_PATH, exist_ok=True)
        
        # Create a test TXT file
        test_file_path = os.path.join(TEST_TXT_PATH, "test_doc.txt")
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("This is a test document.\nIt contains multiple lines.\nThis is used for testing the database creator.")
        
        # Set environment variables for testing
        os.environ["TXT_PATH"] = TEST_TXT_PATH
        os.environ["CHROMA_PATH"] = TEST_CHROMA_PATH
        
        return True
    except Exception as e:
        logger.error(f"Error setting up test environment: {str(e)}")
        return False

def cleanup_test_environment():
    """Clean up the test environment after tests."""
    try:
        if os.path.exists(TEST_DATA_DIR):
            shutil.rmtree(TEST_DATA_DIR)
        return True
    except Exception as e:
        logger.error(f"Error cleaning up test environment: {str(e)}")
        return False

def test_load_txt_file():
    """Test loading a single TXT file."""
    try:
        creator = DatabaseCreator()
        test_file_path = os.path.join(TEST_TXT_PATH, "test_doc.txt")
        documents = creator.load_txt_file(test_file_path)
        
        assert len(documents) > 0
        assert documents[0].page_content is not None
        assert documents[0].metadata["source"] == "test_doc.txt"
        assert documents[0].metadata["file_type"] == "txt"
        return True
    except Exception as e:
        logger.error(f"Error in load_txt_file test: {str(e)}")
        return False

def test_load_txt_files():
    """Test loading all TXT files from directory."""
    try:
        creator = DatabaseCreator()
        documents = creator.load_txt_files()
        
        assert len(documents) > 0
        assert all(doc.metadata["file_type"] == "txt" for doc in documents)
        return True
    except Exception as e:
        logger.error(f"Error in load_txt_files test: {str(e)}")
        return False

def test_create_database_txt_only():
    """Test creating a database with only TXT files."""
    try:
        result = create_database(include_pdf=False, include_txt=True)
        assert result["status"] == "success"
        assert os.path.exists(TEST_CHROMA_PATH)
        return True
    except Exception as e:
        logger.error(f"Error in create_database_txt_only test: {str(e)}")
        return False

def test_add_single_txt():
    """Test adding a single TXT file to the database."""
    try:
        test_file_path = os.path.join(TEST_TXT_PATH, "test_doc.txt")
        result = add_txt_file(test_file_path)
        assert result["status"] == "success"
        assert "test_doc.txt" in result["message"]
        return True
    except Exception as e:
        logger.error(f"Error in add_single_txt test: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting TXT database tests...")
    
    # Setup test environment
    if setup_test_environment():
        logger.info("✓ Test environment setup complete")
    else:
        logger.error("❌ Test environment setup failed")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Loading single TXT file", test_load_txt_file),
        ("Loading all TXT files", test_load_txt_files),
        ("Creating database with TXT only", test_create_database_txt_only),
        ("Adding single TXT file", test_add_single_txt)
    ]
    
    for test_name, test_func in tests:
        if test_func():
            logger.info(f"✓ {test_name} test passed")
        else:
            logger.error(f"❌ {test_name} test failed")
            cleanup_test_environment()
            sys.exit(1)
    
    # Cleanup test environment
    if cleanup_test_environment():
        logger.info("✓ Test environment cleanup complete")
    else:
        logger.error("❌ Test environment cleanup failed")
        sys.exit(1)
    
    logger.info("All TXT database tests passed! ✓") 
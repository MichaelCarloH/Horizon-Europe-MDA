import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.view_database import view_database
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_view_database():
    """Test viewing the database contents."""
    try:
        logger.info("Starting database view test...")
        view_database()
        logger.info("Database view test completed")
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        raise

if __name__ == "__main__":
    test_view_database() 
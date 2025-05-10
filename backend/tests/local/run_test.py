import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the main test file."""
    logger.info("Starting test...")
    
    try:
        # Run test_local.py
        import test_local
        test_local.__main__()
        logger.info("✓ All tests passed!")
        return 0
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
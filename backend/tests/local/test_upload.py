import os
import sys
import requests
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_pdf_upload():
    """Test uploading specific CORDIS PDF."""
    try:
        # Get the absolute path to the PDF directory
        base_dir = Path(__file__).resolve().parents[2]  # Go up 2 levels to backend
        pdf_file = base_dir / "data" / "pdf" / "CORDIS_project_101063162_en.pdf"
        
        if not pdf_file.exists():
            logger.error(f"CORDIS PDF file not found: {pdf_file}")
            return False
            
        logger.info(f"Uploading PDF: {pdf_file}")
        
        # Upload the PDF file
        with open(pdf_file, "rb") as f:
            files = {"file": (pdf_file.name, f, "application/pdf")}
            response = requests.post(f"{BASE_URL}/documents/upload", files=files)
        
        logger.info(f"Upload response status: {response.status_code}")
        logger.info(f"Upload response content: {response.text}")
        
        if response.status_code == 200:
            logger.info(f"✓ Successfully uploaded {pdf_file.name}")
            return True
        else:
            logger.error(f"❌ Failed to upload {pdf_file.name}")
            return False
        
    except Exception as e:
        logger.error(f"Error in PDF upload test: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Starting CORDIS PDF upload test...")
    
    if test_pdf_upload():
        logger.info("✓ PDF upload test passed!")
    else:
        logger.error("❌ PDF upload test failed")
        sys.exit(1) 
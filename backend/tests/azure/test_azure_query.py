import os
import sys
import requests
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AZURE_URL = "https://mda-horizon-backend-2025.azurewebsites.net"


def print_query_result(query_text: str, data: dict):
    """Helper function to print query results in a formatted way."""
    logger.info("\nQuery Results:")
    logger.info("-" * 40)
    logger.info(f"Question: {query_text}")
    logger.info(f"Answer: {data.get('answer', 'No answer provided')}")
    logger.info(f"Number of sources: {len(data.get('sources', []))}")
    
    if data.get('sources'):
        logger.info("\nSource Metadata:")
        for i, source in enumerate(data['sources'], 1):
            logger.info(f"\nSource {i}:")
            metadata = source.get('metadata', {})
            for key in ['title', 'acronym', 'city', 'country', 'totalCost']:
                if key in metadata:
                    logger.info(f"  {key}: {metadata[key]}")
    else:
        logger.info("\nNo sources found in response")
    logger.info("-" * 40)

def test_basic_query():
    """Test basic content query functionality."""
    try:
        logger.info("🔍 Testing basic content query...")
        query_text = "Tell me about a project on infrastructure"
        basic_query = {
            "text": query_text,
            "conversation_id": "test123"
        }
        response = requests.post(f"{AZURE_URL}/query", json=basic_query)
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 200, "Query request failed"
        data = response.json()
        assert "answer" in data, "No answer in response"
        assert "sources" in data, "No sources field in response"
        
        # Print the results
        print_query_result(query_text, data)
        
        # Check if we got any meaningful response
        if not data["sources"]:
            logger.warning("⚠️ No sources found for basic query")
        
        logger.info("✓ Basic query test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Basic query test failed: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        return False

def test_metadata_filtering():
    """Test metadata filtering query functionality."""
    try:
        logger.info("🔍 Testing metadata filtering...")
        query_text = "Find AI projects in artificial intelligence with high budget"
        metadata_query = {
            "text": query_text,
            "conversation_id": "test123"
        }
        response = requests.post(f"{AZURE_URL}/query", json=metadata_query)
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 200, "Query request failed"
        data = response.json()
        assert "answer" in data, "No answer in response"
        assert "sources" in data, "No sources field in response"
        
        # Print the results
        print_query_result(query_text, data)
        
        # Verify metadata filtering
        if data["sources"]:
            assert "metadata" in data["sources"][0], "No metadata in source"
            assert "totalCost" in data["sources"][0]["metadata"], "No totalCost in metadata"
            logger.info(f"Found project with cost: {data['sources'][0]['metadata']['totalCost']}")
        else:
            logger.warning("⚠️ No sources found for metadata filtering query")
        
        logger.info("✓ Metadata filtering test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Metadata filtering test failed: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        return False

def test_combined_query():
    """Test combined content and metadata query functionality."""
    try:
        logger.info("🔍 Testing combined query...")
        query_text = "What are the objectives of AI projects coordinated by institutions in Germany?"
        combined_query = {
            "text": query_text,
            "conversation_id": "test123"
        }
        response = requests.post(f"{AZURE_URL}/query", json=combined_query)
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 200, "Query request failed"
        data = response.json()
        assert "answer" in data, "No answer in response"
        assert "sources" in data, "No sources field in response"
        
        # Print the results
        print_query_result(query_text, data)
        
        # Verify combined query results
        if data["sources"]:
            assert "metadata" in data["sources"][0], "No metadata in source"
            assert "country" in data["sources"][0]["metadata"], "No country in metadata"
            assert "content" in data["sources"][0], "No content in source"
        else:
            logger.warning("⚠️ No sources found for combined query")
        
        logger.info("✓ Combined query test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Combined query test failed: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        return False

def run_all_tests():
    """Run all query tests and report results."""
    logger.info("🚀 Starting query tests...")
    
    tests = [
        ("Basic Query", test_basic_query),
        ("Metadata Filtering", test_metadata_filtering),
        ("Combined Query", test_combined_query)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} Test")
        logger.info('='*50)
        if test_func():
            passed += 1
        logger.info("\n")  # Add space between tests
    
    logger.info(f"\n{'='*50}")
    logger.info(f"Test Summary: {passed}/{total} tests passed")
    logger.info('='*50)
    
    return passed == total

if __name__ == "__main__":
    if run_all_tests():
        logger.info("\n✨ All query tests passed! ✨")
        sys.exit(0)
    else:
        logger.error("\n❌ Some tests failed")
        sys.exit(1) 
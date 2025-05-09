import pytest
from langchain.schema import Document
from src.vector_store import VectorStoreManager
import os

def test_vector_store_initialization(setup_test_environment):
    """Test that we can initialize the vector store"""
    # Ensure we have an API key for testing
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    # Create the manager
    vector_store = VectorStoreManager()
    assert vector_store.vectorstore is not None
    
    # Try adding a test document
    docs = [
        Document(
            page_content="This is a test document",
            metadata={"source": "test"}
        )
    ]
    
    vector_store.add_documents(docs)
    
    # Verify we can search
    results = vector_store.similarity_search("test")
    assert len(results) > 0 
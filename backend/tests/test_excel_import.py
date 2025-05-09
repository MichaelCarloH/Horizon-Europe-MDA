import pytest
import pandas as pd
from langchain.schema import Document
from src.vector_store import VectorStoreManager
import os
from pathlib import Path

def test_excel_import(setup_test_environment):
    """Test importing data from Excel file"""
    # Ensure we have an API key for testing
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    # Create the manager
    vector_store = VectorStoreManager()
    
    # Create a test Excel file
    test_data = {
        'Question': ['What is AI?', 'How does ML work?'],
        'Answer': ['AI is artificial intelligence', 'ML uses algorithms to learn from data'],
        'Category': ['Basics', 'Basics'],
        'Source': ['Test Excel', 'Test Excel']
    }
    df = pd.DataFrame(test_data)
    test_excel_path = Path('test_data.xlsx')
    df.to_excel(test_excel_path, index=False)
    
    try:
        # Convert Excel rows to documents
        documents = []
        for _, row in df.iterrows():
            # Combine question and answer for better context
            content = f"Question: {row['Question']}\nAnswer: {row['Answer']}"
            metadata = {
                'source': row['Source'],
                'category': row['Category'],
                'question': row['Question']
            }
            documents.append(Document(page_content=content, metadata=metadata))
        
        # Add to vector store
        vector_store.add_documents(documents)
        
        # Test searching
        results = vector_store.similarity_search("What is artificial intelligence?")
        assert len(results) > 0
        
        # Verify metadata is preserved
        first_result = results[0]
        assert 'source' in first_result.metadata
        assert 'category' in first_result.metadata
        assert 'question' in first_result.metadata
        
        # Test category filtering
        results = vector_store.similarity_search(
            "What is artificial intelligence?",
            filter={"category": "Basics"}
        )
        assert len(results) > 0
        
    finally:
        # Clean up test file
        if test_excel_path.exists():
            test_excel_path.unlink()

def test_excel_import_with_large_file(setup_test_environment):
    """Test importing a larger Excel file"""
    # Ensure we have an API key for testing
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    # Create the manager
    vector_store = VectorStoreManager()
    
    # Create a larger test Excel file
    test_data = {
        'Question': [f'Question {i}' for i in range(100)],
        'Answer': [f'Answer {i}' for i in range(100)],
        'Category': ['Test' for _ in range(100)],
        'Source': ['Large Test Excel' for _ in range(100)]
    }
    df = pd.DataFrame(test_data)
    test_excel_path = Path('test_large_data.xlsx')
    df.to_excel(test_excel_path, index=False)
    
    try:
        # Convert Excel rows to documents
        documents = []
        for _, row in df.iterrows():
            content = f"Question: {row['Question']}\nAnswer: {row['Answer']}"
            metadata = {
                'source': row['Source'],
                'category': row['Category'],
                'question': row['Question']
            }
            documents.append(Document(page_content=content, metadata=metadata))
        
        # Add to vector store
        vector_store.add_documents(documents)
        
        # Test searching
        results = vector_store.similarity_search("Question 50")
        assert len(results) > 0
        
        # Verify we can find the exact question
        found = False
        for result in results:
            if result.metadata['question'] == 'Question 50':
                found = True
                break
        assert found, "Could not find the exact question in search results"
        
    finally:
        # Clean up test file
        if test_excel_path.exists():
            test_excel_path.unlink() 
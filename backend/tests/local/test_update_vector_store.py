import pytest
from unittest.mock import MagicMock, patch
from src.update_vector_store import main

@pytest.fixture
def mock_components():
    """Fixture to provide mocked components."""
    with patch('src.update_vector_store.DataProcessor') as mock_data_processor, \
         patch('src.update_vector_store.VectorStoreManager') as mock_vector_store, \
         patch('src.update_vector_store.DocumentProcessor') as mock_document_processor:
        
        # Set up mock instances
        data_processor_instance = MagicMock()
        vector_store_instance = MagicMock()
        document_processor_instance = MagicMock()
        
        # Configure mock returns
        mock_data_processor.return_value = data_processor_instance
        mock_vector_store.return_value = vector_store_instance
        mock_document_processor.return_value = document_processor_instance
        
        yield {
            'data_processor': mock_data_processor,
            'vector_store': mock_vector_store,
            'document_processor': mock_document_processor
        }

def test_main_success(mock_components):
    """Test successful execution of main function."""
    # Set up test data
    test_documents = [{"content": "Test content", "metadata": {"source": "test.txt"}}]
    processed_documents = [{"content": "Processed content", "metadata": {"source": "test.txt"}}]
    
    # Configure mock returns
    mock_components['data_processor'].return_value.process_all_data.return_value = test_documents
    mock_components['document_processor'].return_value.process_documents.return_value = processed_documents
    
    # Run the function
    main()
    
    # Verify calls
    mock_components['data_processor'].return_value.process_all_data.assert_called_once()
    mock_components['document_processor'].return_value.process_documents.assert_called_once_with(test_documents)
    mock_components['vector_store'].return_value.add_documents.assert_called_once_with(processed_documents)

def test_main_with_no_documents(mock_components):
    """Test main function with no documents to process."""
    # Configure mock to return empty list
    mock_components['data_processor'].return_value.process_all_data.return_value = []
    
    # Run the function
    main()
    
    # Verify calls
    mock_components['data_processor'].return_value.process_all_data.assert_called_once()
    mock_components['document_processor'].return_value.process_documents.assert_not_called()
    mock_components['vector_store'].return_value.add_documents.assert_not_called()

def test_main_with_processing_error(mock_components):
    """Test main function with processing error."""
    # Configure mock to raise exception
    mock_components['data_processor'].return_value.process_all_data.side_effect = Exception("Processing error")
    
    # Run the function and verify exception
    with pytest.raises(Exception) as exc_info:
        main()
    assert str(exc_info.value) == "Processing error"

def test_document_metadata(mock_components):
    """Test document metadata handling."""
    # Set up test data
    test_document = {
        "content": "Test content 1",
        "metadata": {
            "source": "test.xlsx",
            "processed_date": "2024-01-01T00:00:00",
            "document_type": "excel_data"
        }
    }
    
    # Configure mock returns
    mock_components['data_processor'].return_value.process_all_data.return_value = [test_document]
    mock_components['document_processor'].return_value.process_documents.return_value = [test_document]
    
    # Run the function
    main()
    
    # Verify calls
    mock_components['data_processor'].return_value.process_all_data.assert_called_once()
    mock_components['document_processor'].return_value.process_documents.assert_called_once_with([test_document])
    mock_components['vector_store'].return_value.add_documents.assert_called_once_with([test_document]) 
import os
import pytest
import pandas as pd
from pathlib import Path
from src.data_processor import DataProcessor

@pytest.fixture
def sample_excel_file(test_dir):
    """Create a sample Excel file for testing."""
    df = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Test1', 'Test2', 'Test3', 'Test4', 'Test5'],
        'description': ['Desc1', 'Desc2', 'Desc3', 'Desc4', 'Desc5']
    })
    
    file_path = test_dir / "data" / "raw" / "test.xlsx"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(file_path, index=False)
    return file_path

def test_data_processor_initialization(directory_manager):
    """Test data processor initialization."""
    processor = DataProcessor(str(directory_manager.base_dir))
    assert processor.dir_manager.base_dir == directory_manager.base_dir
    assert processor.dir_manager.raw_data_dir.exists()
    assert processor.dir_manager.processed_data_dir.exists()

def test_process_excel_file(directory_manager, sample_excel_file):
    """Test Excel file processing."""
    processor = DataProcessor(str(directory_manager.base_dir))
    documents = processor.process_excel_file(sample_excel_file, limit=3)
    
    assert len(documents) == 3
    assert all(isinstance(doc, dict) for doc in documents)
    assert all('source_file' in doc for doc in documents)
    assert all('processed_date' in doc for doc in documents)
    assert all('document_type' in doc for doc in documents)
    assert all('content' in doc for doc in documents)

def test_process_all_files(directory_manager, sample_excel_file):
    """Test processing all Excel files."""
    processor = DataProcessor(str(directory_manager.base_dir))
    documents = processor.process_all_files(limit=2)
    
    assert len(documents) == 2
    assert all(isinstance(doc, dict) for doc in documents)

def test_save_processed_data(directory_manager, sample_excel_file):
    """Test saving processed data."""
    processor = DataProcessor(str(directory_manager.base_dir))
    documents = processor.process_excel_file(sample_excel_file, limit=2)
    
    output_file = "test_output.json"
    processor.save_processed_data(documents, output_file)
    
    output_path = processor.dir_manager.processed_data_dir / output_file
    assert output_path.exists()
    
    # Verify saved data
    import json
    with open(output_path) as f:
        saved_data = json.load(f)
    assert len(saved_data) == 2
    assert all(isinstance(doc, dict) for doc in saved_data)

def test_process_excel_file_with_invalid_data(directory_manager, test_dir):
    """Test processing Excel file with invalid data."""
    # Create Excel file with invalid data
    df = pd.DataFrame({
        'id': [1, None, 3],
        'name': ['Test1', None, 'Test3'],
        'description': [None, 'Desc2', None]
    })
    
    file_path = test_dir / "data" / "raw" / "invalid.xlsx"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(file_path, index=False)
    
    processor = DataProcessor(str(directory_manager.base_dir))
    documents = processor.process_excel_file(file_path, limit=3)
    
    assert len(documents) == 3
    assert all('content' in doc for doc in documents)
    # Verify that None values are not included in content
    assert all('None' not in doc['content'] for doc in documents)

def test_process_nonexistent_file(directory_manager):
    """Test processing nonexistent file."""
    processor = DataProcessor(str(directory_manager.base_dir))
    with pytest.raises(Exception):
        processor.process_excel_file("nonexistent.xlsx") 
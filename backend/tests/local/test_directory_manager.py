import os
import pytest
from pathlib import Path
from src.utils.directory_manager import DirectoryManager
from src.config import Settings

def test_directory_manager_initialization():
    """Test directory manager initialization."""
    manager = DirectoryManager()
    assert isinstance(manager, DirectoryManager)
    assert hasattr(manager, 'base_dir')
    assert hasattr(manager, 'data_dir')
    assert hasattr(manager, 'vector_store_dir')

def test_directory_manager_azure_initialization(azure_settings):
    """Test directory manager initialization in Azure environment."""
    manager = DirectoryManager()
    assert isinstance(manager, DirectoryManager)
    assert hasattr(manager, 'base_dir')
    assert hasattr(manager, 'data_dir')
    assert hasattr(manager, 'vector_store_dir')

def test_create_directories():
    """Test directory creation."""
    manager = DirectoryManager()
    test_dir = manager.create_directories("test_dir")
    assert test_dir.exists()
    test_dir.rmdir()  # Cleanup

def test_get_path():
    """Test path generation."""
    manager = DirectoryManager()
    path = manager.get_path("test", "file.txt")
    assert isinstance(path, (str, Path))
    # Handle both Windows and Unix-style paths
    path_str = str(path).replace('\\', '/')
    assert path_str.endswith("test/file.txt")

def test_directory_properties():
    """Test directory properties."""
    manager = DirectoryManager()
    assert hasattr(manager, 'base_dir')
    assert hasattr(manager, 'data_dir')
    assert hasattr(manager, 'processed_dir')
    assert hasattr(manager, 'vector_store_dir')

def test_directory_properties(directory_manager):
    """Test directory property accessors."""
    assert directory_manager.data_dir == directory_manager.base_dir / "data"
    assert directory_manager.raw_data_dir == directory_manager.base_dir / "data" / "raw"
    assert directory_manager.processed_data_dir == directory_manager.base_dir / "data" / "processed"
    assert directory_manager.uploads_dir == directory_manager.base_dir / "uploads"
    assert directory_manager.logs_dir == directory_manager.base_dir / "logs"

def test_azure_storage_path(directory_manager, azure_settings):
    """Test Azure storage path generation."""
    # Test with Azure environment
    path = directory_manager.get_azure_storage_path("test", "file.txt")
    assert path is not None
    assert path.startswith("https://")
    assert azure_settings.AZURE_STORAGE_ACCOUNT in path
    assert "test/file.txt" in path 
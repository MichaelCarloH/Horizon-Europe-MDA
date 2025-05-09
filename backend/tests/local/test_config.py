import os
import pytest
from pathlib import Path

def test_settings_initialization(settings):
    """Test basic settings initialization."""
    assert not settings.AZURE_ENVIRONMENT
    assert settings.API_VERSION == "1.0.0"
    assert settings.API_PREFIX == "/api/v1"
    assert settings.CHUNK_SIZE == 1000
    assert settings.CHUNK_OVERLAP == 200

def test_azure_settings_initialization(azure_settings):
    """Test Azure settings initialization."""
    assert azure_settings.AZURE_ENVIRONMENT
    assert azure_settings.AZURE_STORAGE_ACCOUNT == "testaccount"
    assert azure_settings.AZURE_STORAGE_CONTAINER == "testcontainer"
    assert azure_settings.APPLICATIONINSIGHTS_CONNECTION_STRING == "test-connection-string"

def test_database_url(settings, azure_settings):
    """Test database URL generation."""
    # Test local database URL
    assert settings.get_database_url() == "sqlite:///./data/chroma.db"
    
    # Test Azure database URL
    os.environ["SITE_ROOT"] = "/test/site/root"
    assert azure_settings.get_database_url() == "sqlite:////test/site/root/data/chroma.db"

def test_azure_storage_path(settings, azure_settings):
    """Test Azure storage path generation."""
    # Test without Azure environment
    assert settings.get_azure_storage_path("test.txt") is None
    
    # Test with Azure environment
    path = azure_settings.get_azure_storage_path("test.txt")
    assert path == "https://testaccount.blob.core.windows.net/testcontainer/test.txt"

def test_cors_settings(settings):
    """Test CORS settings."""
    assert settings.CORS_ORIGINS == ["*"]
    assert settings.CORS_METHODS == ["*"]
    assert settings.CORS_HEADERS == ["*"]

def test_vector_store_settings(settings):
    """Test vector store settings."""
    assert isinstance(settings.VECTOR_STORE_DIR, Path)
    assert settings.VECTOR_STORE_DIR == Path("data/vector_store")
    assert settings.CHUNK_SIZE == 1000
    assert settings.CHUNK_OVERLAP == 200

def test_query_settings(settings):
    """Test query settings."""
    assert settings.MAX_RETRIEVED_DOCUMENTS == 5
    assert settings.RELEVANCE_THRESHOLD == 0.7
    assert settings.TEMPERATURE == 0.0

def test_cache_settings(settings):
    """Test cache settings."""
    assert settings.ENABLE_CACHE is True
    assert settings.CACHE_TTL == 3600 
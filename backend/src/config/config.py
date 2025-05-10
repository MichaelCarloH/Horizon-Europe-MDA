from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    AZURE_ENVIRONMENT: bool = os.getenv("AZURE_ENVIRONMENT", "false").lower() == "true"
    
    # Azure-specific settings
    AZURE_STORAGE_ACCOUNT: Optional[str] = os.getenv("AZURE_STORAGE_ACCOUNT")
    AZURE_STORAGE_CONTAINER: Optional[str] = os.getenv("AZURE_STORAGE_CONTAINER")
    APPLICATIONINSIGHTS_CONNECTION_STRING: Optional[str] = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    MAX_RESULTS: int = 5
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 1000
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/chroma.db")
    
    # Path settings
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "chroma")
    DATA_PATH: str = os.getenv("DATA_PATH", "data/pdf")
    
    # Vector store settings
    VECTOR_STORE_DIR: Path = Path("data/vector_store")
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_CHUNKS_PER_DOCUMENT: int = 100
    
    # API settings
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # Query Settings
    MAX_RETRIEVED_DOCUMENTS: int = 5  # Increased from 3
    RELEVANCE_THRESHOLD: float = 0.7
    TEMPERATURE: float = 0.0
    
    # Cache Settings
    ENABLE_CACHE: bool = False
    CACHE_TTL: int = 3600  # 1 hour in seconds
    
    # New settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://localhost:3000",
        "https://localhost:8000",
    ]
    
    # Added from the code block
    COLLECTION_NAME: str = "horizon_europe"
    
    # Upload settings
    UPLOAD_DIR: str = "uploads"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"  # Allow extra fields from environment
    }
        
    def get_azure_storage_path(self, blob: str) -> Optional[str]:
        """Get Azure Storage path if configured."""
        if not self.AZURE_ENVIRONMENT or not self.AZURE_STORAGE_ACCOUNT or not self.AZURE_STORAGE_CONTAINER:
            return None
            
        return f"https://{self.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/{self.AZURE_STORAGE_CONTAINER}/{blob}"
        
    def get_database_url(self) -> str:
        """Get database URL with Azure-specific handling."""
        if self.AZURE_ENVIRONMENT:
            # In Azure, use the site root directory
            site_root = os.getenv("SITE_ROOT", "/home/site/wwwroot")
            return f"sqlite:///{site_root}/data/chroma.db"
        return self.DATABASE_URL

# Create global settings instance
settings = Settings() 

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True) 
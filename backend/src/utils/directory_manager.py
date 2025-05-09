import os
from pathlib import Path
from typing import List, Optional

class DirectoryManager:
    def __init__(self, base_dir: str = None):
        """
        Initialize directory manager.
        
        Args:
            base_dir: Base directory path. If None, uses the backend directory.
        """
        self.is_azure = os.getenv("AZURE_ENVIRONMENT", "false").lower() == "true"
        
        if base_dir is None:
            if self.is_azure:
                # In Azure, use the site root directory
                self.base_dir = Path(os.getenv("SITE_ROOT", "/home/site/wwwroot"))
            else:
                self.base_dir = Path(__file__).parent.parent.parent
        else:
            self.base_dir = Path(base_dir)
            
        # Create base directories
        self.create_directories([
            "data",
            "data/raw",
            "data/processed",
            "uploads",
            "logs"
        ])
            
    def create_directories(self, directories: List[str]) -> Path:
        """
        Create multiple directories if they don't exist.
        
        Args:
            directories: List of directory paths relative to base_dir
            
        Returns:
            Path object for the last created directory
        """
        last_path = None
        for directory in directories:
            path = self.base_dir / directory
            path.mkdir(parents=True, exist_ok=True)
            last_path = path
        return last_path
            
    def get_path(self, *paths: str) -> Path:
        """
        Get absolute path for a file or directory.
        
        Args:
            *paths: Path components relative to base_dir
            
        Returns:
            Absolute Path object
        """
        # Convert Windows backslashes to forward slashes
        path = self.base_dir.joinpath(*paths)
        return Path(str(path).replace('\\', '/'))
        
    @property
    def data_dir(self) -> Path:
        """Get the data directory path."""
        return self.base_dir / "data"
        
    @property
    def raw_data_dir(self) -> Path:
        """Get the raw data directory path."""
        return self.data_dir / "raw"
        
    @property
    def processed_data_dir(self) -> Path:
        """Get the processed data directory path."""
        return self.data_dir / "processed"
        
    @property
    def uploads_dir(self) -> Path:
        """Get the uploads directory path."""
        return self.base_dir / "uploads"
        
    @property
    def logs_dir(self) -> Path:
        """Get the logs directory path."""
        return self.base_dir / "logs"
        
    @property
    def is_azure_environment(self) -> bool:
        """Check if running in Azure environment."""
        return self.is_azure
        
    def get_azure_storage_path(self, container: str, blob: str) -> Optional[str]:
        """
        Get Azure Storage path if in Azure environment.
        
        Args:
            container: Storage container name
            blob: Blob name
            
        Returns:
            Azure Storage path or None if not in Azure
        """
        if not self.is_azure:
            return None
            
        storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
        if not storage_account:
            return None
            
        return f"https://{storage_account}.blob.core.windows.net/{container}/{blob}" 

    @property
    def vector_store_dir(self) -> Path:
        """Get the vector store directory path."""
        return self.data_dir / "vector_store" 
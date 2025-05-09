import os
import sqlite3
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def initialize_database(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Initialize the SQLite database with proper configuration for both local and Azure environments.
    
    Args:
        db_path: Optional path to the database file. If not provided, uses default location.
        
    Returns:
        sqlite3.Connection: The initialized database connection
    """
    try:
        # Check if we're in Azure environment
        if os.getenv("AZURE_ENVIRONMENT"):
            try:
                import pysqlite3
                sqlite3 = pysqlite3
                logger.info("Using pysqlite3 for Azure environment")
            except ImportError:
                logger.warning("pysqlite3 not available, falling back to standard sqlite3")
        
        # Set up database path
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "..", "data", "chroma.db")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize connection with proper configuration
        conn = sqlite3.connect(
            db_path,
            check_same_thread=False,  # Allow multiple threads to access the database
            timeout=30.0  # Increase timeout for Azure environment
        )
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Configure journal mode for better performance
        conn.execute("PRAGMA journal_mode = WAL")
        
        # Set synchronous mode for better performance while maintaining durability
        conn.execute("PRAGMA synchronous = NORMAL")
        
        # Set cache size for better performance
        conn.execute("PRAGMA cache_size = -2000")  # Use 2MB of cache
        
        logger.info(f"Database initialized successfully at {db_path}")
        return conn
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

def get_db_connection() -> sqlite3.Connection:
    """
    Get a database connection, creating one if it doesn't exist.
    
    Returns:
        sqlite3.Connection: The database connection
    """
    return initialize_database() 
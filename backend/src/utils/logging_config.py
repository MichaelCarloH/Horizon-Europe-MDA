import logging
import os
from pathlib import Path
from typing import Optional

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: The logging level to use (default: INFO)
        log_file: Optional log file path. If None, uses default location.
        
    Returns:
        Logger instance
    """
    # Get environment
    is_azure = os.getenv("AZURE_ENVIRONMENT", "false").lower() == "true"
    
    # Create logs directory if it doesn't exist
    if log_file is None:
        if is_azure:
            # In Azure, use the site root logs directory
            log_dir = Path(os.getenv("SITE_ROOT", "/home/site/wwwroot")) / "logs"
        else:
            log_dir = Path(__file__).parent.parent.parent / "logs"
        log_file = log_dir / "app.log"
    else:
        log_dir = Path(log_file).parent
        
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Add Azure Application Insights handler if available
    if is_azure:
        try:
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
            if connection_string:
                logging.getLogger().addHandler(
                    AzureLogHandler(connection_string=connection_string)
                )
        except ImportError:
            pass
    
    return logging.getLogger(__name__) 
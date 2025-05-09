import pytest
import os
import logging
from src.utils.logging_config import setup_logging
from src.config import Settings
from pathlib import Path

def test_setup_logging():
    """Test basic logging setup."""
    logger = setup_logging()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "src.utils.logging_config"

def test_setup_logging_with_custom_file():
    """Test logging setup with custom file."""
    test_dir = Path("test_logs")
    test_dir.mkdir(exist_ok=True)
    log_file = test_dir / "test.log"
    
    logger = setup_logging(log_file=str(log_file))
    assert isinstance(logger, logging.Logger)
    assert log_file.exists()
    
    # Cleanup
    log_file.unlink()
    test_dir.rmdir()

def test_setup_logging_azure(azure_settings, test_dir):
    """Test logging setup in Azure environment."""
    logger = setup_logging()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "src.utils.logging_config"

def test_logging_levels():
    """Test different logging levels."""
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logger = setup_logging(log_level=level)
        assert isinstance(logger, logging.Logger)
        assert logger.name == "src.utils.logging_config"

def test_logging_output(caplog):
    """Test logging output."""
    logger = setup_logging()
    test_message = "Test log message"
    logger.info(test_message)
    assert test_message in caplog.text 
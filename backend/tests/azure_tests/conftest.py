import pytest
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture(scope="session")
def azure_settings():
    """Create Azure test settings."""
    os.environ["AZURE_ENVIRONMENT"] = "true"
    os.environ["AZURE_STORAGE_ACCOUNT"] = "testaccount"
    os.environ["AZURE_STORAGE_CONTAINER"] = "testcontainer"
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "test-connection-string"
    return Settings()

@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for the Azure API."""
    return "https://mda-horizon-backend-2025.azurewebsites.net" 
# Testing Guide

This directory contains tests for both local development and Azure deployment environments.

## Directory Structure

```
tests/
├── common/           # Shared test utilities and fixtures
│   ├── conftest.py  # Common fixtures
│   └── test_base.py # Base test classes
├── local/           # Tests for local development
│   ├── test_api.py
│   ├── test_local.py
│   ├── test_main.py
│   ├── test_config.py
│   ├── test_data_processor.py
│   ├── test_directory_manager.py
│   ├── test_logging_config.py
│   └── test_update_vector_store.py
├── azure/           # Tests for Azure deployment
│   ├── test_api.py
│   └── test_azure_endpoints.py
├── README.md
└── __init__.py
```

## Prerequisites

1. Python 3.8+ installed
2. Virtual environment activated
3. Required packages installed:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## Environment Setup

1. Create a `.env` file in the backend directory:
   ```
   OPENAI_API_KEY=your_api_key
   AZURE_ENVIRONMENT=false  # Set to true for Azure tests
   CHROMA_PATH=test_chroma
   ```

2. Ensure you're in the backend directory:
   ```bash
   cd backend
   ```

## Running Tests

### Local Development Tests

1. Start the local server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

2. In a new terminal, run the local tests:
   ```bash
   pytest tests/local -v
   ```

These tests will:
- Test API endpoints locally
- Verify component functionality
- Check database operations
- Validate configuration
- Test logging setup

### Azure Deployment Tests

1. Ensure your Azure deployment is running
2. Run Azure tests:
   ```bash
   pytest tests/azure -v
   ```

These tests will:
- Test deployed endpoints
- Verify Azure integration
- Check production environment

### Running All Tests

```bash
pytest -v
```

## Test Categories

1. API Tests
   - Health endpoint
   - Query endpoint
   - Error handling
   - Input validation

2. Component Tests
   - Data processor
   - Directory manager
   - Logging configuration
   - Vector store updates

3. Integration Tests
   - Local server integration
   - Azure deployment integration
   - Database operations

## Troubleshooting

1. If tests fail to start:
   - Check if server is running
   - Verify environment variables
   - Check port availability

2. If database tests fail:
   - Ensure ChromaDB is installed
   - Check CHROMA_PATH setting
   - Verify database permissions

3. If Azure tests fail:
   - Check Azure deployment status
   - Verify Azure credentials
   - Check network connectivity

## Writing New Tests

1. Common Test Cases:
   - Add to `common/test_base.py`
   - Use inheritance to share across environments

2. Environment-Specific Tests:
   - Inherit from base test classes
   - Override methods as needed
   - Add environment-specific test cases

3. Fixtures:
   - Common fixtures in `common/conftest.py`
   - Environment-specific fixtures in respective `conftest.py`

4. Best Practices:
   - Follow existing patterns
   - Maintain separation of concerns
   - Keep tests focused and atomic
   - Use descriptive names and docstrings 
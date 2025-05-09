# Testing Guide

This directory contains tests for both local development and Azure deployment environments.

## Directory Structure

```
tests/
├── common/           # Shared test utilities and fixtures
├── local_tests/     # Tests for local development
├── azure_tests/     # Tests for Azure deployment
└── README.md        # This file
```

## Running Tests

### Local Development Tests

To run local development tests:

```bash
# From the backend directory
pytest tests/local_tests -v
```

These tests will:
1. Start a local FastAPI server
2. Run tests against the local endpoints
3. Automatically clean up after completion

### Azure Deployment Tests

To run Azure deployment tests:

```bash
# From the backend directory
pytest tests/azure_tests -v
```

These tests will:
1. Connect to the Azure deployment
2. Run tests against the deployed endpoints
3. Verify Azure-specific functionality

### Running All Tests

To run all tests (both local and Azure):

```bash
# From the backend directory
pytest -v
```

## Test Environment Setup

1. Create a `.env` file in the backend directory with required environment variables:
   ```
   OPENAI_API_KEY=your_api_key
   AZURE_ENVIRONMENT=false  # Set to true for Azure tests
   CHROMA_PATH=test_chroma
   ```

2. Install test dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Test Categories

1. API Tests
   - Health endpoint
   - Query endpoint
   - Error handling
   - Input validation

2. Database Tests
   - ChromaDB integration
   - Vector store operations

3. Environment Tests
   - Configuration loading
   - Environment variables
   - Directory management

## Writing New Tests

1. Place shared fixtures in `tests/common/conftest.py`
2. Add environment-specific fixtures to respective `conftest.py` files
3. Follow the existing test structure and naming conventions
4. Include appropriate assertions and error cases 
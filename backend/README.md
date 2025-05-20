# Backend Documentation

## Directory Structure

```
backend/
├── src/
│   ├── config/           # Configuration settings
│   │   ├── __init__.py
│   │   └── config.py     # Environment and app settings
│   │
│   ├── database/         # Database operations
│   │   ├── __init__.py
│   │   ├── database.py   # Database connection and operations
│   │   └── view_database.py  # Database viewing utilities
│   │
│   ├── processing/       # Document and query processing
│   │   ├── __init__.py
│   │   ├── document_processor.py  # Document processing logic
│   │   └── query_processor.py     # Query handling and response generation
│   │
│   ├── utils/           # Utility functions
│   │   ├── __init__.py
│   │   ├── directory_manager.py   # Directory management utilities
│   │   ├── excel_importer.py      # Excel file import utilities
│   │   └── logging_config.py      # Logging configuration
│   │
│   └── vector_store/    # Vector store operations
│       ├── __init__.py
│       ├── vector_store.py        # Vector store management
│       ├── compare_embeddings.py  # Embedding comparison utilities
│       └── update_vector_store.py # Vector store update utilities
│
├── tests/               # Test files
│   ├── __init__.py
│   ├── conftest.py      # Test configuration and fixtures
│   └── local/           # Local test files
│
├── main.py             # FastAPI application entry point
└── requirements.txt    # Python dependencies
```

## Key Components

### Configuration (`src/config/`)
- Environment variables and application settings
- API keys and connection strings
- CORS and security settings
- Azure Storage configuration

### Database (`src/database/`)
- SQLite database operations
- Document storage and retrieval
- Database viewing utilities
- Azure Storage integration

### Processing (`src/processing/`)
- Document processing and chunking
- Query handling and response generation
- Conversation management

### Vector Store (`src/vector_store/`)
- ChromaDB integration
- Document embedding and storage
- Similarity search operations
- Azure Storage support

### Utilities (`src/utils/`)
- Directory management
- Excel file import
- Logging configuration

## Setup and Installation

1. Create a virtual environment with Python 3.11:
```bash
python3.11 -m venv .venv-py311
# On Windows:
.venv-py311\Scripts\activate
# On Unix/MacOS:
source .venv-py311/bin/activate
```

2. Install dependencies:
```bash
# For local development:
pip install -r requirements.txt

# For Azure deployment:
pip install -r requirements-azure.txt
```

3. Create a `.env` file:
```env
# Development environment
OPENAI_API_KEY=your_api_key_here
CHROMA_PATH=./data/chroma
COLLECTION_NAME=documents
UPLOAD_DIR=./data/uploads

# Production environment (Azure)
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
CHROMA_PATH=azure://your_storage_account/chroma-db
```

4. Start the server:
```bash
# Development mode with auto-reload:
python main.py

# Or using uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# For Azure deployment:
python run_app.py
```

## Database Setup

### Local Development
The Chroma database is stored locally in the `./data/chroma` directory.

### Production (Azure)
1. Create an Azure Storage Account
2. Create a container named `chroma-db`
3. Set the environment variables:
   - `AZURE_STORAGE_CONNECTION_STRING`: Your Azure Storage connection string
   - `CHROMA_PATH`: Set to `azure://your_storage_account/chroma-db`
4. Upload the database files to the container

## API Documentation

The API documentation is available at `http://localhost:8000/docs` when the server is running.

### Main Endpoints

1. Health Check:
```bash
GET /health
```

2. Query Processing:
```bash
POST /query
{
    "text": "Your question here",
    "conversation_id": "optional_conversation_id"
}
```

3. Document Management:
```bash
# Upload document
POST /documents/upload
Content-Type: multipart/form-data
file: <file>

# Delete documents
DELETE /documents
{
    "document_ids": ["id1", "id2"]
}
```

4. Vector Store Management:
```bash
# Get statistics
GET /vector-store/stats

# Export metadata
GET /vector-store/export-metadata
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
- Use Black for code formatting
- Follow PEP 8 guidelines
- Add type hints to function parameters

### Logging
- Logs are configured in `src/utils/logging_config.py`
- Log files are stored in `logs/` directory
- Different log levels for development and production

## Troubleshooting

1. Import Errors:
   - Check Python path setup in `main.py`
   - Verify virtual environment is activated
   - Ensure all dependencies are installed

2. Database Issues:
   - Check database file permissions
   - Verify database connection string
   - Check for database migrations
   - Verify Azure Storage connection and permissions

3. Vector Store Issues:
   - Verify ChromaDB installation
   - Check vector store path permissions
   - Ensure OpenAI API key is valid
   - Check Azure Storage container access

4. Document Processing:
   - Check upload directory permissions
   - Verify file format support
   - Check document size limits

5. Azure Storage Issues:
   - Verify connection string is correct
   - Check container exists and is accessible
   - Ensure database files are properly uploaded
   - Check network connectivity to Azure 
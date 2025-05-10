# EuroRAG Project

A Retrieval-Augmented Generation (RAG) system for document-based question answering, built with FastAPI and React.

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── src/                # Source code
│   │   ├── config/        # Configuration settings
│   │   ├── database/      # Database operations
│   │   ├── processing/    # Document and query processing
│   │   ├── utils/         # Utility functions
│   │   └── vector_store/  # Vector store operations
│   ├── tests/             # Test files
│   └── main.py           # FastAPI application entry point
│
└── frontend/              # React frontend
    ├── src/              # Source code
    ├── public/           # Static files
    └── package.json      # Dependencies
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- OpenAI API key

## Setup

### Backend Setup

1. Create and activate a virtual environment with Python 3.11:
```bash
cd backend
python3.11 -m venv .venv-py311
# On Windows:
.venv-py311\Scripts\activate
# On Unix/MacOS:
source .venv-py311/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:
```env
OPENAI_API_KEY=your_api_key_here
CHROMA_PATH=./data/chroma
COLLECTION_NAME=documents
UPLOAD_DIR=./data/uploads
```

4. Start the backend server:
```bash
# Development mode with auto-reload:
python main.py

# Or using uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Health Check
```bash
GET /health
```

### Query Processing
```bash
POST /query
{
    "text": "Your question here",
    "conversation_id": "optional_conversation_id"
}
```

### Document Management
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

### Vector Store Management
```bash
# Get vector store statistics
GET /vector-store/stats

# Export metadata
GET /vector-store/export-metadata
```

### Conversation Management
```bash
# Clear conversation
POST /conversations/{conversation_id}/clear

# Get conversation history
GET /conversations/{conversation_id}/history
```

## Making Queries

1. Through the API:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the main topic of the document?", "conversation_id": null}'
```

2. Through the Frontend:
- Open `http://localhost:5173` in your browser
- Enter your question in the chat interface
- The system will process your query and return a response

## Development

### Running Tests
```bash
cd backend
python -m pytest tests/
```

### Code Style
The project uses:
- Black for Python code formatting
- ESLint for JavaScript/TypeScript formatting

## Troubleshooting

1. If you get import errors:
   - Make sure you're in the correct directory
   - Check that the virtual environment is activated
   - Verify that all dependencies are installed

2. If the frontend can't connect to the backend:
   - Ensure the backend server is running
   - Check that CORS is properly configured
   - Verify the API URL in the frontend configuration

3. If document processing fails:
   - Check the upload directory permissions
   - Verify the OpenAI API key is valid
   - Check the logs for detailed error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.


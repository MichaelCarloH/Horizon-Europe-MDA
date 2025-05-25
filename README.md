# Horizon Intelligence

A Retrieval-Augmented Generation (RAG) system for document-based question answering, built with FastAPI and React.

[![Documentation](https://img.shields.io/badge/Documentation-Wiki-blue)](https://github.com/MichaelCarloH/Horizon-Europe-MDA/wiki)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Quick Links

- [📚 Project Overview](https://github.com/MichaelCarloH/Horizon-Europe-MDA/wiki/Project-Overview)
- [🚀 Getting Started](https://github.com/MichaelCarloH/Horizon-Europe-MDA/wiki/Getting-Started)
- [🔧 Development Guide](https://github.com/MichaelCarloH/Horizon-Europe-MDA/wiki/Development-Guide)
- [📋 API Documentation](https://github.com/MichaelCarloH/Horizon-Europe-MDA/wiki/API-Documentation)
- [🔐 System Architecture](https://github.com/MichaelCarloH/Horizon-Europe-MDA/wiki/System-Architecture)

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

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/MichaelCarloH/Horizon-Europe-MDA.git
cd Horizon-Europe-MDA
```

2. Set up the backend:
```bash
cd backend
python3.11 -m venv .venv-py311
source .venv-py311/bin/activate  # or `.venv-py311\Scripts\activate` on Windows
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Start the development servers:
```bash
# Terminal 1 (Backend)
cd backend
python main.py

# Terminal 2 (Frontend)
cd frontend
npm run dev
```

## Documentation

All documentation is available in our [GitHub Wiki](https://github.com/MichaelCarloH/Horizon-Europe-MDA/wiki), including:

- Project Overview
- Getting Started Guide
- Development Guide
- API Documentation
- System Architecture
- Troubleshooting Guide

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/MichaelCarloH/Horizon-Europe-MDA/wiki/Contributing) in the Wiki.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please:
1. Check our [Troubleshooting Guide](https://github.com/MichaelCarloH/Horizon-Europe-MDA/wiki/Troubleshooting)
2. Open an issue on GitHub
3. Contact the maintainers

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [ChromaDB](https://www.trychroma.com/)
- [OpenAI](https://openai.com/)

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
- Open `http://localhost:8000` in your browser
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


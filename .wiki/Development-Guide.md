# Development Guide

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- Docker (optional)
- VS Code (recommended)

### Backend Setup

1. **Create Virtual Environment**
   ```bash
   cd backend
   python3.11 -m venv .venv-py311
   # Windows
   .venv-py311\Scripts\activate
   # Unix/MacOS
   source .venv-py311/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Environment Variables**
   Create `.env` file:
   ```env
   OPENAI_API_KEY=your_api_key
   CHROMA_PATH=./data/chroma
   COLLECTION_NAME=documents
   UPLOAD_DIR=./data/uploads
   DEBUG=True
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment Configuration**
   Create `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_WS_URL=ws://localhost:8000
   ```

## Development Workflow

### Code Style

1. **Python**
   - Follow PEP 8
   - Use Black for formatting
   - Use isort for imports
   - Use mypy for type checking

2. **TypeScript/JavaScript**
   - Follow ESLint rules
   - Use Prettier for formatting
   - Use TypeScript strict mode
   - Follow React best practices

### Git Workflow

1. **Branching Strategy**
   - `main`: Production code
   - `develop`: Development branch
   - `feature/*`: New features
   - `fix/*`: Bug fixes
   - `release/*`: Release preparation

2. **Commit Guidelines**
   - Use conventional commits
   - Write clear commit messages
   - Reference issues in commits
   - Keep commits focused

### Testing

1. **Backend Tests**
   ```bash
   cd backend
   pytest
   pytest --cov=src  # With coverage
   ```

2. **Frontend Tests**
   ```bash
   cd frontend
   npm test
   npm run test:coverage
   ```

3. **End-to-End Tests**
   ```bash
   npm run test:e2e
   ```

## Code Organization

### Backend Structure

```
backend/
├── src/
│   ├── config/        # Configuration
│   ├── database/      # Database models
│   ├── processing/    # Document processing
│   ├── utils/         # Utilities
│   └── vector_store/  # Vector operations
├── tests/            # Test files
└── main.py          # Application entry
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/   # React components
│   ├── hooks/       # Custom hooks
│   ├── pages/       # Page components
│   ├── services/    # API services
│   └── utils/       # Utilities
└── public/          # Static files
```

## Debugging

### Backend Debugging

1. **Logging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.debug("Debug message")
   ```

2. **Debug Mode**
   ```bash
   python main.py --debug
   ```

### Frontend Debugging

1. **React DevTools**
   - Install browser extension
   - Use component inspector
   - Monitor state changes

2. **Network Debugging**
   - Use browser dev tools
   - Monitor API calls
   - Check WebSocket connections

## Performance Optimization

### Backend

1. **Caching**
   - Use Redis for caching
   - Implement response caching
   - Cache embeddings

2. **Database**
   - Optimize queries
   - Use indexes
   - Monitor performance

### Frontend

1. **Code Splitting**
   - Use dynamic imports
   - Implement lazy loading
   - Optimize bundle size

2. **Performance Monitoring**
   - Use React Profiler
   - Monitor render times
   - Track API performance

## Deployment

### Local Deployment

1. **Docker**
   ```bash
   docker-compose up
   ```

2. **Manual**
   ```bash
   # Backend
   cd backend
   python main.py

   # Frontend
   cd frontend
   npm run dev
   ```

### Production Deployment

1. **Backend**
   - Use Gunicorn
   - Configure Nginx
   - Set up SSL

2. **Frontend**
   - Build static files
   - Deploy to CDN
   - Configure caching

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Check Python path
   - Verify virtual environment
   - Check import statements

2. **API Issues**
   - Check CORS settings
   - Verify endpoints
   - Check authentication

3. **Database Issues**
   - Check connections
   - Verify migrations
   - Check permissions

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [ChromaDB Documentation](https://www.trychroma.com/) 
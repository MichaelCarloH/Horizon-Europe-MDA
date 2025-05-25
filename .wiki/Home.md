# Horizon Europe MDA Wiki

Welcome to the Horizon Europe MDA (Mission-Driven Analytics) project documentation. This Wiki serves as the central knowledge base for the project.

## Quick Links

- [🚀 Getting Started](Getting-Started)
- [📊 Project Overview](Project-Overview)
- [🔧 Development Guide](Development-Guide)
- [📋 API Documentation](API-Documentation)
- [🔐 Security](Security)

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
├── frontend/              # React frontend
│   ├── src/              # Source code
│   ├── public/           # Static files
│   └── package.json      # Dependencies
│
├── data/                 # Data storage
│   ├── raw/             # Raw data files
│   ├── processed/       # Processed data
│   └── models/          # Trained models
│
└── notebooks/           # Jupyter notebooks
    ├── analysis/        # Data analysis notebooks
    └── experiments/     # Experimental notebooks
```

## Key Features

- **Document Processing**: Advanced document ingestion and processing pipeline
- **Vector Search**: Efficient semantic search using ChromaDB
- **RAG System**: Retrieval-Augmented Generation for accurate responses
- **Interactive Dashboard**: Real-time data visualization
- **API Integration**: RESTful API for easy integration

## Technology Stack

- **Backend**: FastAPI, Python 3.11
- **Frontend**: React, TypeScript, Next.js
- **Database**: ChromaDB
- **AI/ML**: OpenAI API
- **Deployment**: Docker, GitHub Actions

## Contributing

We welcome contributions! Please see our [Contributing Guide](Contributing) for details.

## Support

If you encounter any issues or have questions:
1. Check our [Troubleshooting Guide](Troubleshooting)
2. Open an issue on GitHub
3. Contact the maintainers

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/MichaelCarloH/Horizon-Europe-MDA/blob/main/LICENSE) file for details. 
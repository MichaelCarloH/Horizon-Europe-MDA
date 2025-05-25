# Getting Started

This guide will help you get up and running with the Horizon Europe MDA project.

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- OpenAI API key
- Git

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MichaelCarloH/Horizon-Europe-MDA.git
   cd Horizon-Europe-MDA
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3.11 -m venv .venv-py311
   # On Windows:
   .venv-py311\Scripts\activate
   # On Unix/MacOS:
   source .venv-py311/bin/activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   Create a `.env` file in the backend directory:
   ```env
   OPENAI_API_KEY=your_api_key_here
   CHROMA_PATH=./data/chroma
   COLLECTION_NAME=documents
   UPLOAD_DIR=./data/uploads
   ```

## Running the Application

1. **Start the Backend**
   ```bash
   cd backend
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Frontend**
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

## First Steps

1. **Upload Documents**
   - Use the web interface to upload documents
   - Or use the API endpoint: `POST /documents/upload`

2. **Make Queries**
   - Use the chat interface in the web application
   - Or use the API endpoint: `POST /query`

3. **Explore the Dashboard**
   - View document statistics
   - Monitor system performance
   - Access analytics

## Next Steps

- Read the [Project Overview](Project-Overview) to understand the system architecture
- Check the [Development Guide](Development-Guide) for contribution guidelines
- Review the [API Documentation](API-Documentation) for integration details

## Troubleshooting

If you encounter any issues:
1. Check the [Troubleshooting Guide](Troubleshooting)
2. Verify your environment setup
3. Check the logs in the backend console
4. Open an issue on GitHub if needed 
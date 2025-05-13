#!/bin/bash

# Initialize logging
echo "Starting application setup..."

# Create necessary directories
mkdir -p data/raw data/processed data/pdf logs

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)
export AZURE_ENVIRONMENT=${AZURE_ENVIRONMENT:-"false"}

# Create and activate virtual environment
echo "Creating virtual environment .venv-py311 with Python 3.11..."
python3.11 -m venv .venv-py311
source .venv-py311/bin/activate

# Verify Python version
python --version

# Install dependencies
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Azure-specific requirements if in Azure environment
if [ "$AZURE_ENVIRONMENT" = "true" ]; then
    echo "Installing Azure-specific requirements..."
    pip install -r requirements-azure.txt
    echo "Installing gunicorn and uvicorn..."
    pip install gunicorn uvicorn
    
    # Configure pysqlite3 to replace sqlite3
    echo "Configuring pysqlite3..."
    
    # Create a wrapper script that configures SQLite before importing the app
    cat > run_app.py << 'EOL'
import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3

# Now import and run the app
from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOL
    
    # Start the application using the wrapper script with optimized settings
    echo "Starting application in Azure environment..."
    gunicorn -w 1 \
             --worker-class uvicorn.workers.UvicornWorker \
             --timeout 300 \
             --worker-connections 1000 \
             --keep-alive 5 \
             --worker-tmp-dir /dev/shm \
             -b 0.0.0.0:8000 run_app:app
else
    echo "Starting application in local environment..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi 
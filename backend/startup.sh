#!/bin/bash

# Initialize logging
echo "Starting application setup..."

# Create necessary directories
mkdir -p data/raw data/processed data/pdf logs

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)
export AZURE_ENVIRONMENT=${AZURE_ENVIRONMENT:-"false"}

# Create and activate virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
    source .venv/bin/activate
    
    # Install base requirements
    echo "Installing base requirements..."
    pip install -r requirements.txt
    
    # Install Azure-specific requirements if in Azure environment
    if [ "$AZURE_ENVIRONMENT" = "true" ]; then
        echo "Installing Azure-specific requirements..."
        pip install -r requirements-azure.txt
    fi
else
    source .venv/bin/activate
fi

# Start the application
if [ "$AZURE_ENVIRONMENT" = "true" ]; then
    echo "Starting application in Azure environment..."
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
else
    echo "Starting application in local environment..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi 
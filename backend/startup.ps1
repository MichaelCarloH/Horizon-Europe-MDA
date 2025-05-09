# Initialize logging
Write-Host "Starting application setup..."

# Create necessary directories
New-Item -ItemType Directory -Force -Path data/raw, data/processed, data/pdf, logs

# Set environment variables
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)"
$env:AZURE_ENVIRONMENT = if ($env:AZURE_ENVIRONMENT) { $env:AZURE_ENVIRONMENT } else { "false" }

# Create and activate virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    
    # Install base requirements
    Write-Host "Installing base requirements..."
    pip install -r requirements.txt
    
    # Install Azure-specific requirements if in Azure environment
    if ($env:AZURE_ENVIRONMENT -eq "true") {
        Write-Host "Installing Azure-specific requirements..."
        pip install -r requirements-azure.txt
    }
} else {
    .\.venv\Scripts\Activate.ps1
}

# Process data and update vector store
Write-Host "Processing data and updating vector store..."
python -m src.update_vector_store

# Start the application
if ($env:AZURE_ENVIRONMENT -eq "true") {
    Write-Host "Starting application in Azure environment..."
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
} else {
    Write-Host "Starting application in local environment..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
} 
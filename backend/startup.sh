#!/bin/bash

echo "Starting application..."

# Ensure logs directory exists
mkdir -p /home/site/wwwroot/logs

# If you need to swap sqlite3 for pysqlite3 in Azure, keep this logic:
if [ "$AZURE_ENVIRONMENT" = "true" ]; then
    echo "Configuring pysqlite3 for Azure..."
    # Replace sqlite3 with pysqlite3 in sys.modules at runtime
    cat > run_app.py << 'EOL'
import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3

from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOL
    # Start with Gunicorn using the wrapper
    exec gunicorn -w 1 \
        --worker-class uvicorn.workers.UvicornWorker \
        --timeout 300 \
        --worker-connections 1000 \
        --keep-alive 5 \
        --worker-tmp-dir /dev/shm \
        -b 0.0.0.0:8000 run_app:app
else
    # Local/dev: run directly
    exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi 
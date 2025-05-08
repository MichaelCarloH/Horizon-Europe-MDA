#!/bin/bash
set -e

cd /home/site/wwwroot

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting application..."
exec python -m gunicorn --config gunicorn.conf.py api:app 
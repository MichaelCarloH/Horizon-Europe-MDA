#!/bin/bash
set -e

cd /home/site/wwwroot

echo "Creating virtual environment..."
python -m venv venv
source venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt
pip install gunicorn

echo "Starting application..."
exec python -m gunicorn --config gunicorn.conf.py api:app 
#!/bin/bash
set -e

cd /home/site/wwwroot

echo "Creating virtual environment..."
python -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Starting application..."
exec python -m gunicorn --config gunicorn.conf.py main:app 
#!/bin/bash
cd /home/site/wwwroot

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Start the application
python -m gunicorn --config gunicorn.conf.py api:app 
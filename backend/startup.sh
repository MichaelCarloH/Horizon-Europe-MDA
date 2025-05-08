#!/bin/bash
cd /home/site/wwwroot

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    # If no virtual environment, install dependencies globally
    pip install -r requirements.txt
    pip install gunicorn
fi

# Make sure the script is executable
chmod +x startup.sh

# Start the application
python -m gunicorn --config gunicorn.conf.py api:app 
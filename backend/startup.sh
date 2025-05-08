#!/bin/bash
cd /home/site/wwwroot

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies using uv
uv pip install -r requirements.txt
uv pip install gunicorn

# Start the application
python -m gunicorn --config gunicorn.conf.py api:app 
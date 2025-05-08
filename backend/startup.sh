#!/bin/bash
cd /home/site/wwwroot
python -m gunicorn --config gunicorn.conf.py api:app 
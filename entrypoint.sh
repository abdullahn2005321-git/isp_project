#!/bin/bash
python create_super_admin.py

if [ "$FLASK_DEBUG" = "1" ]; then
    python app.py
else
    gunicorn --bind 0.0.0.0:${PORT:-5000} --workers ${WEB_CONCURRENCY:-2} app:app
fi

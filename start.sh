#!/bin/bash
# Startup script for Railway deployment

echo "🚂 Starting Railway deployment..."

# Run the setup script
bash /app/railway_setup.sh

echo "🚀 Starting Gunicorn server..."

# Start Gunicorn
exec gunicorn ecm_website.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 1 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    --log-level debug \
    --reload

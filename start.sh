#!/bin/bash
# Optimized startup script for Railway deployment

echo "� Starting ECM Website..."

# Run migrations quickly
python manage.py migrate --noinput > /dev/null 2>&1 || echo "Migration warning (continuing...)"

# Start Gunicorn immediately
echo "Starting server on port $PORT..."

exec gunicorn ecm_website.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

# !/bin/bash
# This script will be run by Railway during deployment

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Other setup tasks can be added here

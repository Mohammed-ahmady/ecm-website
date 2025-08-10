#!/bin/bash
# Railway deployment setup script

echo "Starting Railway deployment setup..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist (for admin access)
echo "Setting up admin user..."
python manage.py shell << EOF
from django.contrib.auth.models import User
import os

admin_email = os.getenv('ADMIN_EMAIL', 'admin@ecm.com')
admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', admin_email, admin_password)
    print(f"Admin user created with email: {admin_email}")
else:
    print("Admin user already exists")
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Railway deployment setup complete!"

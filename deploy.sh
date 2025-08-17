#!/bin/bash
# Deployment script for ECM Website
# This script performs final pre-deployment checks and deployment tasks

set -e  # Exit on error

echo "🚀 Starting deployment process..."

# 1. Generate a .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚠️ No .env file found, creating from example..."
    cp .env.example .env
    echo "⚠️ WARNING: You must update the .env file with real values!"
fi

# 1a. Check if SECRET_KEY needs to be updated
echo "🔑 Checking SECRET_KEY security..."
if grep -q "django-insecure\|your_secret_key_here" .env; then
    echo "⚠️ Insecure SECRET_KEY detected in .env file"
    echo "🔧 Fixing SECRET_KEY..."
    python scripts/fix_secret_key.py
fi

# 2. Verify Python and pip
echo "🐍 Checking Python environment..."
python --version
pip --version

# 3. Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# 4. Run Django deployment checks
echo "🔍 Running Django deployment checks..."
python manage.py check --deploy

# 5. Collect static files
echo "🗂️ Collecting static files..."
python manage.py collectstatic --noinput

# 6. Create cache table for database caching
echo "💾 Creating cache table..."
python scripts/prepare_db.py

# 7. Apply database migrations
echo "🗄️ Applying database migrations..."
python manage.py migrate

# 8. Final pre-deployment checks
echo "✅ Running final checks..."

# Check if Cloudinary is configured
if [ -z "$CLOUDINARY_CLOUD_NAME" ] || [ -z "$CLOUDINARY_API_KEY" ] || [ -z "$CLOUDINARY_API_SECRET" ]; then
    echo "❌ ERROR: Cloudinary environment variables not set"
    exit 1
fi

# Check if SECRET_KEY is secure
if [[ "$SECRET_KEY" == *"django-insecure"* ]]; then
    echo "❌ ERROR: Using insecure default SECRET_KEY. Generate a new one!"
    exit 1
fi

echo "✨ Pre-deployment checks passed!"
echo "🚀 Ready for Railway deployment!"

# 9. Launch gunicorn (for testing)
if [ "$1" == "--run" ]; then
    echo "🚀 Starting Gunicorn server..."
    gunicorn ecm_website.wsgi:application
fi

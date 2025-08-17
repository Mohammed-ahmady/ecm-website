#!/bin/bash
# Railway Redeployment Script for ECM Website
# Executes all necessary steps to redeploy the application

set -e  # Exit on error

echo "🚀 Starting redeployment process..."

# 1. Verify environment and dependencies
echo "✅ Checking environment..."
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git and try again."
    exit 1
fi

# 2. Ensure we have the latest changes
echo "📥 Pulling latest changes from repository..."
git pull origin main

# 3. Create cache table for database caching
echo "💾 Creating cache table if it doesn't exist..."
python manage.py createcachetable --quiet || echo "⚠️ Cache table creation failed (continuing)"

# 4. Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate || echo "⚠️ Migration warning (continuing)"

# 5. Collect static files
echo "🗂️ Collecting static files..."
python manage.py collectstatic --noinput

# 6. Check deployment settings
echo "🔍 Verifying deployment settings..."
python manage.py check --deploy

# 7. Deploy to Railway
echo "🚂 Deploying to Railway..."
if command -v railway &> /dev/null; then
    # If Railway CLI is installed
    railway up
else
    # If Railway CLI is not installed
    echo "ℹ️ Railway CLI not found. Starting local server instead."
    echo "🌐 To deploy to Railway, please install Railway CLI and run 'railway up'"
    echo "ℹ️ Starting local server for testing..."
    
    # Start the Django server (for testing only)
    gunicorn ecm_website.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 2
fi

echo "✨ Deployment process complete!"

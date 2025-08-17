# Railway Redeployment Script for ECM Website (PowerShell Version)
# Executes all necessary steps to redeploy the application

Write-Host "🚀 Starting redeployment process..." -ForegroundColor Cyan

# 1. Verify environment and dependencies
Write-Host "✅ Checking environment..." -ForegroundColor Green
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed. Please install Git and try again." -ForegroundColor Red
    exit 1
}

# 2. Ensure we have the latest changes
Write-Host "📥 Pulling latest changes from repository..." -ForegroundColor Cyan
git pull origin main

# 3. Create cache table for database caching
Write-Host "💾 Creating cache table if it doesn't exist..." -ForegroundColor Cyan
try {
    python manage.py createcachetable --quiet
} catch {
    Write-Host "⚠️ Cache table creation failed (continuing)" -ForegroundColor Yellow
}

# 4. Run database migrations
Write-Host "🗄️ Running database migrations..." -ForegroundColor Cyan
try {
    python manage.py migrate
} catch {
    Write-Host "⚠️ Migration warning (continuing)" -ForegroundColor Yellow
}

# 5. Collect static files
Write-Host "🗂️ Collecting static files..." -ForegroundColor Cyan
python manage.py collectstatic --noinput

# 6. Check deployment settings
Write-Host "🔍 Verifying deployment settings..." -ForegroundColor Cyan
python manage.py check --deploy

# 7. Deploy to Railway
Write-Host "🚂 Deploying to Railway..." -ForegroundColor Cyan
if (Get-Command railway -ErrorAction SilentlyContinue) {
    # If Railway CLI is installed
    railway up
} else {
    # If Railway CLI is not installed
    Write-Host "ℹ️ Railway CLI not found. Starting local server instead." -ForegroundColor Yellow
    Write-Host "🌐 To deploy to Railway, please install Railway CLI and run 'railway up'" -ForegroundColor Yellow
    Write-Host "ℹ️ Starting local server for testing..." -ForegroundColor Cyan
    
    # Check if gunicorn is available
    if (Get-Command gunicorn -ErrorAction SilentlyContinue) {
        # Start with gunicorn
        gunicorn ecm_website.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 2
    } else {
        # Fall back to Django's development server
        Write-Host "Using Django development server (not recommended for production)" -ForegroundColor Yellow
        python manage.py runserver 0.0.0.0:8000
    }
}

Write-Host "✨ Deployment process complete!" -ForegroundColor Green

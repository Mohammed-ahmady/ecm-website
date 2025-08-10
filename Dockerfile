# Use Python 3.13 slim image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBUG=True \
    ALLOWED_HOSTS="*" \
    DJANGO_SETTINGS_MODULE=ecm_website.settings \
    PYTHONPATH=/app \
    PORT=${PORT:-8000}

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Ensure media directory exists and set proper permissions
RUN chmod -R 755 /app/media || mkdir -p /app/media && chmod -R 755 /app/media

# Expose port
EXPOSE 8000

# Create a non-root user
RUN adduser --disabled-password --gecos "" django

# Give proper permissions to the non-root user
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Run gunicorn with proper settings
CMD gunicorn ecm_website.wsgi:application --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 1 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    --log-level debug \
    --reload

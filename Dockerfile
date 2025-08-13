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

# Copy and set permissions for setup scripts
COPY railway_setup.sh /app/
COPY start.sh /app/
RUN chmod +x /app/railway_setup.sh /app/start.sh

# Ensure media and staticfiles directories exist with proper permissions
RUN mkdir -p /app/media /app/staticfiles && \
    chmod -R 755 /app/media /app/staticfiles

# Expose port
EXPOSE 8000

# Create a non-root user
RUN adduser --disabled-password --gecos "" django

# Give proper permissions to the non-root user
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Use the startup script
CMD ["/app/start.sh"]

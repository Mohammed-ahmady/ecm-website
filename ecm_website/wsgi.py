"""
WSGI config for ecm_website project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Initialize Sentry for error tracking in production
from ecm_website.sentry import init_sentry

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecm_website.settings')

application = get_wsgi_application()

import logging
import sys
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)

@csrf_exempt
def health_check(request):
    health_status = {
        'status': 'healthy',
        'details': {
            'database': {'status': 'unknown'},
            'debug': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'python_version': sys.version,
            'environment': 'production' if not settings.DEBUG else 'development',
        }
    }
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            if cursor.fetchone() is None:
                raise Exception("Database test query failed")
            
        health_status['details']['database'] = {
            'status': 'connected',
            'engine': settings.DATABASES['default']['ENGINE'],
            'name': settings.DATABASES['default']['NAME']
        }
        
        logger.info("Health check passed successfully")
        return JsonResponse(health_status)
        
    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        logger.error(error_msg)
        health_status.update({
            'status': 'unhealthy',
            'details': {
                **health_status['details'],
                'database': {
                    'status': 'error',
                    'message': str(e)
                }
            }
        })
        return JsonResponse(health_status, status=500)

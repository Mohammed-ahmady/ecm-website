import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

@csrf_exempt
def health_check(request):
    """
    Simple health check endpoint optimized for Railway
    """
    try:
        # Simple health status - no database check to avoid timeouts
        health_status = {
            'status': 'healthy',
            'service': 'ecm-website',
            'timestamp': '2025-08-10'
        }
        
        logger.info("Health check passed - simple mode")
        return JsonResponse(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

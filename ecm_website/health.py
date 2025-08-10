from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def health_check(request):
    """
    Ultra-simple health check for Railway
    Returns plain text OK - no JSON parsing issues
    """
    try:
        logger.info("Health check requested")
        return HttpResponse("OK", status=200, content_type="text/plain")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HttpResponse("ERROR", status=500, content_type="text/plain")

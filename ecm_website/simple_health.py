from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def root_health_check(request):
    """Simple root health check for Railway"""
    return HttpResponse("OK", status=200, content_type="text/plain")

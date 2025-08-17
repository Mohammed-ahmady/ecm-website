from django.http import HttpResponse, HttpResponseServerError
from django.db import connections
from django.db.utils import OperationalError

def health_check(request):
    try:
        # Test database connection
        for name in connections:
            cursor = connections[name].cursor()
            cursor.execute("SELECT 1;")
            cursor.fetchone()
        
        # If we get here, the database is working
        return HttpResponse("ok", content_type="text/plain")
    except OperationalError:
        return HttpResponseServerError("database error", content_type="text/plain")
    except Exception as e:
        return HttpResponseServerError(str(e), content_type="text/plain")

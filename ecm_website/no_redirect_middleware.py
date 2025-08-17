from django.http import HttpResponseRedirect, HttpResponse
import re

class NoRedirectSlashMiddleware:
    """
    Middleware to prevent 301 redirects when trailing slashes are missing.
    This helps improve Google Search Console indexing by avoiding redirect chains.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the original path
        path = request.path_info

        # Handle URLs that should respond directly (without redirecting)
        # This handles both paths with and without trailing slashes
        if path.endswith('/'):
            # Path already has a slash, proceed normally
            response = self.get_response(request)
            return response
        else:
            # Path without trailing slash
            # Check if we're trying to access one of the problematic paths
            non_slash_paths = ['/about', '/contact', '/inquiry', '/parts']
            
            if path in non_slash_paths:
                # For problematic paths, modify the path to have a trailing slash
                # but don't redirect - just handle it directly
                request.path_info = f"{path}/"
                
                # Get the response with the modified path
                response = self.get_response(request)
                
                # If it would be a redirect, handle it directly instead
                if isinstance(response, HttpResponseRedirect) and response.status_code == 301:
                    # Get the response for the URL with trailing slash
                    return self.get_response(request)
                return response
            
            # For all other paths, let Django handle it normally
            return self.get_response(request)

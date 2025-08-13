from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def canonical_url(request):
    """
    Returns the canonical URL for the current page.
    This handles trailing slashes and query parameters properly.
    """
    path = request.path
    
    # Handle trailing slash consistency
    if not path.endswith('/') and '.' not in path.split('/')[-1]:
        path = f"{path}/"
        
    full_url = request.build_absolute_uri(path)
    
    # Remove query parameters for canonical URLs
    if '?' in full_url:
        full_url = full_url.split('?')[0]
        
    return full_url

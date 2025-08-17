from django.contrib.sites.models import Site
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SiteDomainMiddleware:
    """
    Middleware to ensure the correct Site domain is always set,
    especially important for sitemap generation.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check and update the Site domain before processing the request
        try:
            # Only do this check occasionally to avoid DB hits on every request
            if getattr(request, '_site_domain_checked', False) is False:
                site = Site.objects.get(id=settings.SITE_ID)
                if site.domain != settings.SITE_DOMAIN:
                    site.name = 'Magirus Center'
                    site.domain = settings.SITE_DOMAIN
                    site.save()
                    logger.info("Site domain corrected by middleware")
                setattr(request, '_site_domain_checked', True)
        except Exception as e:
            logger.error(f"Error in SiteDomainMiddleware: {e}")
            
        response = self.get_response(request)
        return response

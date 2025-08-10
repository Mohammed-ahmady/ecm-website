# C:\Users\Mohammed\Documents\ECM\ecm_website\urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView # Only if you still use TemplateView for some pages
from parts.views import InquiryCreateView, home_view # Import your specific views
from .health import health_check
from .simple_health import root_health_check
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, PartSitemap, CategorySitemap, TruckModelSitemap
from django.http import HttpResponse
from django.contrib.sites.models import Site
import logging

logger = logging.getLogger(__name__)

# Update the domain name in the Site framework
def update_site_domain():
    try:
        site_domain = getattr(settings, 'SITE_DOMAIN', 'magiruscenter.me')
        site = Site.objects.get(id=settings.SITE_ID)
        if site.domain != site_domain:
            logger.info(f"Updating site domain from {site.domain} to {site_domain}")
            site.name = 'Magirus Center'
            site.domain = site_domain
            site.save()
            logger.info("Site domain updated successfully")
    except Exception as e:
        logger.error(f"Error updating site domain: {e}")

# Run the update function - this will execute when the app starts
try:
    update_site_domain()
except Exception as e:
    logger.error(f"Could not run site domain update: {e}")

def robots_txt(request):
    # Always use the correct domain for sitemap URL
    site_domain = getattr(settings, 'SITE_DOMAIN', 'magiruscenter.me')
    sitemap_url = f"https://{site_domain}/sitemap.xml"
    
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

sitemaps = {
    'static': StaticViewSitemap,
    'parts': PartSitemap,
    'categories': CategorySitemap,
    'truck_models': TruckModelSitemap,
}

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('healthz/', root_health_check, name='root_health_check'),  # Alternative health endpoint
    path('up/', root_health_check, name='simple_up_check'),  # Even simpler endpoint
    path('admin/', admin.site.urls),
    path('', home_view, name='home'), # Use the function-based home_view from parts.views
    
    # Direct URL pattern matches for both with and without trailing slashes
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('about', TemplateView.as_view(template_name='about.html')),  # No trailing slash version
    
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('contact', TemplateView.as_view(template_name='contact.html')),  # No trailing slash version
    
    path('inquiry/', InquiryCreateView.as_view(), name='inquiry'), # Use the InquiryCreateView
    path('inquiry', InquiryCreateView.as_view()),  # No trailing slash version
    
    path('parts/', include('parts.urls')), # Link to your parts app URLs
    path('parts', include('parts.urls')),  # No trailing slash version
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('googleffabe9f5a3599130.html', 
         lambda r: HttpResponse(
             "google-site-verification: googleffabe9f5a3599130.html", 
             content_type="text/html"
         ),
         name='google_verification'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
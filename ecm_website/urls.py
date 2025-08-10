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

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
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
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('inquiry/', InquiryCreateView.as_view(), name='inquiry'), # Use the InquiryCreateView
    path('parts/', include('parts.urls')), # Link to your parts app URLs
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
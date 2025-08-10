from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from parts.models import Part, Category, TruckModel
from datetime import datetime, timezone

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return ['home', 'about', 'contact', 'inquiry', 'parts:part_list']

    def location(self, item):
        return reverse(item)
        
    def lastmod(self, obj):
        # Return the current date for static pages
        return datetime.now(timezone.utc)

class PartSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1.0
    protocol = 'https'

    def items(self):
        return Part.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('parts:part_detail', args=[obj.slug])

class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('parts:part_list') + f'?category={obj.slug}'
        
    def lastmod(self, obj):
        # Get the last updated part in this category
        parts = Part.objects.filter(category=obj).order_by('-updated_at')
        if parts.exists():
            return parts.first().updated_at
        return datetime.now(timezone.utc)

class TruckModelSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return TruckModel.objects.all()

    def location(self, obj):
        return reverse('parts:part_list') + f'?truck_model={obj.slug}'
        
    def lastmod(self, obj):
        # Get the last updated part for this truck model
        parts = Part.objects.filter(truck_models=obj).order_by('-updated_at')
        if parts.exists():
            return parts.first().updated_at
        return datetime.now(timezone.utc)

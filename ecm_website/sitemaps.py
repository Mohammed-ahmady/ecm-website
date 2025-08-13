from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from parts.models import Part, Category, TruckModel

class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ['home', 'about', 'contact', 'inquiry', 'parts:part_list']
    
    def location(self, item):
        return reverse(item)

class PartSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return Part.objects.filter(is_active=True).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('parts:part_detail', args=[obj.slug])

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()
    
    def location(self, obj):
        return f"{reverse('parts:part_list')}?category={obj.slug}"

class TruckModelSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return TruckModel.objects.all()
    
    def location(self, obj):
        return f"{reverse('parts:part_list')}?truck_model={obj.slug}"

# Combine all sitemaps
sitemaps = {
    'static': StaticSitemap,
    'parts': PartSitemap,
    'categories': CategorySitemap, 
    'truck_models': TruckModelSitemap
}

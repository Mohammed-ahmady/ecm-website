from parts.models import CartItem, Category, TruckModel
from django.conf import settings

def cart_context(request):
    """Add cart item count to all templates"""
    if hasattr(request, 'session'):
        session_key = request.session.session_key
        if session_key:
            cart_count = CartItem.objects.filter(session_key=session_key).count()
        else:
            cart_count = 0
    else:
        cart_count = 0
    
    return {
        'cart_count': cart_count
    }

def seo_context(request):
    """Add SEO-related context to all templates"""
    # Get top categories and truck models for footer links (good for SEO)
    top_categories = Category.objects.all()[:10]
    top_truck_models = TruckModel.objects.all()[:10]
    
    company_name = "European Center for Magirus"
    site_description = "Your trusted source for authentic Magirus truck parts with worldwide shipping and expert support."
    
    # Social media URLs
    social_links = {
        "facebook": "https://facebook.com/magiruscenter",
        "instagram": "https://instagram.com/magiruscenter",
        "twitter": "https://twitter.com/magiruscenter",
    }
    
    # Company info for SEO
    company_info = {
        "name": company_name,
        "address": "206 Shubra, Asaad, Al-Sahel, Cairo Governorate, Egypt",
        "phone": "+20 10 07019879",
        "email": "sallamsameh96@gmail.com",
        "founded": "2019",
    }
    
    return {
        'top_categories': top_categories,
        'top_truck_models': top_truck_models,
        'company_name': company_name,
        'site_description': site_description,
        'social_links': social_links,
        'company_info': company_info,
        'is_production': not settings.DEBUG,
    }

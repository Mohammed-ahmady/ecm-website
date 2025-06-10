from django.urls import path
from .views import PartListView, PartDetailView
from . import views

app_name = 'parts'

urlpatterns = [
    path('', PartListView.as_view(), name='part_list'),
    path('add/<int:part_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('remove/<int:part_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_page, name='checkout_page'),
    path('<slug:slug>/', PartDetailView.as_view(), name='part_detail'),
      
]

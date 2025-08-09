from django.urls import path
from .views import PartListView, PartDetailView
from . import views

app_name = 'parts'

urlpatterns = [
    path('', PartListView.as_view(), name='part_list'),
    path('cart/add/<int:part_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update/<int:part_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:part_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update-payment/', views.update_payment_method, name='update_payment_method'),
    path('cart/update-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', views.checkout_page, name='checkout_page'),
    path('<slug:slug>/', PartDetailView.as_view(), name='part_detail'),
]

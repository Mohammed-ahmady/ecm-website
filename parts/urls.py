from django.urls import path
from .views import PartListView, PartDetailView

app_name = 'parts'

urlpatterns = [
    path('', PartListView.as_view(), name='part_list'),
    path('<slug:slug>/', PartDetailView.as_view(), name='part_detail'),
]

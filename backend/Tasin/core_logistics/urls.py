# core_logistics/urls.py

from django.urls import path
from . import views
from .views import OptimizeRouteView 

urlpatterns = [
    # It's good practice to keep API endpoints consistent
    path('barcode-details/<str:barcode>/', views.barcode_details, name='barcode-details'),
    path('optimize-route/', OptimizeRouteView.as_view(), name='optimize-route'),
]
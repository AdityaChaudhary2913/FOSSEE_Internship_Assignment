"""
URL configuration for the Equipment application.
Maps API endpoints to their respective views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatasetViewSet, AuthViewSet, health_check

# Create router and register viewsets
router = DefaultRouter()
router.register(r'datasets', DatasetViewSet, basename='dataset')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    # Health check
    path('health/', health_check, name='health-check'),
    
    # Include router URLs
    path('', include(router.urls)),
]

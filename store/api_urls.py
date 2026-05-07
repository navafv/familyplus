from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CategoryViewSet, ProductViewSet

# Initialize the router
router = DefaultRouter()

# Register the viewsets
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]

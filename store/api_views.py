from rest_framework import viewsets
from category.models import Category
from .models import Product
from .serializers import CategorySerializer, ProductSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset for viewing categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset for viewing available products.
    Includes filtering by category_slug and optimizes database queries.
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Base queryset: only available products
        # Optimization: select_related for the foreign key, prefetch_related for reverse foreign keys
        queryset = Product.objects.filter(is_available=True).select_related(
            'category'
        ).prefetch_related(
            'variation_set', 
            'productgallery_set'
        ).order_by('id')

        # Optional filtering by category_slug
        category_slug = self.request.query_params.get('category_slug', None)
        if category_slug is not None:
            queryset = queryset.filter(category__slug=category_slug)
            
        return queryset

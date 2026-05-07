from rest_framework import serializers
from category.models import Category
from .models import Product, Variation, ProductGallery

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = ['id', 'variation_category', 'variation_value', 'is_active']

class ProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    # Nested serializer for the related category
    category = CategorySerializer(read_only=True)
    
    # Nested serializer for multiple gallery images
    # We use source='productgallery_set' because the related_name wasn't explicitly set on the ForeignKey in models.py
    gallery = ProductGallerySerializer(source='productgallery_set', many=True, read_only=True)
    
    # Custom field to group variations into colors and sizes
    variations = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'slug', 'description', 'price', 
            'images', 'stock', 'is_available', 'category', 
            'created_date', 'modified_date', 'gallery', 'variations'
        ]

    def get_variations(self, obj):
        # Utilizing the custom VariationManager methods from models.py
        # obj.variation_set.all() must be prefetched in the viewset to prevent N+1 queries
        colors = VariationSerializer(obj.variation_set.filter(variation_category='color', is_active=True), many=True).data
        sizes = VariationSerializer(obj.variation_set.filter(variation_category='size', is_active=True), many=True).data
        return {
            'colors': colors,
            'sizes': sizes
        }

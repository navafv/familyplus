from rest_framework import serializers
from .models import CartItem
from store.models import Product
from store.serializers import VariationSerializer

class BasicProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'price', 'images', 'slug']

class CartItemSerializer(serializers.ModelSerializer):
    product = BasicProductSerializer(read_only=True)
    variations = VariationSerializer(many=True, read_only=True)
    sub_total = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'variations', 'quantity', 'is_active', 'sub_total']

class CartResponseSerializer(serializers.Serializer):
    cart_items = CartItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    shipping = serializers.DecimalField(max_digits=10, decimal_places=2)
    grand_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()

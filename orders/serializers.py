from rest_framework import serializers
from .models import Order, Payment, OrderProduct
from carts.serializers import BasicProductSerializer
from store.serializers import VariationSerializer

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'first_name', 'last_name', 'phone', 'email', 
            'address_line_1', 'address_line_2', 'country', 'state', 'city', 
            'order_note', 'order_total', 'shipping', 'status', 'is_ordered', 'created_at'
        ]
        read_only_fields = ['order_number', 'order_total', 'shipping', 'status', 'is_ordered', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['user', 'payment_id', 'payment_method', 'amount_paid', 'status', 'created_at']

class OrderProductSerializer(serializers.ModelSerializer):
    product = BasicProductSerializer(read_only=True)
    variation = VariationSerializer(many=True, read_only=True)

    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'variation', 'quantity', 'product_price', 'ordered', 'created_at']

class OrderDetailSerializer(OrderSerializer):
    # Related names usually default to lowercase model name + _set unless defined in ForeignKey
    order_products = OrderProductSerializer(source='orderproduct_set', many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ['payment', 'order_products']

from django.contrib import admin
from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')
    search_fields = ('cart_id',)
    list_per_page = 20

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'user', 'quantity', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('product__product_name', 'cart__cart_id', 'user__email')
    list_per_page = 20
from django.contrib import admin
from .models import Payment, Order, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'full_name', 'phone', 'email',
        'city', 'order_total', 'shipping', 'status',
        'is_ordered', 'created_at'
    )
    list_filter = ('status', 'is_ordered', 'created_at')
    search_fields = ('order_number', 'first_name', 'last_name', 'phone', 'email')
    list_per_page = 20
    inlines = [OrderProductInline]

    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion of order records
        return True  # change to False if you want to disable deletes

    def has_add_permission(self, request):
        # Prevent creating orders manually via admin
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'payment_method', 'amount_paid', 'status', 'created_at')
    search_fields = ('payment_id', 'user__email', 'status')
    list_filter = ('payment_method', 'status', 'created_at')


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'user', 'quantity', 'product_price', 'ordered', 'created_at')
    search_fields = ('order__order_number', 'product__product_name', 'user__email')
    list_filter = ('ordered', 'created_at')

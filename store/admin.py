from django.contrib import admin
from .models import Product, Variation, ReviewRating, ProductGallery
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    readonly_fields = ('id',)  # Optional, prevents accidental ID edits


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name', 'price', 'stock', 'category',
        'is_available', 'created_date', 'modified_date'
    )
    prepopulated_fields = {'slug': ('product_name',)}
    list_filter = ('category', 'is_available')
    search_fields = ('product_name', 'category__category_name')
    ordering = ('-created_date',)
    inlines = [ProductGalleryInline]


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')
    search_fields = ('product__product_name', 'variation_value')


class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'subject', 'status', 'created_at')
    list_filter = ('rating', 'status', 'created_at')
    search_fields = ('user__email', 'product__product_name', 'subject')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating, ReviewRatingAdmin)
admin.site.register(ProductGallery)

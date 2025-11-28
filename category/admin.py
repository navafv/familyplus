from django.contrib import admin
from .models import Category

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')
    search_fields = ('category_name',)
    list_filter = ('category_name',)
    ordering = ('category_name',)

admin.site.register(Category, CategoryAdmin)

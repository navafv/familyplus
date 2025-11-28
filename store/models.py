from django.db import models
from django.urls import reverse
from category.models import Category
from accounts.models import Account
from django.db.models import Avg, Count
import os


def product_image_upload_path(instance, filename):
    # uploads to photos/products/<product-slug>/<filename>
    return os.path.join('photos', 'products', instance.slug if hasattr(instance, 'slug') else 'general', filename)

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(upload_to=product_image_upload_path)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('store:product_detail', args=[self.category.slug, self.slug])
    
    def __str__(self):
        return self.product_name
    
    def average_review(self):
        result = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        return float(result['average'] or 0)
    
    def review_count(self):
        result = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        return int(result['count'] or 0)
    
class VariationManager(models.Manager):
    def colors(self):
        return super().filter(variation_category='color', is_active=True).distinct()
    
    def sizes(self):
        return super().filter(variation_category='size', is_active=True).distinct()

VARIATION_CATEGORY_CHOICES = (
    ('color', 'Color'),
    ('size', 'Size'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=VARIATION_CATEGORY_CHOICES)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=45, blank=True)
    status = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.subject
    
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    class Meta:
        verbose_name = 'Product Gallery'
        verbose_name_plural = 'Product Galleries'

    def __str__(self):
        return self.product.product_name
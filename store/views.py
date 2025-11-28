from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, ReviewRating, ProductGallery
from orders.models import OrderProduct
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from .forms import ReviewForm


def paginate_queryset(request, queryset, per_page=12, page_window=2):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page')
    paged_queryset = paginator.get_page(page)
    current_page = paged_queryset.number
    total_pages = paginator.num_pages
    start = max(1, current_page - page_window)
    end = min(total_pages, current_page + page_window)
    custom_range = []
    if start > 1:
        custom_range.append(1)
        if start > 2:
            custom_range.append(None)
    custom_range.extend(range(start, end + 1))
    if end < total_pages:
        if end < total_pages - 1:
            custom_range.append(None)
        custom_range.append(total_pages)
    return paged_queryset, custom_range

def store(request, category_slug=None):
    categories = None
    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).select_related('category')
    else:
        products = Product.objects.filter(is_available=True).order_by('id').select_related('category')
    
    paged_products, custom_page_range = paginate_queryset(request, products)
    sizes = ["XS", "S", "M", "L", "XL"]
    colors = ["red", "blue", "green", "yellow"]
    context = {
        'products': paged_products,
        'product_count': products.count(),
        'category': categories,
        'custom_page_range': custom_page_range,
        'sizes': sizes,
        'colors': colors,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    single_product = get_object_or_404(Product.objects.select_related('category'), category__slug=category_slug, slug=product_slug)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    
    orderproduct = None
    if request.user.is_authenticated:
        orderproduct = OrderProduct.objects.filter(user=request.user, product=single_product).exists()
    
    reviews = ReviewRating.objects.filter(product=single_product, status=True).select_related('user')
    product_gallery = ProductGallery.objects.filter(product=single_product)

    for review in reviews:
        review.rating_half = review.rating - 0.5
    
    star_range = range(1, 6)
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'star_range': star_range,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    products = Product.objects.none()
    keyword = request.GET.get('keyword', '')
    if keyword:
        products = Product.objects.filter(
            Q(description__icontains=keyword) | Q(product_name__icontains=keyword),
            is_available=True
        ).order_by('-created_date').select_related('category')
    
    paged_products, custom_page_range = paginate_queryset(request, products)
    
    context = {
        'products': paged_products,
        'keyword': keyword,
        'product_count': products.count(),
        'custom_page_range': custom_page_range,
    }
    return render(request, 'store/store.html', context)

def submit_review(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to submit a review.')
        return redirect('accounts:login')
    
    url = request.META.get('HTTP_REFERER')
    try:
        review = ReviewRating.objects.get(user=request.user, product_id=product_id)
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
    except ReviewRating.DoesNotExist:
        form = ReviewForm(request.POST)
        if form.is_valid():
            ReviewRating.objects.create(
                subject=form.cleaned_data['subject'],
                rating=form.cleaned_data['rating'],
                review=form.cleaned_data['review'],
                ip=request.META.get('REMOTE_ADDR'),
                product_id=product_id,
                user_id=request.user.id
            )
            messages.success(request, 'Thank you! Your review has been submitted.')
    return redirect(url)
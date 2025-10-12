from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Product, ReviewRating, ProductGallery
from orders.models import OrderProduct
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages

# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')

    product_count = products.count()

    # Paginator setup
    paginator = Paginator(products, 15)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    # --- Smart Pagination Logic ---
    # This logic creates a custom page range to display in the template
    page_window = 2  # How many pages to show on each side of the current page
    current_page = paged_products.number
    total_pages = paginator.num_pages
    
    # Calculate the start and end of the primary page window
    start = max(1, current_page - page_window)
    end = min(total_pages, current_page + page_window)

    # Build the final list of page numbers to display
    custom_page_range = []

    # Add the first page and an ellipsis if the window doesn't start at the beginning
    if start > 1:
        custom_page_range.append(1)
        if start > 2:
            custom_page_range.append(None)  # None will be rendered as '...' in the template

    # Add the pages in the main window
    custom_page_range.extend(range(start, end + 1))

    # Add an ellipsis and the last page if the window doesn't end at the last page
    if end < total_pages:
        if end < total_pages - 1:
            custom_page_range.append(None) # Ellipsis marker
        custom_page_range.append(total_pages)

    context = {
        'products': paged_products,
        'product_count': product_count,
        'category': categories,
        'custom_page_range': custom_page_range, # Pass the custom range to the template
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
    context = {
        'products': products,
        'keyword': keyword,
    }
    return render(request, 'store/store.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from decimal import Decimal


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def _get_cart_item(user, cart, product, product_variations):
    """
    Helper to get or create CartItem considering variations
    """
    cart_items = CartItem.objects.filter(
        product=product,
        user=user if user.is_authenticated else None,
        cart=cart if not user.is_authenticated else None
    )
    product_variation_ids = sorted([v.id for v in product_variations])
    
    for item in cart_items:
        existing_variation_ids = sorted([v.id for v in item.variations.all()])
        if product_variation_ids == existing_variation_ids:
            return item, True
    return None, False

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variation = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except Variation.DoesNotExist:
                continue

    if request.user.is_authenticated:
        user = request.user
        cart = None
    else:
        user = None
        cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))

    cart_item, exists = _get_cart_item(user, cart, product, product_variation)
    if exists:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            user=user,
            cart=cart
        )
        if product_variation:
            cart_item.variations.add(*product_variation)
    return redirect('carts:cart')

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('carts:cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('carts:cart')

def _calculate_cart_totals(cart_items):
    total = sum(item.product.price * Decimal(item.quantity) for item in cart_items)
    quantity = sum(item.quantity for item in cart_items)
    shipping = Decimal(40)  # move to settings.py for production
    grand_total = total + shipping
    return total, quantity, shipping, grand_total

def cart(request):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total, quantity, shipping, grand_total = _calculate_cart_totals(cart_items)
    except ObjectDoesNotExist:
        cart_items = []
        total = quantity = shipping = grand_total = Decimal(0)
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'shipping': shipping,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request):
    try:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        total, quantity, shipping, grand_total = _calculate_cart_totals(cart_items)
    except ObjectDoesNotExist:
        cart_items = []
        total = quantity = shipping = grand_total = Decimal(0)
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'shipping': shipping,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)
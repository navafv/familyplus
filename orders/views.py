from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import F
from carts.models import CartItem
from store.models import Product
from .models import Order, Payment, OrderProduct
from .forms import OrderForm
import datetime

from django.core.mail import EmailMessage
from django.template.loader import render_to_string


# ---------------------------
# Payment Processing View
# ---------------------------
@require_POST
@transaction.atomic
def payments(request):
    order_id = request.POST.get('order_id')
    if not order_id:
        return redirect('home')

    try:
        order = Order.objects.select_for_update().get(
            user=request.user, is_ordered=False, order_number=order_id
        )
    except Order.DoesNotExist:
        return redirect('home')

    # Create and save the payment
    payment = Payment.objects.create(
        user=request.user,
        payment_id=order.order_number,
        payment_method="Cash On Delivery",
        amount_paid=order.order_total,
        status="Pending",
    )

    # Mark order as completed
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move items from Cart to OrderProduct
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct.objects.create(
            order=order,
            payment=payment,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True,
        )

        # Transfer variations
        order_product.variation.set(item.variations.all())

        # Reduce product stock
        item.product.stock = F('stock') - item.quantity
        item.product.save(update_fields=['stock'])

        # Refresh from DB if you need to check if it dropped below zero (optional but good practice)
        item.product.refresh_from_db()
        if item.product.stock < 0:
            # Handle edge case where overselling happened
            pass

    # Clear user’s cart
    cart_items.delete()

    # Send confirmation email
    mail_subject = 'Thank you for your order'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })
    EmailMessage(mail_subject, message, to=[request.user.email]).send()

    # Redirect to order completion page
    return redirect('/orders/order_complete?order_number=' + str(order.order_number))


# ---------------------------
# Place Order View
# ---------------------------
def place_order(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    if not cart_items.exists():
        return redirect('store:store')

    # Calculate totals
    for item in cart_items:
        total += (item.product.price * item.quantity)
        quantity += item.quantity
    shipping = 40
    grand_total = total + shipping

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order(
                user=current_user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                address_line_1=form.cleaned_data['address_line_1'],
                address_line_2=form.cleaned_data['address_line_2'],
                country=form.cleaned_data['country'],
                state=form.cleaned_data['state'],
                city=form.cleaned_data['city'],
                order_note=form.cleaned_data['order_note'],
                order_total=grand_total,
                shipping=shipping,
                ip=request.META.get('REMOTE_ADDR'),
            )
            data.save()

            # Generate unique order number
            current_date = datetime.date.today().strftime('%Y%m%d')
            order_number = f"{current_date}{data.id}"
            data.order_number = order_number
            data.save()

            context = {
                'order': data,
                'cart_items': cart_items,
                'total': total,
                'shipping': shipping,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
        else:
            return redirect('carts:checkout')

    return redirect('store:store')


# ---------------------------
# Order Complete View
# ---------------------------
def order_complete(request):
    order_number = request.GET.get('order_number')
    if not order_number:
        return redirect('home')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        order_products = OrderProduct.objects.filter(order=order)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')

    context = {
        'order_number': order_number,
        'order': order,
        'order_products': order_products,
    }
    return render(request, 'orders/order_complete.html', context)
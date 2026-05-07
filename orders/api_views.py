import datetime
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .models import Order, Payment, OrderProduct
from carts.models import CartItem
from .serializers import OrderSerializer, OrderDetailSerializer

class CheckoutAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_user = request.user
        cart_items = CartItem.objects.filter(user=current_user, is_active=True)
        
        if not cart_items.exists():
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate totals
        total = sum((item.product.price * item.quantity) for item in cart_items)
        shipping = 40  # Hardcoded exactly as in original views.py
        grand_total = total + shipping

        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Save the Order with calculated totals and user IP
            order = serializer.save(
                user=current_user,
                order_total=grand_total,
                shipping=shipping,
                ip=request.META.get('REMOTE_ADDR'),
                is_ordered=False
            )

            # Generate unique order number (YYYYMMDD + order.id)
            current_date = datetime.date.today().strftime('%Y%m%d')
            order_number = f"{current_date}{order.id}"
            order.order_number = order_number
            order.save()

            return Response({
                "message": "Order created successfully. Proceed to payment.",
                "order_number": order.order_number,
                "grand_total": grand_total
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentProcessAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_number = request.data.get('order_number')
        if not order_number:
            return Response({"error": "order_number is required."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            try:
                # Lock the order row to prevent race conditions during payment processing
                order = Order.objects.select_for_update().get(
                    user=request.user, is_ordered=False, order_number=order_number
                )
            except Order.DoesNotExist:
                return Response({"error": "Order does not exist or is already processed."}, status=status.HTTP_404_NOT_FOUND)

            # Create the Payment object (hardcoded to Cash On Delivery as per old logic)
            payment = Payment.objects.create(
                user=request.user,
                payment_id=order.order_number,
                payment_method="Cash On Delivery",
                amount_paid=str(order.order_total),
                status="Pending",
            )

            order.payment = payment
            order.is_ordered = True
            order.save()

            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            if not cart_items.exists():
                # Should not happen ideally if checkout passed, but safe to check
                return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

            # Move cart items to OrderProduct and reduce stock securely
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

                # Safely reduce stock using F() expressions to prevent concurrency race conditions
                item.product.stock = F('stock') - item.quantity
                item.product.save(update_fields=['stock'])

            # Clear user's cart
            cart_items.delete()

            # Send order confirmation email pointing to the future React application
            mail_subject = 'Thank you for your order'
            message = render_to_string('orders/order_received_email.html', {
                'user': request.user,
                'order': order,
                'react_order_url': f"http://localhost:3000/order-complete/{order.order_number}/"
            })
            EmailMessage(mail_subject, message, to=[request.user.email]).send(fail_silently=True)

            return Response({
                "message": "Payment processed and order completed successfully.",
                "order_number": order.order_number
            }, status=status.HTTP_200_OK)

class OrderHistoryAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, is_ordered=True).order_by('-created_at')

class OrderDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer
    lookup_field = 'order_number'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, is_ordered=True)

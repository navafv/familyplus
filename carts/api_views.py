from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal

from .models import Cart, CartItem
from store.models import Product, Variation
from .serializers import CartResponseSerializer

def _get_cart_from_request(request):
    if request.user.is_authenticated:
        return None
    cart_id = request.META.get('HTTP_X_CART_ID')
    if not cart_id:
        raise ValidationError({"detail": "X-Cart-Id header is required for anonymous users."})
    cart, _ = Cart.objects.get_or_create(cart_id=cart_id)
    return cart

def _get_cart_item(user, cart, product, product_variations):
    """
    Helper to get or create CartItem considering variations.
    Strictly matches original logic.
    """
    cart_items = CartItem.objects.filter(
        product=product,
        user=user if user and user.is_authenticated else None,
        cart=cart if not (user and user.is_authenticated) else None
    )
    product_variation_ids = sorted([v.id for v in product_variations])
    
    for item in cart_items:
        existing_variation_ids = sorted([v.id for v in item.variations.all()])
        if product_variation_ids == existing_variation_ids:
            return item, True
    return None, False

class CartDetailAPIView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user, is_active=True).select_related('product').prefetch_related('variations')
            else:
                cart = _get_cart_from_request(request)
                cart_items = CartItem.objects.filter(cart=cart, is_active=True).select_related('product').prefetch_related('variations')
                
            total = sum(item.product.price * Decimal(item.quantity) for item in cart_items)
            quantity = sum(item.quantity for item in cart_items)
            shipping = Decimal(40)
            grand_total = total + shipping
        except (ObjectDoesNotExist, ValidationError):
            cart_items = []
            total = quantity = shipping = grand_total = Decimal(0)

        data = {
            'cart_items': cart_items,
            'total': total,
            'shipping': shipping,
            'grand_total': grand_total,
            'quantity': quantity
        }
        serializer = CartResponseSerializer(data)
        return Response(serializer.data)

class CartItemAddAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product_variation = []
        
        # Expect variations as a dictionary: {"color": "red", "size": "M"}
        variations_data = request.data.get('variations', {})
        for key, value in variations_data.items():
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except Variation.DoesNotExist:
                continue

        cart = _get_cart_from_request(request)
        user = request.user if request.user.is_authenticated else None

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
                
        return Response({"message": "Item added to cart."}, status=status.HTTP_200_OK)

class CartItemDecreaseAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, product_id, cart_item_id):
        product = get_object_or_404(Product, id=product_id)
        try:
            if request.user.is_authenticated:
                cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            else:
                cart = _get_cart_from_request(request)
                cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
                
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
            return Response({"message": "Item quantity decreased."}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND)

class CartItemRemoveAPIView(views.APIView):
    permission_classes = [AllowAny]

    def delete(self, request, product_id, cart_item_id):
        product = get_object_or_404(Product, id=product_id)
        try:
            if request.user.is_authenticated:
                cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            else:
                cart = _get_cart_from_request(request)
                cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
                
            cart_item.delete()
            return Response({"message": "Item removed from cart."}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND)

class CartMergeAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_id = request.data.get('cart_id') or request.META.get('HTTP_X_CART_ID')
        if not cart_id:
            return Response({"error": "cart_id or X-Cart-Id header is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session_cart = Cart.objects.get(cart_id=cart_id)
            user = request.user
            
            session_items = CartItem.objects.filter(cart=session_cart)
            user_items = CartItem.objects.filter(user=user)

            for session_item in session_items:
                session_variations = list(session_item.variations.all())
                matched = False
                for user_item in user_items:
                    user_variations = list(user_item.variations.all())
                    if session_item.product == user_item.product and session_variations == user_variations:
                        user_item.quantity += session_item.quantity
                        user_item.save()
                        matched = True
                        break
                if not matched:
                    session_item.user = user
                    session_item.cart = None
                    session_item.save()
            
            # Clean up the old session cart
            session_cart.delete()
            
            return Response({"message": "Cart merged successfully."}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"message": "No anonymous cart found to merge."}, status=status.HTTP_200_OK)

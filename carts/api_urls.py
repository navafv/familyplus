from django.urls import path
from .api_views import (
    CartDetailAPIView, CartItemAddAPIView, 
    CartItemDecreaseAPIView, CartItemRemoveAPIView,
    CartMergeAPIView
)

urlpatterns = [
    path('', CartDetailAPIView.as_view(), name='api-cart-detail'),
    path('add/<int:product_id>/', CartItemAddAPIView.as_view(), name='api-cart-add'),
    path('decrease/<int:product_id>/<int:cart_item_id>/', CartItemDecreaseAPIView.as_view(), name='api-cart-decrease'),
    path('remove/<int:product_id>/<int:cart_item_id>/', CartItemRemoveAPIView.as_view(), name='api-cart-remove'),
    path('merge/', CartMergeAPIView.as_view(), name='api-cart-merge'),
]

from django.urls import path
from .api_views import (
    CheckoutAPIView, PaymentProcessAPIView, 
    OrderHistoryAPIView, OrderDetailAPIView
)

urlpatterns = [
    path('checkout/', CheckoutAPIView.as_view(), name='api-checkout'),
    path('process-payment/', PaymentProcessAPIView.as_view(), name='api-process-payment'),
    path('history/', OrderHistoryAPIView.as_view(), name='api-order-history'),
    path('<str:order_number>/', OrderDetailAPIView.as_view(), name='api-order-detail'),
]

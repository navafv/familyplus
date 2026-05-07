from django.urls import path
from .api_views import (
    RegisterAPIView, VerifyEmailAPIView, ProfileAPIView, 
    ChangePasswordAPIView, ContactAPIView, NewsletterAPIView
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api-register'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='api-verify-email'),
    path('profile/', ProfileAPIView.as_view(), name='api-profile'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='api-change-password'),
    path('contact/', ContactAPIView.as_view(), name='api-contact'),
    path('newsletter/', NewsletterAPIView.as_view(), name='api-newsletter'),
]

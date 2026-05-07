from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from .models import Account
from .serializers import (
    RegistrationSerializer, UserSerializer, ChangePasswordSerializer,
    ContactMessageSerializer, NewsletterSubscriberSerializer
)

class RegisterAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        
        # Replicating the exact same business logic from old views.py
        # Send verification email pointing to the future React frontend
        mail_subject = 'Activate your Family Plus account'
        
        # We assume the React app runs on localhost:3000 locally
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_link = f"http://localhost:3000/verify/{uid}/{token}/"

        message = render_to_string('accounts/account_verification_email.html', {
            'user': user,
            'verification_link': verification_link,
        })
        EmailMessage(mail_subject, message, to=[user.email]).send(fail_silently=False)

class VerifyEmailAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        uidb64 = request.data.get('uidb64')
        token = request.data.get('token')

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Your account has been activated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired activation link.'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        # Always return the currently authenticated user
        return self.request.user

class ChangePasswordAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check the current password
            if not user.check_password(serializer.validated_data.get("current_password")):
                return Response({"current_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # Update to the new password
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContactMessageSerializer

class NewsletterAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = NewsletterSubscriberSerializer

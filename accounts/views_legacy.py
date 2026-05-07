from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, url_has_allowed_host_and_scheme
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError

from .forms import RegistrationForm, UserForm, UserProfileForm, NewsletterSubscriptionForm
from .models import Account, UserProfile

from orders.models import Order, OrderProduct
from carts.models import Cart, CartItem
from carts.views import _cart_id

import logging

logger = logging.getLogger(__name__)


# --- Helper Functions ---

def merge_cart(user, session_cart):
    """
    Merge session cart items with user cart items on login
    """
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


# --- User Registration ---
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name, last_name=last_name,
                email=email, username=username, password=password
            )
            user.phone_number = phone_number
            user.is_active = False  # Require email verification
            user.save()

            # Create user profile with default picture
            UserProfile.objects.create(user=user, profile_picture='default/default-user.png')

            # Send verification email
            current_site = get_current_site(request)
            mail_subject = 'Activate your Family Plus account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            EmailMessage(mail_subject, message, to=[email]).send(fail_silently=False)

            messages.success(request, 'Account created! Please verify your email before login.')
            return redirect(f'/accounts/login/?command=verification&email={email}')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# --- Login ---
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(email=email, password=password)

        if user:
            try:
                session_cart = Cart.objects.get(cart_id=_cart_id(request))
                merge_cart(user, session_cart)
            except Cart.DoesNotExist:
                pass
            except Exception as e:
                logger.exception("Error merging cart: %s", e)

            auth.login(request, user)
            messages.success(request, f'Welcome back, {user.first_name} {user.last_name}!')

            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('accounts:login')
    return render(request, 'accounts/login.html')


# --- Logout ---
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


# --- Activate Account ---
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Invalid or expired activation link.')
        return redirect('accounts:register')


# --- Dashboard ---
@login_required(login_url='login')
def dashboard(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    orders_count = Order.objects.filter(user=request.user, is_ordered=True).count()
    return render(request, 'accounts/dashboard.html', {
        'userprofile': userprofile,
        'orders_count': orders_count
    })


# --- Forgot Password ---
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Account.objects.get(email=email)
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Family Plus Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            EmailMessage(mail_subject, message, to=[email]).send(fail_silently=False)
            messages.success(request, 'Password reset email sent successfully.')
            return redirect('accounts:login')
        except Account.DoesNotExist:
            messages.error(request, 'Account does not exist')
            return redirect('accounts:forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


# --- Reset Password Validation ---
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('accounts:resetPassword')
    else:
        messages.error(request, 'This link is invalid or has expired.')
        return redirect('accounts:login')


# --- Reset Password ---
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('accounts:resetPassword')

        uid = request.session.get('uid')
        user = Account.objects.get(pk=uid)
        try:
            from django.contrib.auth.password_validation import validate_password
            validate_password(password, user=user)
        except ValidationError as e:
            messages.error(request, '; '.join(e.messages))
            return redirect('accounts:resetPassword')

        user.set_password(password)
        user.save()
        messages.success(request, 'Password reset successful.')
        return redirect('accounts:login')

    return render(request, 'accounts/resetPassword.html')


# --- Orders & Profile ---
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    return render(request, 'accounts/my_orders.html', {'orders': orders})


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('accounts:change_password')

        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('accounts:change_password')

        try:
            from django.contrib.auth.password_validation import validate_password
            validate_password(new_password, user=user)
        except ValidationError as e:
            messages.error(request, '; '.join(e.messages))
            return redirect('accounts:change_password')

        user.set_password(new_password)
        user.save()
        auth.logout(request)  # Force logout after password change
        messages.success(request, 'Password updated. Please login again.')
        return redirect('accounts:login')

    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_number=order_id)
    order_detail = OrderProduct.objects.filter(order=order)
    subtotal = sum(item.product_price * item.quantity for item in order_detail)
    return render(request, 'accounts/order_detail.html', {
        'order': order,
        'order_detail': order_detail,
        'subtotal': subtotal
    })


# --- Newsletter Subscription ---
def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterSubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for subscribing!')
        else:
            messages.error(request, 'Email is invalid or already subscribed.')
    return redirect(request.META.get('HTTP_REFERER', reverse_lazy('home')))
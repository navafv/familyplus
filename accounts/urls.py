from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),

    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("resetpassword-validate/<uidb64>/<token>/", views.resetpassword_validate, name="resetpassword_validate"),
    path("forgot-password/", views.forgotPassword, name="forgotPassword"),
    path("reset-password/", views.resetPassword, name="resetPassword"),

    path("my-orders/", views.my_orders, name="my_orders"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("order-detail/<int:order_id>/", views.order_detail, name="order_detail"),

    path("subscribe/", views.subscribe_newsletter, name="subscribe"),
]
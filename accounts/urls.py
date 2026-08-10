from django.urls import path
from .views import register, login_view, verify_mfa, logout_view, profile

urlpatterns = [
    path("register/", register),
    path("login/", login_view),
    path("verify-mfa/", verify_mfa),
    path("logout/", logout_view),
    path("profile/", profile),
]

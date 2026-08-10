import secrets
import pyotp
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import UserSecurityProfile
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({"id": user.id, "username": user.username}, status=201)

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    profile, _ = UserSecurityProfile.objects.get_or_create(user=user)
    if profile.mfa_enabled:
        request.session["pending_mfa_user"] = user.id
        return Response({"mfa_required": True})
    login(request, user)
    return Response({"authenticated": True, "username": user.username})

@api_view(["POST"])
@permission_classes([AllowAny])
def verify_mfa(request):
    user_id = request.session.get("pending_mfa_user")
    if not user_id:
        return Response({"detail": "No pending MFA login."}, status=400)
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserSecurityProfile, user=user)
    if not profile.mfa_enabled or not pyotp.TOTP(profile.mfa_secret).verify(request.data.get("otp", "")):
        return Response({"detail": "Invalid OTP."}, status=401)
    login(request, user)
    request.session.pop("pending_mfa_user", None)
    return Response({"authenticated": True, "username": user.username})

@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response({"logged_out": True})

@api_view(["GET", "POST"])
def profile(request):
    profile, _ = UserSecurityProfile.objects.get_or_create(user=request.user)
    if request.method == "GET":
        return Response(ProfileSerializer(profile).data)
    if request.data.get("enable_mfa"):
        if not profile.mfa_secret:
            profile.mfa_secret = pyotp.random_base32()
        profile.mfa_enabled = True
        profile.save()
        return Response({"mfa_enabled": True, "secret": profile.mfa_secret})
    profile.mfa_enabled = False
    profile.save()
    return Response({"mfa_enabled": False})

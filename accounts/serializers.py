from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import UserSecurityProfile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        UserSecurityProfile.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is inactive.")
        attrs["user"] = user
        return attrs

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSecurityProfile
        fields = ["mfa_enabled"]

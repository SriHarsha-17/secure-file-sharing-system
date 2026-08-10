from rest_framework import serializers
from .models import SecureSpace, SpaceMember

class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecureSpace
        fields = ["id", "name", "owner", "created_at", "revoked"]
        read_only_fields = ["id", "owner", "created_at", "revoked"]

class MemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = SpaceMember
        fields = ["id", "username", "role", "joined_at"]

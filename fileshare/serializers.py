from rest_framework import serializers
from .models import EncryptedFile, FilePermission, ShareToken

class EncryptedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedFile
        fields = [
            "id", "original_name", "size_bytes", "algorithm",
            "file_hash", "created_at", "revoked"
        ]
        read_only_fields = fields

class PermissionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = FilePermission
        fields = ["id", "username", "can_download", "can_share", "expires_at"]

class ShareTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareToken
        fields = ["token", "expires_at", "max_downloads", "downloads", "revoked", "created_at"]
        read_only_fields = ["token", "downloads", "revoked", "created_at"]

import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class EncryptedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_files")
    original_name = models.CharField(max_length=255)
    stored_file = models.FileField(upload_to="encrypted/")
    size_bytes = models.BigIntegerField(default=0)
    algorithm = models.CharField(max_length=40, default="AES-256-GCM")
    nonce_b64 = models.TextField()
    file_hash = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)

class FilePermission(models.Model):
    file = models.ForeignKey(EncryptedFile, on_delete=models.CASCADE, related_name="permissions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_download = models.BooleanField(default=True)
    can_share = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["file", "user"], name="unique_file_user_permission")
        ]

    def is_active(self):
        return not self.expires_at or self.expires_at > timezone.now()

class ShareToken(models.Model):
    token = models.CharField(max_length=128, unique=True, db_index=True)
    file = models.ForeignKey(EncryptedFile, on_delete=models.CASCADE, related_name="share_tokens")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_downloads = models.PositiveIntegerField(default=1)
    downloads = models.PositiveIntegerField(default=0)
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def active(self):
        return (
            not self.revoked
            and self.downloads < self.max_downloads
            and (not self.expires_at or self.expires_at > timezone.now())
        )

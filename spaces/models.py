from django.contrib.auth.models import User
from django.db import models
import uuid

class SecureSpace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_spaces")
    created_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)

class SpaceMember(models.Model):
    ROLE_CHOICES = [("OWNER", "Owner"), ("EDITOR", "Editor"), ("VIEWER", "Viewer")]
    space = models.ForeignKey(SecureSpace, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="VIEWER")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["space", "user"], name="unique_space_member")
        ]

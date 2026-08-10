from django.contrib.auth.models import User
from django.db import models
from fileshare.models import EncryptedFile

class AuditEvent(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=80)
    file = models.ForeignKey(EncryptedFile, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

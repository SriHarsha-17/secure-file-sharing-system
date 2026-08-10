from django.contrib import admin
from .models import EncryptedFile, FilePermission, ShareToken
admin.site.register(EncryptedFile)
admin.site.register(FilePermission)
admin.site.register(ShareToken)

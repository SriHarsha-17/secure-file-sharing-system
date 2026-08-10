import secrets
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import EncryptedFile, FilePermission, ShareToken
from .serializers import EncryptedFileSerializer, PermissionSerializer, ShareTokenSerializer
from auditlog.utils import record_event

@api_view(["POST"])
def upload_encrypted_file(request):
    upload = request.FILES.get("file")
    if not upload:
        return Response({"detail": "Encrypted file is required."}, status=400)

    original_name = request.data.get("original_name", upload.name)
    nonce_b64 = request.data.get("nonce_b64", "")
    file_hash = request.data.get("file_hash", "")

    obj = EncryptedFile.objects.create(
        owner=request.user,
        original_name=original_name,
        stored_file=upload,
        size_bytes=upload.size,
        nonce_b64=nonce_b64,
        file_hash=file_hash,
    )
    record_event(request.user, "UPLOAD", obj, f"Uploaded encrypted file {original_name}")
    return Response(EncryptedFileSerializer(obj).data, status=201)

@api_view(["GET"])
def my_files(request):
    files = EncryptedFile.objects.filter(owner=request.user, revoked=False).order_by("-created_at")
    shared = EncryptedFile.objects.filter(
        permissions__user=request.user,
        permissions__can_download=True,
        revoked=False
    ).distinct().order_by("-created_at")
    return Response({
        "owned": EncryptedFileSerializer(files, many=True).data,
        "shared": EncryptedFileSerializer(shared, many=True).data,
    })

def has_download_access(user, obj):
    if obj.owner_id == user.id:
        return True
    try:
        p = obj.permissions.get(user=user)
        return p.can_download and p.is_active()
    except FilePermission.DoesNotExist:
        return False

@api_view(["GET"])
def download_file(request, file_id):
    obj = get_object_or_404(EncryptedFile, id=file_id, revoked=False)
    if not has_download_access(request.user, obj):
        record_event(request.user, "DENIED_DOWNLOAD", obj, "Unauthorized download attempt")
        return Response({"detail": "Access denied."}, status=403)
    record_event(request.user, "DOWNLOAD", obj, "Downloaded encrypted ciphertext")
    return FileResponse(obj.stored_file.open("rb"), as_attachment=True, filename=obj.original_name + ".enc")

@api_view(["POST"])
def grant_permission(request, file_id):
    obj = get_object_or_404(EncryptedFile, id=file_id, owner=request.user)
    username = request.data.get("username")
    target = get_object_or_404(User, username=username)
    p, _ = FilePermission.objects.update_or_create(
        file=obj,
        user=target,
        defaults={
            "can_download": bool(request.data.get("can_download", True)),
            "can_share": bool(request.data.get("can_share", False)),
            "expires_at": request.data.get("expires_at") or None,
        },
    )
    record_event(request.user, "GRANT_ACCESS", obj, f"Granted access to {target.username}")
    return Response(PermissionSerializer(p).data)

@api_view(["GET"])
def permissions(request, file_id):
    obj = get_object_or_404(EncryptedFile, id=file_id, owner=request.user)
    return Response(PermissionSerializer(obj.permissions.select_related("user"), many=True).data)

@api_view(["POST"])
def create_share_token(request, file_id):
    obj = get_object_or_404(EncryptedFile, id=file_id, owner=request.user)
    minutes = int(request.data.get("expires_minutes", 60))
    max_downloads = max(1, int(request.data.get("max_downloads", 1)))
    token = secrets.token_urlsafe(48)
    share = ShareToken.objects.create(
        token=token,
        file=obj,
        created_by=request.user,
        expires_at=timezone.now() + timedelta(minutes=minutes),
        max_downloads=max_downloads,
    )
    record_event(request.user, "CREATE_SHARE", obj, "Created expiring share token")
    return Response(ShareTokenSerializer(share).data, status=201)

@api_view(["POST"])
def revoke_share(request, token):
    share = get_object_or_404(ShareToken, token=token, created_by=request.user)
    share.revoked = True
    share.save(update_fields=["revoked"])
    record_event(request.user, "REVOKE_SHARE", share.file, "Revoked share token")
    return Response({"revoked": True})

@api_view(["GET"])
def token_download(request, token):
    share = get_object_or_404(ShareToken.objects.select_related("file"), token=token)
    if not share.active() or share.file.revoked:
        return Response({"detail": "Share is expired, revoked, or exhausted."}, status=403)
    share.downloads += 1
    share.save(update_fields=["downloads"])
    return FileResponse(
        share.file.stored_file.open("rb"),
        as_attachment=True,
        filename=share.file.original_name + ".enc"
    )

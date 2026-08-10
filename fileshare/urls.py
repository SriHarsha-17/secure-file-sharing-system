from django.urls import path
from .views import (
    upload_encrypted_file, my_files, download_file, grant_permission,
    permissions, create_share_token, revoke_share, token_download
)

urlpatterns = [
    path("upload/", upload_encrypted_file),
    path("mine/", my_files),
    path("<uuid:file_id>/download/", download_file),
    path("<uuid:file_id>/permissions/", permissions),
    path("<uuid:file_id>/grant/", grant_permission),
    path("<uuid:file_id>/share/", create_share_token),
    path("share/<str:token>/revoke/", revoke_share),
    path("share/<str:token>/download/", token_download),
]

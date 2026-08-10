from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
from django.conf.urls.static import static


@ensure_csrf_cookie
def dashboard(request):
    return TemplateView.as_view(template_name="dashboard.html")(request)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/files/", include("fileshare.urls")),
    path("api/spaces/", include("spaces.urls")),
    path("api/audit/", include("auditlog.urls")),
    path("", dashboard, name="dashboard"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
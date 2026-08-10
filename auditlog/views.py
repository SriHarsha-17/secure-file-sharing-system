from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AuditEvent

@api_view(["GET"])
def events(request):
    qs = AuditEvent.objects.filter(user=request.user).order_by("-created_at")[:200]
    return Response([
        {
            "action": e.action,
            "description": e.description,
            "ip_address": e.ip_address,
            "created_at": e.created_at,
        } for e in qs
    ])

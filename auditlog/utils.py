from .models import AuditEvent

def record_event(user, action, file_obj=None, description="", request=None):
    ip = None
    if request:
        ip = request.META.get("REMOTE_ADDR")
    return AuditEvent.objects.create(
        user=user,
        action=action,
        file=file_obj,
        description=description,
        ip_address=ip,
    )

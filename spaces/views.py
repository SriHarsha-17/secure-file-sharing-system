from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SecureSpace, SpaceMember
from .serializers import SpaceSerializer, MemberSerializer
from auditlog.utils import record_event

@api_view(["POST"])
def create_space(request):
    name = request.data.get("name", "").strip()
    if not name:
        return Response({"detail": "Space name is required."}, status=400)
    space = SecureSpace.objects.create(name=name, owner=request.user)
    SpaceMember.objects.create(space=space, user=request.user, role="OWNER")
    record_event(request.user, "CREATE_SPACE", None, f"Created Secure Space {name}")
    return Response(SpaceSerializer(space).data, status=201)

@api_view(["GET"])
def my_spaces(request):
    spaces = SecureSpace.objects.filter(members__user=request.user, revoked=False).distinct()
    return Response(SpaceSerializer(spaces, many=True).data)

@api_view(["POST"])
def add_member(request, space_id):
    space = get_object_or_404(SecureSpace, id=space_id, owner=request.user, revoked=False)
    username = request.data.get("username")
    target = get_object_or_404(User, username=username)
    role = request.data.get("role", "VIEWER")
    if role not in {"EDITOR", "VIEWER"}:
        return Response({"detail": "Invalid role."}, status=400)
    member, _ = SpaceMember.objects.update_or_create(
        space=space, user=target, defaults={"role": role}
    )
    record_event(request.user, "ADD_MEMBER", None, f"Added {target.username} to {space.name}")
    return Response(MemberSerializer(member).data)

@api_view(["GET"])
def members(request, space_id):
    space = get_object_or_404(
        SecureSpace, id=space_id, members__user=request.user, revoked=False
    )
    return Response(MemberSerializer(space.members.select_related("user"), many=True).data)

@api_view(["POST"])
def revoke_member(request, space_id, user_id):
    space = get_object_or_404(SecureSpace, id=space_id, owner=request.user, revoked=False)
    member = get_object_or_404(SpaceMember, space=space, user_id=user_id)
    if member.user_id == request.user.id:
        return Response({"detail": "Owner cannot be revoked."}, status=400)
    member.delete()
    record_event(request.user, "REVOKE_MEMBER", None, f"Revoked user {user_id} from {space.name}")
    return Response({"revoked": True})

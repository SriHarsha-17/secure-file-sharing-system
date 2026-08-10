from django.urls import path
from .views import create_space, my_spaces, add_member, members, revoke_member

urlpatterns = [
    path("", create_space),
    path("mine/", my_spaces),
    path("<uuid:space_id>/members/", members),
    path("<uuid:space_id>/members/add/", add_member),
    path("<uuid:space_id>/members/<int:user_id>/revoke/", revoke_member),
]

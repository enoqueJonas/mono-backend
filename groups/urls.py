from django.urls import path

from groups.views.groups import GroupListCreateView
from groups.views.members import GroupMemberListCreateView
from groups.views.groups import GroupListCreateView, GroupDetailView

urlpatterns = [
    path("", GroupListCreateView.as_view(), name="group-list-create"),
    path("<uuid:group_id>/", GroupDetailView.as_view(), name="group-detail"),
    path("<uuid:group_id>/members/",
         GroupMemberListCreateView.as_view(), name="group-members"),
]

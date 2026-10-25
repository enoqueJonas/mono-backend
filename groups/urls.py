from django.urls import path

from groups.views.groups import GroupListCreateView
from groups.views.members import (
    GroupMemberDetailView,
    GroupMemberListCreateView,
)
from groups.views.groups import GroupListCreateView, GroupDetailView, GroupBlockchainHistoryView
from groups.views.settings import GroupSettingsUpdateView, GroupSettingsIntegrityView
from groups.views.rotation import (
    GroupRotationView,
)

urlpatterns = [
    path('<uuid:group_id>/blockchain-history/', GroupBlockchainHistoryView.as_view(), name='group-blockchain-history'),
    path('<uuid:group_id>/settings/<int:version>/integrity/', GroupSettingsIntegrityView.as_view(), name='group-settings-integrity'),
    path("", GroupListCreateView.as_view(), name="group-list-create"),
    path("<uuid:group_id>/", GroupDetailView.as_view(), name="group-detail"),
    path("<uuid:group_id>/members/",
         GroupMemberListCreateView.as_view(), name="group-members"),
    path("<uuid:group_id>/settings/", GroupSettingsUpdateView.as_view(),
         name="group-settings-update",),
    path(
        "<uuid:group_id>/members/<uuid:group_member_id>/",
        GroupMemberDetailView.as_view(),
        name="group-member-detail",
    ),
    path(
        "<uuid:group_id>/rotation/",
        GroupRotationView.as_view(),
        name="group-rotation",
    ),
]

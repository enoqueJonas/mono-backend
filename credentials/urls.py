from django.urls import path

from credentials.views.credentials import (
    CredentialDetailView,
    MyCredentialListView,
)
from credentials.views.group_credentials import (
    GroupCredentialIssueView,
)


urlpatterns = [
    path(
        "",
        MyCredentialListView.as_view(),
        name="my-credential-list",
    ),
    path(
        "<uuid:credential_id>/",
        CredentialDetailView.as_view(),
        name="credential-detail",
    ),
    path(
        "<uuid:group_id>/credentials/",
        GroupCredentialIssueView.as_view(),
        name="group-credential-issue",
    ),
]

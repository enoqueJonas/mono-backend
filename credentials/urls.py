from django.urls import path

from credentials.views.credentials import (
    CredentialDetailView,
    MyCredentialListView,
)
from credentials.views.group_credentials import (
    GroupCredentialIssueView,
)
from credentials.views.verify_credential import (
    VerifyCredentialView,
)
from credentials.views.revoke_credential import (
    RevokeCredentialView,
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
    path(
        "verify/",
        VerifyCredentialView.as_view(),
        name="credential-verify",
    ),
    path(
        "<uuid:credential_id>/revoke/",
        RevokeCredentialView.as_view(),
        name="credential-revoke",
    ),
]

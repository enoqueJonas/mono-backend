from django.urls import path

from identity.views.group_did import (
    GroupDIDDocumentView,
    GroupDIDView,
)
from identity.views.user_did import (
    MyDIDDocumentView,
    MyDIDView,
)

urlpatterns = [
    path(
        "me/",
        MyDIDView.as_view(),
        name="my-did",
    ),
    path(
        "me/document/",
        MyDIDDocumentView.as_view(),
        name="my-did-document",
    ),
    path(
        "groups/<uuid:group_id>/",
        GroupDIDView.as_view(),
        name="group-did",
    ),
    path(
        "groups/<uuid:group_id>/document/",
        GroupDIDDocumentView.as_view(),
        name="group-did-document",
    ),
]

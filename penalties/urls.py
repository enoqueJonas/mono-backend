from django.urls import path

from penalties.views import (
    GroupPenaltyListCreateView,
    GroupPenaltyResolveView,
)


urlpatterns = [
    path(
        "groups/<uuid:group_id>/penalties/",
        GroupPenaltyListCreateView.as_view(),
        name="group-penalty-list-create",
    ),
    path(
        (
            "groups/<uuid:group_id>/penalties/"
            "<uuid:penalty_id>/resolve/"
        ),
        GroupPenaltyResolveView.as_view(),
        name="group-penalty-resolve",
    ),
]

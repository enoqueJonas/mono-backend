from django.urls import path

from contributions.views.contributions import GroupContributionCreateView

urlpatterns = [
    path(
        "groups/<uuid:group_id>/contributions/",
        GroupContributionCreateView.as_view(),
        name="group-contribution-create",
    ),
]

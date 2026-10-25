from django.urls import path

from contributions.views.contributions import GroupContributionCreateView, ContributionIntegrityView

urlpatterns = [
    path('groups/<uuid:group_id>/contributions/<uuid:contribution_id>/integrity/', ContributionIntegrityView.as_view(), name='contribution-integrity'),
    path(
        "groups/<uuid:group_id>/contributions/",
        GroupContributionCreateView.as_view(),
        name="group-contribution-create",
    ),
]

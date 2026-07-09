from django.urls import path

from groups.views.groups import GroupListCreateView

urlpatterns = [
    path("", GroupListCreateView.as_view(), name="group-list-create"),
]

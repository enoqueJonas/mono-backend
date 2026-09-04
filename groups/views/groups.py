from core.exceptions import DomainException
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import success
from groups.serializers.create_group import CreateGroupSerializer
from groups.serializers.group import (
    GroupDetailSerializer,
    GroupSerializer,
)
from groups.services.group_service import GroupService
from groups.selectors.group_selector import GroupSelector


class GroupListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        groups = GroupSelector.list_user_groups(user=request.user)
        return success(
            data=GroupSerializer(
                groups,
                many=True,
                context={"user": request.user},
            ).data
        )

    def post(self, request):

        serializer = CreateGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = GroupService.create_group(
            created_by=request.user,
            data=serializer.validated_data,
        )

        return success(
            data=GroupSerializer(
                group,
                context={"user": request.user},
            ).data,
            message="Group created successfully.",
            status_code=201,
        )


class GroupNotFound(DomainException):
    default_message = "Group not found."


class GroupDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        group = GroupSelector.get_group_for_user(
            group_id=group_id,
            user=request.user,
        )

        if group is None:
            raise GroupNotFound()

        statistics = GroupSelector.get_group_statistics(
            group=group,
        )

        return success(
            data=GroupDetailSerializer(
                group,
                context={
                    "statistics": statistics,
                    "user": request.user,
                },
            ).data
        )

    def delete(self, request, group_id):

        group = GroupService.archive_group(
            group_id=group_id,
            archived_by=request.user,
        )

        return success(
            data=GroupSerializer(
                group,
                context={"user": request.user},
            ).data,
            message="Group archived successfully.",
        )

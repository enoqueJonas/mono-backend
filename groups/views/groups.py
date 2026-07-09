from core.exceptions import DomainException
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import success
from groups.serializers.create_group import CreateGroupSerializer
from groups.serializers.group import GroupSerializer
from groups.services.group_service import GroupService
from groups.selectors.group_selector import GroupSelector


class GroupListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        groups = GroupSelector.list_user_groups(user=request.user)
        return success(
            data=GroupSerializer(groups, many=True).data
        )

    def post(self, request):

        serializer = CreateGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = GroupService.create_group(
            created_by=request.user,
            data=serializer.validated_data,
        )

        return success(
            data=GroupSerializer(group).data,
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

        return success(
            data=GroupSerializer(group).data
        )

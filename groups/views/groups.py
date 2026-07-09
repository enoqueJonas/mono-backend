from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import success
from groups.serializers.create_group import CreateGroupSerializer
from groups.serializers.group import GroupSerializer
from groups.services.group_service import GroupService


class GroupListCreateView(APIView):
    permission_classes = [IsAuthenticated]

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

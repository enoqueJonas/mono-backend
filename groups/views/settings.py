from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import success
from groups.serializers.group import GroupSettingsSerializer
from groups.serializers.update_group_settings import (
    UpdateGroupSettingsSerializer,
)
from groups.services.group_service import GroupService


class GroupSettingsUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, group_id):
        serializer = UpdateGroupSettingsSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        settings = GroupService.update_settings(
            group_id=group_id,
            updated_by=request.user,
            data=serializer.validated_data,
        )

        return success(
            data=GroupSettingsSerializer(settings).data,
            message="Group settings updated successfully.",
        )

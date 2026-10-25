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


class GroupSettingsIntegrityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id, version):
        from django.shortcuts import get_object_or_404
        from blockchain.services.group_anchor_service import GroupAnchorService
        from groups.models import GroupSettings
        from groups.services.group_member_service import GroupMemberService

        GroupMemberService.ensure_active_member(group_id=group_id, user=request.user)
        group_settings = get_object_or_404(GroupSettings, group_id=group_id, version=version)
        return success(data=GroupAnchorService().verify_integrity(group_settings))

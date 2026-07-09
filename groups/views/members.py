from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import success
from groups.models import GroupMember
from groups.serializers.add_member import AddGroupMemberSerializer
from groups.serializers.group_member import GroupMemberSerializer
from groups.services.group_member_service import GroupMemberService
from groups.services.group_service import GroupService


class GroupMemberListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        GroupMemberService.ensure_active_member(
            group_id=group_id,
            user=request.user,
        )

        members = GroupMember.objects.select_related("user").filter(
            group_id=group_id
        ).order_by("joined_at")

        return success(
            data=GroupMemberSerializer(members, many=True).data
        )

    def post(self, request, group_id):
        serializer = AddGroupMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        member = GroupService.add_member(
            group_id=group_id,
            added_by=request.user,
            phone_number=serializer.validated_data["phone_number"],
        )

        return success(
            data=GroupMemberSerializer(member).data,
            message="Member added successfully.",
            status_code=201,
        )

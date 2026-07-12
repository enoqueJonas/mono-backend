from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import success
from groups.services.group_member_service import GroupMemberService
from identity.models import GroupDID
from identity.serializers.group_did import GroupDIDSerializer
from identity.services.did_service import DIDNotFound, DIDService


class GroupDIDView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        GroupMemberService.ensure_active_member(
            group_id=group_id,
            user=request.user,
        )

        identity = GroupDID.objects.filter(
            group_id=group_id,
        ).first()

        if identity is None:
            raise DIDNotFound()

        return success(
            data=GroupDIDSerializer(identity).data,
        )


class GroupDIDDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        GroupMemberService.ensure_active_member(
            group_id=group_id,
            user=request.user,
        )

        identity = GroupDID.objects.filter(
            group_id=group_id,
        ).first()

        if identity is None:
            raise DIDNotFound()

        return success(
            data=DIDService.build_document(
                identity=identity,
            )
        )

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from credentials.application.services.revoke_credential_service import (
    RevokeCredentialService,
)
from credentials.models import VerifiableCredential
from credentials.serializers.revoke_credential import RevokeCredentialSerializer
from groups.services.group_service import GroupService


class RevokeCredentialView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, credential_id):
        serializer = RevokeCredentialSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        credential_to_revoke = VerifiableCredential.objects.select_related(
            "group_member__group",
        ).get(id=credential_id)
        GroupService.ensure_manager(
            group_id=credential_to_revoke.group_member.group_id,
            user=request.user,
        )

        credential = RevokeCredentialService().revoke(
            credential_id=credential_id,
            reason=serializer.validated_data["reason"],
        )
        return Response(
            {
                "message": "Credential revoked successfully.",
                "data": {
                    "credential_id": credential.id,
                    "status": credential.status,
                    "revoked_at": credential.revoked_at,
                },
            },
            status=status.HTTP_200_OK,
        )

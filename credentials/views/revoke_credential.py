from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from credentials.application.services.revoke_credential_service import (
    RevokeCredentialService,
)
from credentials.serializers.revoke_credential import (
    RevokeCredentialSerializer,
)


class RevokeCredentialView(APIView):
    def post(
        self,
        request,
        credential_id,
    ):
        serializer = (
            RevokeCredentialSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        credential = (
            RevokeCredentialService().revoke(
                credential_id=credential_id,
                reason=serializer.validated_data[
                    "reason"
                ],
            )
        )

        return Response(
            {
                "message": (
                    "Credential revoked successfully."
                ),
                "data": {
                    "credential_id": credential.id,
                    "status": credential.status,
                    "revoked_at": credential.revoked_at,
                },
            },
            status=status.HTTP_200_OK,
        )

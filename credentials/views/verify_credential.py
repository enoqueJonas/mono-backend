from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from credentials.application.services.verify_credential_service import (
    VerifyCredentialService,
)
from credentials.serializers.verify_credential import (
    VerifyCredentialSerializer,
)


class VerifyCredentialView(APIView):
    def post(self, request):
        serializer = VerifyCredentialSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True,
        )

        valid = VerifyCredentialService().verify(
            credential=serializer.validated_data[
                "credential"
            ],
        )

        return Response(
            {
                "message": "Credential verification completed.",
                "data": {
                    "valid": valid,
                },
            },
            status=status.HTTP_200_OK,
        )

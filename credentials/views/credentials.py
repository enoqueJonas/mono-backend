from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import success
from credentials.exceptions import CredentialNotFound
from credentials.selectors.credential_selector import (
    CredentialSelector,
)
from credentials.serializers.verifiable_credential import (
    VerifiableCredentialSerializer,
)


class MyCredentialListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        credentials = CredentialSelector.list_for_holder(
            user=request.user,
        )

        return success(
            data=VerifiableCredentialSerializer(
                credentials,
                many=True,
            ).data
        )


class CredentialDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, credential_id):
        credential = (
            CredentialSelector.get_accessible_credential(
                credential_id=credential_id,
                user=request.user,
            )
        )

        if credential is None:
            raise CredentialNotFound()

        return success(
            data=VerifiableCredentialSerializer(
                credential
            ).data
        )

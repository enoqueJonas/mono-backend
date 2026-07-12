from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import success
from identity.selectors.user_did_selector import UserDIDSelector
from identity.serializers.user_did import UserDIDSerializer
from identity.services.did_service import DIDNotFound, DIDService


class MyDIDView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        identity = UserDIDSelector.get_for_user(
            user=request.user,
        )

        if identity is None:
            raise DIDNotFound()

        return success(
            data=UserDIDSerializer(identity).data,
        )


class MyDIDDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        identity = UserDIDSelector.get_for_user(
            user=request.user,
        )

        if identity is None:
            raise DIDNotFound()

        document = DIDService.build_document(
            identity=identity,
        )

        return success(
            data=document,
        )

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import success
from credentials.serializers.issue_credential import (
    IssueContributionCredentialSerializer,
)
from credentials.serializers.verifiable_credential import (
    VerifiableCredentialSerializer,
)
from credentials.services.credential_service import (
    CredentialService,
)


class GroupCredentialIssueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        serializer = (
            IssueContributionCredentialSerializer(
                data=request.data
            )
        )

        serializer.is_valid(raise_exception=True)

        credential = CredentialService.issue_for_group(
            group_id=group_id,
            group_member_id=(
                serializer.validated_data[
                    "group_member_id"
                ]
            ),
            issued_by_user=request.user,
            period_start=(
                serializer.validated_data[
                    "period_start"
                ]
            ),
            period_end=(
                serializer.validated_data[
                    "period_end"
                ]
            ),
        )

        return success(
            data=VerifiableCredentialSerializer(
                credential
            ).data,
            message=(
                "Verifiable credential issued successfully."
            ),
            status_code=201,
        )

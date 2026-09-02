from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from contributions.serializers.contribution import (
    ContributionSerializer,
)
from contributions.services.contribution_service import (
    ContributionService,
)
from core.responses import success
from wallets.serializers import (
    MobileWalletContributionSerializer,
)


class MobileWalletContributionWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = (
            MobileWalletContributionSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        contribution = (
            ContributionService
            .register_mobile_wallet_contribution(
                data=serializer.validated_data,
            )
        )

        return success(
            data=ContributionSerializer(
                contribution
            ).data,
            message=(
                "Mobile wallet contribution "
                "registered successfully."
            ),
            status_code=201,
        )

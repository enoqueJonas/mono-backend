import hashlib
import hmac
import time

from django.conf import settings
from rest_framework.exceptions import NotFound, PermissionDenied
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
        self._authenticate_simulated_provider(request)
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

    @staticmethod
    def _authenticate_simulated_provider(request):
        # This is an authenticated simulation protocol, not a real M-Pesa/e-Mola
        # provider contract. Disabled by default and not deployed as a public
        # payment-confirmation endpoint.
        if not getattr(settings, "MOBILE_WALLET_WEBHOOK_ENABLED", False):
            raise NotFound("Mobile wallet simulation is disabled.")

        secret = getattr(settings, "MOBILE_WALLET_WEBHOOK_SECRET", "")
        timestamp = request.headers.get("X-Mono-Timestamp", "")
        provided_signature = request.headers.get("X-Mono-Signature", "")
        if not secret or not timestamp.isdecimal() or not provided_signature:
            raise PermissionDenied("Invalid wallet callback authentication.")

        # Short window limits, but does not eliminate, replay opportunities.
        # The contribution reference is additionally unique in the DB.
        try:
            sent_at = int(timestamp)
        except ValueError as exc:
            raise PermissionDenied("Invalid wallet callback timestamp.") from exc

        if abs(time.time() - sent_at) > 300:
            raise PermissionDenied("Expired wallet callback timestamp.")

        payload = timestamp.encode("ascii") + b"." + request.body
        expected = hmac.new(
            secret.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(provided_signature, expected):
            raise PermissionDenied("Invalid wallet callback authentication.")

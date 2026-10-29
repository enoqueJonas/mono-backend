import hashlib
import hmac
import json
import time
from decimal import Decimal
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from contributions.models import Contribution
from groups.models import (
    Group,
    GroupMember,
    GroupSettings,
)


@override_settings(
    MOBILE_WALLET_WEBHOOK_ENABLED=True,
    MOBILE_WALLET_WEBHOOK_SECRET="test-secret-not-for-production",
)
class MobileWalletWebhookAPITests(APITestCase):

    def setUp(self):
        # Mock only the blockchain boundary in these API-level tests.
        self.anchor_patcher = patch(
            "contributions.services.contribution_service.ContributionAnchorService"
        )
        self.mock_anchor_service = self.anchor_patcher.start()
        self.addCleanup(self.anchor_patcher.stop)

        self.user = User.objects.create_user(
            phone_number="+258843030303",
            password="test1234",
        )

        self.group = Group.objects.create(
            name="Grupo Wallet API",
        )

        self.settings = GroupSettings.objects.create(
            group=self.group,
            version=1,
            contribution_amount=Decimal(
                "1000.00"
            ),
            currency="MZN",
            contribution_frequency=(
                GroupSettings
                .ContributionFrequency
                .MONTHLY
            ),
            maximum_members=10,
            rotation_strategy=(
                GroupSettings
                .RotationStrategy
                .FIXED_ORDER
            ),
            requires_consensus=False,
            allow_manual_contributions=True,
            is_active=True,
        )

        self.member = GroupMember.objects.create(
            group=self.group,
            user=self.user,
            role=GroupMember.Role.MEMBER,
            status=GroupMember.Status.ACTIVE,
        )

        self.url = reverse(
            "mobile-wallet-contribution-webhook"
        )

    def payload(self):
        return {
            "group_id": str(self.group.id),
            "group_member_id": str(
                self.member.id
            ),
            "amount": "1000.00",
            "currency": "MZN",
            "contribution_period": (
                "2026-09-01"
            ),
            "reference": "WALLET-API-001",
        }

    def signed_post(self, payload, *, timestamp=None, secret="test-secret-not-for-production"):
        raw = json.dumps(
            payload, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        stamp = str(int(time.time())) if timestamp is None else str(timestamp)
        signature = hmac.new(
            secret.encode("utf-8"), stamp.encode("ascii") + b"." + raw,
            hashlib.sha256,
        ).hexdigest()
        return self.client.post(
            self.url, raw, content_type="application/json",
            HTTP_X_MONO_TIMESTAMP=stamp,
            HTTP_X_MONO_SIGNATURE=signature,
        )

    def test_wallet_can_register_contribution(
        self,
    ):
        response = self.signed_post(self.payload())

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        contribution = Contribution.objects.get(
            reference="WALLET-API-001"
        )

        self.assertEqual(
            contribution.source,
            Contribution.Source.MOBILE_WALLET,
        )

        self.assertEqual(
            contribution.status,
            Contribution.Status.CONFIRMED,
        )

        self.mock_anchor_service.return_value.anchor.assert_called_once_with(
            contribution
        )

        self.assertEqual(
            response.data["data"]["reference"],
            "WALLET-API-001",
        )

    def test_wallet_rejects_invalid_amount(self):
        payload = self.payload()
        payload["amount"] = "500.00"

        response = self.signed_post(payload)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            Contribution.objects.exists()
        )

    def test_wallet_rejects_invalid_currency(
        self,
    ):
        payload = self.payload()
        payload["currency"] = "USD"

        response = self.signed_post(payload)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            Contribution.objects.exists()
        )

    def test_wallet_rejects_duplicate_reference(
        self,
    ):
        payload = self.payload()

        first_response = self.signed_post(payload)

        second_response = self.signed_post(payload)

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Contribution.objects.count(),
            1,
        )

    def test_wallet_requires_mandatory_fields(
        self,
    ):
        response = self.signed_post({
                "reference": "WALLET-API-002",
            })

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            Contribution.objects.exists()
        )

    def test_wallet_rejects_unsigned_confirmation(self):
        response = self.client.post(
            self.url, self.payload(), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Contribution.objects.exists())

    def test_wallet_rejects_wrong_signature(self):
        response = self.signed_post(self.payload(), secret="wrong-secret")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Contribution.objects.exists())

    def test_wallet_rejects_stale_timestamp(self):
        response = self.signed_post(
            self.payload(), timestamp=int(time.time()) - 700
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Contribution.objects.exists())

    @override_settings(MOBILE_WALLET_WEBHOOK_ENABLED=False)
    def test_wallet_disabled_by_default(self):
        response = self.signed_post(self.payload())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Contribution.objects.exists())

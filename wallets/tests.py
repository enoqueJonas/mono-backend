from decimal import Decimal

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


class MobileWalletWebhookAPITests(APITestCase):

    def setUp(self):
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

    def test_wallet_can_register_contribution(
        self,
    ):
        response = self.client.post(
            self.url,
            self.payload(),
            format="json",
        )

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

        self.assertEqual(
            response.data["data"]["reference"],
            "WALLET-API-001",
        )

    def test_wallet_rejects_invalid_amount(self):
        payload = self.payload()
        payload["amount"] = "500.00"

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

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

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

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

        first_response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        second_response = self.client.post(
            self.url,
            payload,
            format="json",
        )

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
        response = self.client.post(
            self.url,
            {
                "reference": "WALLET-API-002",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            Contribution.objects.exists()
        )

from contributions.services.contribution_service import (
    ContributionService,
    DuplicateContribution,
    DuplicateContributionReference,
    InactiveMember,
    InvalidContributionAmount,
    InvalidContributionCurrency,
    MemberNotFound,
)

from decimal import Decimal

from django.test import TestCase

from accounts.models import User
from contributions.models import Contribution
from contributions.services.contribution_service import (
    ContributionService,
    DuplicateContribution,
    DuplicateContributionReference,
    InactiveMember,
    InvalidContributionAmount,
    InvalidContributionCurrency,
    MemberNotFound,
)
from groups.models import (
    Group,
    GroupMember,
    GroupSettings,
)


class MobileWalletContributionServiceTests(TestCase):

    def setUp(self):
        self.member_user = User.objects.create_user(
            phone_number="+258841010101",
            password="test1234",
        )

        self.other_user = User.objects.create_user(
            phone_number="+258842020202",
            password="test1234",
        )

        self.group = Group.objects.create(
            name="Grupo Wallet",
        )

        self.settings = GroupSettings.objects.create(
            group=self.group,
            version=1,
            contribution_amount=Decimal("1000.00"),
            currency="MZN",
            contribution_frequency=(
                GroupSettings.ContributionFrequency.MONTHLY
            ),
            maximum_members=10,
            rotation_strategy=(
                GroupSettings.RotationStrategy.FIXED_ORDER
            ),
            requires_consensus=False,
            allow_manual_contributions=True,
            is_active=True,
        )

        self.member = GroupMember.objects.create(
            group=self.group,
            user=self.member_user,
            role=GroupMember.Role.MEMBER,
            status=GroupMember.Status.ACTIVE,
        )

        self.other_group = Group.objects.create(
            name="Outro Grupo Wallet",
        )

        self.other_member = GroupMember.objects.create(
            group=self.other_group,
            user=self.other_user,
            role=GroupMember.Role.MEMBER,
            status=GroupMember.Status.ACTIVE,
        )

    def test_register_mobile_wallet_contribution(self):
        contribution = (
            ContributionService
            .register_mobile_wallet_contribution(
                data={
                    "group_id": self.group.id,
                    "group_member_id": self.member.id,
                    "amount": "1000.00",
                    "currency": "MZN",
                    "contribution_period": "2026-09-01",
                    "reference": "WALLET-001",
                }
            )
        )

        self.assertEqual(
            contribution.member,
            self.member,
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
            contribution.reference,
            "WALLET-001",
        )

    def test_mobile_wallet_rejects_invalid_amount(self):
        with self.assertRaises(
            InvalidContributionAmount
        ):
            ContributionService.register_mobile_wallet_contribution(
                data={
                    "group_id": self.group.id,
                    "group_member_id": self.member.id,
                    "amount": "500.00",
                    "currency": "MZN",
                    "contribution_period": "2026-09-01",
                    "reference": "WALLET-002",
                }
            )

    def test_mobile_wallet_rejects_invalid_currency(self):
        with self.assertRaises(
            InvalidContributionCurrency
        ):
            ContributionService.register_mobile_wallet_contribution(
                data={
                    "group_id": self.group.id,
                    "group_member_id": self.member.id,
                    "amount": "1000.00",
                    "currency": "USD",
                    "contribution_period": "2026-09-01",
                    "reference": "WALLET-003",
                }
            )

    def test_mobile_wallet_rejects_member_from_other_group(
        self,
    ):
        with self.assertRaises(
            MemberNotFound
        ):
            ContributionService.register_mobile_wallet_contribution(
                data={
                    "group_id": self.group.id,
                    "group_member_id": (
                        self.other_member.id
                    ),
                    "amount": "1000.00",
                    "currency": "MZN",
                    "contribution_period": "2026-09-01",
                    "reference": "WALLET-004",
                }
            )

    def test_mobile_wallet_rejects_inactive_member(self):
        self.member.status = (
            GroupMember.Status.SUSPENDED
        )
        self.member.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        with self.assertRaises(
            InactiveMember
        ):
            ContributionService.register_mobile_wallet_contribution(
                data={
                    "group_id": self.group.id,
                    "group_member_id": self.member.id,
                    "amount": "1000.00",
                    "currency": "MZN",
                    "contribution_period": "2026-09-01",
                    "reference": "WALLET-005",
                }
            )

    def test_mobile_wallet_rejects_duplicate_reference(
        self,
    ):
        data = {
            "group_id": self.group.id,
            "group_member_id": self.member.id,
            "amount": "1000.00",
            "currency": "MZN",
            "contribution_period": "2026-09-01",
            "reference": "WALLET-006",
        }

        ContributionService.register_mobile_wallet_contribution(
            data=data
        )

        with self.assertRaises(
            DuplicateContributionReference
        ):
            ContributionService.register_mobile_wallet_contribution(
                data=data
            )

    def test_mobile_wallet_rejects_duplicate_member_period(
        self,
    ):
        ContributionService.register_mobile_wallet_contribution(
            data={
                "group_id": self.group.id,
                "group_member_id": self.member.id,
                "amount": "1000.00",
                "currency": "MZN",
                "contribution_period": "2026-09-01",
                "reference": "WALLET-007",
            }
        )

        with self.assertRaises(
            DuplicateContribution
        ):
            ContributionService.register_mobile_wallet_contribution(
                data={
                    "group_id": self.group.id,
                    "group_member_id": self.member.id,
                    "amount": "1000.00",
                    "currency": "MZN",
                    "contribution_period": "2026-09-01",
                    "reference": "WALLET-008",
                }
            )

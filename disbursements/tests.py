from datetime import date
from decimal import Decimal

from django.test import TestCase

from accounts.models import User
from contributions.models import Contribution
from disbursements.models import Disbursement
from disbursements.services.disbursement_service import (
    ArchivedGroup,
    DisbursementAlreadyExists,
    DisbursementService,
    InactiveBeneficiary,
    IncompleteContributions,
    NoConfirmedContributions,
)
from groups.models import (
    Group,
    GroupMember,
    GroupSettings,
    RotationOrder,
)


class DisbursementServiceTests(TestCase):

    def setUp(self):
        self.manager_user = User.objects.create_user(
            phone_number="+258841111111",
            password="testpass123",
        )

        self.member_user = User.objects.create_user(
            phone_number="+258842222222",
            password="testpass123",
        )

        self.group = Group.objects.create(
            name="Grupo Teste",
        )

        self.settings = GroupSettings.objects.create(
            group=self.group,
            version=1,
            contribution_amount=Decimal("1000.00"),
            currency="MZN",
            contribution_frequency=(
                GroupSettings.ContributionFrequency.MONTHLY
            ),
            maximum_members=2,
            rotation_strategy=(
                GroupSettings.RotationStrategy.FIXED_ORDER
            ),
            requires_consensus=False,
            allow_manual_contributions=True,
            is_active=True,
        )

        self.manager = GroupMember.objects.create(
            group=self.group,
            user=self.manager_user,
            role=GroupMember.Role.MANAGER,
            status=GroupMember.Status.ACTIVE,
        )

        self.member = GroupMember.objects.create(
            group=self.group,
            user=self.member_user,
            role=GroupMember.Role.MEMBER,
            status=GroupMember.Status.ACTIVE,
        )

        self.period = date(2026, 9, 1)

        self.rotation = RotationOrder.objects.create(
            group=self.group,
            member=self.member,
            group_settings=self.settings,
            contribution_period=self.period,
            cycle_number=1,
            position=1,
            status=RotationOrder.Status.CURRENT,
        )

    def create_confirmed_contributions(self):
        Contribution.objects.create(
            member=self.manager,
            group_settings=self.settings,
            amount=Decimal("1000.00"),
            currency="MZN",
            source=Contribution.Source.MANUAL,
            status=Contribution.Status.CONFIRMED,
            contribution_period=self.period,
            reference="MAN-001",
        )

        Contribution.objects.create(
            member=self.member,
            group_settings=self.settings,
            amount=Decimal("1000.00"),
            currency="MZN",
            source=Contribution.Source.MANUAL,
            status=Contribution.Status.CONFIRMED,
            contribution_period=self.period,
            reference="MAN-002",
        )

    def test_create_disbursement(self):
        self.create_confirmed_contributions()

        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        self.assertEqual(
            disbursement.group,
            self.group,
        )
        self.assertEqual(
            disbursement.beneficiary,
            self.member,
        )
        self.assertEqual(
            disbursement.rotation_order,
            self.rotation,
        )
        self.assertEqual(
            disbursement.group_settings,
            self.settings,
        )
        self.assertEqual(
            disbursement.amount,
            Decimal("2000.00"),
        )
        self.assertEqual(
            disbursement.currency,
            "MZN",
        )
        self.assertEqual(
            disbursement.status,
            Disbursement.Status.APPROVED,
        )

    def test_disbursement_uses_exact_rotation_settings_version(self):
        self.create_confirmed_contributions()

        GroupSettings.objects.create(
            group=self.group,
            version=2,
            contribution_amount=Decimal("1500.00"),
            currency="MZN",
            contribution_frequency=(
                GroupSettings.ContributionFrequency.MONTHLY
            ),
            maximum_members=2,
            rotation_strategy=(
                GroupSettings.RotationStrategy.FIXED_ORDER
            ),
            requires_consensus=True,
            allow_manual_contributions=True,
            is_active=False,
        )

        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        self.assertEqual(
            disbursement.group_settings,
            self.settings,
        )
        self.assertEqual(
            disbursement.amount,
            Decimal("2000.00"),
        )
        self.assertEqual(
            disbursement.status,
            Disbursement.Status.APPROVED,
        )

    def test_requires_all_active_members_to_have_confirmed_contribution(self):
        Contribution.objects.create(
            member=self.member,
            group_settings=self.settings,
            amount=Decimal("1000.00"),
            currency="MZN",
            source=Contribution.Source.MANUAL,
            status=Contribution.Status.CONFIRMED,
            contribution_period=self.period,
            reference="MAN-001",
        )

        with self.assertRaises(
            IncompleteContributions
        ):
            DisbursementService.create(
                group_id=self.group.id,
                cycle_number=1,
            )

    def test_rejects_when_no_confirmed_contributions_exist(self):
        with self.assertRaises(
            NoConfirmedContributions
        ):
            DisbursementService.create(
                group_id=self.group.id,
                cycle_number=1,
            )

    def test_rejects_duplicate_disbursement_for_same_rotation(self):
        self.create_confirmed_contributions()

        DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        with self.assertRaises(
            DisbursementAlreadyExists
        ):
            DisbursementService.create(
                group_id=self.group.id,
                cycle_number=1,
            )

    def test_rejects_inactive_beneficiary(self):
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
            InactiveBeneficiary
        ):
            DisbursementService.create(
                group_id=self.group.id,
                cycle_number=1,
            )

    def test_rejects_archived_group(self):
        self.group.status = Group.Status.ARCHIVED
        self.group.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        with self.assertRaises(
            ArchivedGroup
        ):
            DisbursementService.create(
                group_id=self.group.id,
                cycle_number=1,
            )

    def test_requires_consensus_when_group_settings_require_it(self):
        self.settings.requires_consensus = True
        self.settings.save(
            update_fields=[
                "requires_consensus",
                "updated_at",
            ]
        )

        self.create_confirmed_contributions()

        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        self.assertEqual(
            disbursement.status,
            Disbursement.Status.AWAITING_CONSENSUS,
        )

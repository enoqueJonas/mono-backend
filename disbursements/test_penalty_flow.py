from datetime import date
from decimal import Decimal

from django.test import TestCase

from accounts.models import User
from contributions.models import Contribution
from disbursements.models import Disbursement
from disbursements.services.disbursement_service import (
    ActivePenalty,
    DisbursementService,
)
from groups.models import (
    Group,
    GroupMember,
    GroupSettings,
    RotationOrder,
)
from penalties.services import PenaltyService


class DisbursementPenaltyFlowTests(TestCase):
    def setUp(self):
        self.manager_user = User.objects.create_user(
            phone_number="+258846666666",
            password="testpass123",
        )
        self.member_user = User.objects.create_user(
            phone_number="+258847777777",
            password="testpass123",
        )

        self.group = Group.objects.create(
            name="Grupo Penalizações",
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
            requires_consensus=True,
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

        self.period = date(2026, 9, 4)
        self.rotation = RotationOrder.objects.create(
            group=self.group,
            member=self.member,
            group_settings=self.settings,
            contribution_period=self.period,
            cycle_number=1,
            position=1,
            status=RotationOrder.Status.CURRENT,
        )

        Contribution.objects.create(
            member=self.manager,
            group_settings=self.settings,
            amount=Decimal("1000.00"),
            currency="MZN",
            source=Contribution.Source.MANUAL,
            status=Contribution.Status.CONFIRMED,
            contribution_period=self.period,
            reference="PEN-MAN-001",
        )
        Contribution.objects.create(
            member=self.member,
            group_settings=self.settings,
            amount=Decimal("1000.00"),
            currency="MZN",
            source=Contribution.Source.MANUAL,
            status=Contribution.Status.CONFIRMED,
            contribution_period=self.period,
            reference="PEN-MAN-002",
        )

    def test_active_penalty_added_after_creation_blocks_approval(self):
        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        self.assertEqual(
            disbursement.status,
            Disbursement.Status.AWAITING_CONSENSUS,
        )

        PenaltyService.create(
            member=self.member,
            reason="Incumprimento das regras do grupo",
        )

        with self.assertRaises(ActivePenalty):
            DisbursementService.approve(
                disbursement_id=disbursement.id,
                approved_by=self.manager_user,
            )

        disbursement.refresh_from_db()
        self.assertEqual(
            disbursement.status,
            Disbursement.Status.AWAITING_CONSENSUS,
        )

    def test_active_penalty_added_after_approval_blocks_completion(self):
        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        approved = DisbursementService.approve(
            disbursement_id=disbursement.id,
            approved_by=self.manager_user,
        )
        self.assertEqual(
            approved.status,
            Disbursement.Status.APPROVED,
        )

        PenaltyService.create(
            member=self.member,
            reason="Incumprimento das regras do grupo",
        )

        with self.assertRaises(ActivePenalty):
            DisbursementService.complete(
                disbursement_id=disbursement.id,
                completed_by=self.manager_user,
            )

        disbursement.refresh_from_db()
        self.rotation.refresh_from_db()

        self.assertEqual(
            disbursement.status,
            Disbursement.Status.APPROVED,
        )
        self.assertEqual(
            self.rotation.status,
            RotationOrder.Status.CURRENT,
        )

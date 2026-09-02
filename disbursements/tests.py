import uuid
from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from contributions.models import Contribution
from disbursements.models import Disbursement
from disbursements.services.disbursement_service import (
    ArchivedGroup,
    DisbursementAlreadyExists,
    DisbursementNotFound,
    DisbursementService,
    InactiveBeneficiary,
    IncompleteContributions,
    InvalidDisbursementStatus,
    NoConfirmedContributions,
)
from groups.models import (
    Group,
    GroupMember,
    GroupSettings,
    RotationOrder,
)
from groups.services.group_service import NotGroupManager
from disbursements.services.disbursement_service import (
    ActivePenalty,
    # ... restantes imports existentes
)
from penalties.services import PenaltyService


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

    def test_cannot_create_disbursement_with_active_penalty(
        self,
    ):
        self.create_confirmed_contributions()

        PenaltyService.create(
            member=self.member,
            reason="Late contribution.",
        )

        with self.assertRaises(ActivePenalty):
            DisbursementService.create(
                group_id=self.group.id,
                cycle_number=1,
            )

        self.assertFalse(
            Disbursement.objects.filter(
                group=self.group,
                cycle_number=1,
            ).exists()
        )

    def test_resolved_penalty_does_not_block_disbursement(
        self,
    ):
        self.create_confirmed_contributions()

        penalty = PenaltyService.create(
            member=self.member,
            reason="Late contribution.",
        )

        PenaltyService.resolve(
            penalty_id=penalty.id,
        )

        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        self.assertEqual(
            disbursement.beneficiary,
            self.member,
        )

        self.assertEqual(
            disbursement.status,
            Disbursement.Status.APPROVED,
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

    def test_requires_all_active_members_to_have_confirmed_contribution(
        self,
    ):
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

    def test_rejects_duplicate_disbursement_for_same_rotation(
        self,
    ):
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

    def test_requires_consensus_when_group_settings_require_it(
        self,
    ):
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

    def test_approve_disbursement_awaiting_consensus(self):
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

        approved = DisbursementService.approve(
            disbursement_id=disbursement.id,
            approved_by=self.manager_user,
        )

        self.assertEqual(
            approved.status,
            Disbursement.Status.APPROVED,
        )

    def test_cannot_approve_already_approved_disbursement(
        self,
    ):
        self.create_confirmed_contributions()

        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        self.assertEqual(
            disbursement.status,
            Disbursement.Status.APPROVED,
        )

        with self.assertRaises(
            InvalidDisbursementStatus
        ):
            DisbursementService.approve(
                disbursement_id=disbursement.id,
                approved_by=self.manager_user,
            )

    def test_regular_member_cannot_approve_disbursement(
        self,
    ):
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

        with self.assertRaises(
            NotGroupManager
        ):
            DisbursementService.approve(
                disbursement_id=disbursement.id,
                approved_by=self.member_user,
            )

    def test_cannot_approve_nonexistent_disbursement(self):
        with self.assertRaises(
            DisbursementNotFound
        ):
            DisbursementService.approve(
                disbursement_id=uuid.uuid4(),
                approved_by=self.manager_user,
            )

    def test_complete_approved_disbursement(self):
        self.create_confirmed_contributions()

        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        completed = DisbursementService.complete(
            disbursement_id=disbursement.id,
            completed_by=self.manager_user,
        )

        self.assertEqual(
            completed.status,
            Disbursement.Status.COMPLETED,
        )

        self.assertIsNotNone(
            completed.completed_at,
        )

        self.rotation.refresh_from_db()

        self.assertEqual(
            self.rotation.status,
            RotationOrder.Status.COMPLETED,
        )

    def test_complete_disbursement_advances_rotation(self):
        next_rotation = RotationOrder.objects.create(
            group=self.group,
            member=self.manager,
            group_settings=self.settings,
            contribution_period=self.period,
            cycle_number=1,
            position=2,
            status=RotationOrder.Status.PENDING,
        )

        self.create_confirmed_contributions()

        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        DisbursementService.complete(
            disbursement_id=disbursement.id,
            completed_by=self.manager_user,
        )

        self.rotation.refresh_from_db()
        next_rotation.refresh_from_db()

        self.assertEqual(
            self.rotation.status,
            RotationOrder.Status.COMPLETED,
        )

        self.assertEqual(
            next_rotation.status,
            RotationOrder.Status.CURRENT,
        )

    def test_cannot_complete_disbursement_awaiting_consensus(
        self,
    ):
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

        with self.assertRaises(
            InvalidDisbursementStatus
        ):
            DisbursementService.complete(
                disbursement_id=disbursement.id,
                completed_by=self.manager_user,
            )

    def test_regular_member_cannot_complete_disbursement(
        self,
    ):
        self.create_confirmed_contributions()

        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        with self.assertRaises(
            NotGroupManager
        ):
            DisbursementService.complete(
                disbursement_id=disbursement.id,
                completed_by=self.member_user,
            )


class DisbursementAPITests(APITestCase):

    def setUp(self):
        self.manager_user = User.objects.create_user(
            phone_number="+258843333333",
            password="testpass123",
        )

        self.member_user = User.objects.create_user(
            phone_number="+258844444444",
            password="testpass123",
        )

        self.outsider_user = User.objects.create_user(
            phone_number="+258845555555",
            password="testpass123",
        )

        self.group = Group.objects.create(
            name="Grupo API",
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

        Contribution.objects.create(
            member=self.manager,
            group_settings=self.settings,
            amount=Decimal("1000.00"),
            currency="MZN",
            source=Contribution.Source.MANUAL,
            status=Contribution.Status.CONFIRMED,
            contribution_period=self.period,
            reference="API-MAN-001",
        )

        Contribution.objects.create(
            member=self.member,
            group_settings=self.settings,
            amount=Decimal("1000.00"),
            currency="MZN",
            source=Contribution.Source.MANUAL,
            status=Contribution.Status.CONFIRMED,
            contribution_period=self.period,
            reference="API-MAN-002",
        )

        self.list_url = reverse(
            "group-disbursement-list-create",
            kwargs={
                "group_id": self.group.id,
            },
        )

    def test_requires_authentication(self):
        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_active_member_can_list_group_disbursements(
        self,
    ):
        DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        self.client.force_authenticate(
            user=self.member_user,
        )

        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["data"]),
            1,
        )

        self.assertEqual(
            response.data["data"][0]["cycle_number"],
            1,
        )

        self.assertEqual(
            Decimal(
                response.data["data"][0]["amount"]
            ),
            Decimal("2000.00"),
        )

    def test_non_member_cannot_list_group_disbursements(
        self,
    ):
        self.client.force_authenticate(
            user=self.outsider_user,
        )

        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["message"],
            "You are not an active member of this group.",
        )

    def test_manager_can_create_disbursement(self):
        self.client.force_authenticate(
            user=self.manager_user,
        )

        response = self.client.post(
            self.list_url,
            {
                "cycle_number": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Disbursement.objects.count(),
            1,
        )

        disbursement = Disbursement.objects.get()

        self.assertEqual(
            disbursement.beneficiary,
            self.member,
        )

        self.assertEqual(
            disbursement.amount,
            Decimal("2000.00"),
        )

        self.assertEqual(
            response.data["data"]["status"],
            Disbursement.Status.APPROVED,
        )

    def test_regular_member_cannot_create_disbursement(
        self,
    ):
        self.client.force_authenticate(
            user=self.member_user,
        )

        response = self.client.post(
            self.list_url,
            {
                "cycle_number": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Disbursement.objects.count(),
            0,
        )

        self.assertEqual(
            response.data["message"],
            "Only group managers can perform this action.",
        )

    def test_cycle_number_is_required(self):
        self.client.force_authenticate(
            user=self.manager_user,
        )

        response = self.client.post(
            self.list_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "cycle_number",
            response.data,
        )

    def test_cycle_number_must_be_greater_than_zero(self):
        self.client.force_authenticate(
            user=self.manager_user,
        )

        response = self.client.post(
            self.list_url,
            {
                "cycle_number": 0,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_active_member_can_retrieve_disbursement(self):
        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        detail_url = reverse(
            "group-disbursement-detail",
            kwargs={
                "group_id": self.group.id,
                "disbursement_id": disbursement.id,
            },
        )

        self.client.force_authenticate(
            user=self.member_user,
        )

        response = self.client.get(
            detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["data"]["id"],
            str(disbursement.id),
        )

        self.assertEqual(
            response.data["data"]["settings_version"],
            1,
        )

        self.assertEqual(
            response.data["data"]["contribution_period"],
            "2026-09-01",
        )

    def test_manager_can_approve_disbursement(self):
        self.settings.requires_consensus = True
        self.settings.save(
            update_fields=[
                "requires_consensus",
                "updated_at",
            ]
        )

        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        approve_url = reverse(
            "group-disbursement-approve",
            kwargs={
                "group_id": self.group.id,
                "disbursement_id": disbursement.id,
            },
        )

        self.client.force_authenticate(
            user=self.manager_user,
        )

        response = self.client.post(
            approve_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        disbursement.refresh_from_db()

        self.assertEqual(
            disbursement.status,
            Disbursement.Status.APPROVED,
        )

        self.assertEqual(
            response.data["data"]["status"],
            Disbursement.Status.APPROVED,
        )

    def test_regular_member_cannot_approve_disbursement_api(self):
        self.settings.requires_consensus = True
        self.settings.save(
            update_fields=[
                "requires_consensus",
                "updated_at",
            ]
        )

        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        approve_url = reverse(
            "group-disbursement-approve",
            kwargs={
                "group_id": self.group.id,
                "disbursement_id": disbursement.id,
            },
        )

        self.client.force_authenticate(
            user=self.member_user,
        )

        response = self.client.post(
            approve_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        disbursement.refresh_from_db()

        self.assertEqual(
            disbursement.status,
            Disbursement.Status.AWAITING_CONSENSUS,
        )

    def test_cannot_approve_already_approved_disbursement_api(
        self,
    ):
        disbursement = DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
        )

        approve_url = reverse(
            "group-disbursement-approve",
            kwargs={
                "group_id": self.group.id,
                "disbursement_id": disbursement.id,
            },
        )

        self.client.force_authenticate(
            user=self.manager_user,
        )

        response = self.client.post(
            approve_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

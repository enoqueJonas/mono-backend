from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from contributions.models import Contribution
from disbursements.models import Disbursement, DisbursementApproval
from disbursements.services.disbursement_service import (
    DisbursementService,
    DuplicateDisbursementApproval,
    IneligibleApprover,
    InsufficientDisbursementApprovals,
    InsufficientEligibleApprovers,
    IncompleteContributions,
)
from groups.models import Group, GroupMember, GroupSettings, RotationOrder
from groups.serializers.create_group import CreateGroupSettingsSerializer
from groups.serializers.update_group_settings import UpdateGroupSettingsSerializer
from groups.services.group_service import GroupService
from core.exceptions import DomainException


class IndependentDisbursementApprovalTests(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user(
                phone_number=f"+25884177000{i}", password="testpass123"
            )
            for i in range(5)
        ]
        self.manager, self.beneficiary, self.voter1, self.voter2, self.outsider = self.users
        self.group = Group.objects.create(name="Grupo RN06")
        self.settings = GroupSettings.objects.create(
            group=self.group,
            version=1,
            contribution_amount=Decimal("1000.00"),
            currency="MZN",
            contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
            maximum_members=6,
            rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
            requires_consensus=False,  # Legacy toggle must not bypass approvals.
            allow_manual_contributions=True,
            is_active=True,
        )
        self.members = {}
        for user, role in [
            (self.manager, GroupMember.Role.MANAGER),
            (self.beneficiary, GroupMember.Role.MEMBER),
            (self.voter1, GroupMember.Role.MEMBER),
            (self.voter2, GroupMember.Role.MEMBER),
        ]:
            self.members[user.pk] = GroupMember.objects.create(
                group=self.group, user=user,
                status=GroupMember.Status.ACTIVE, role=role,
            )
        self.period = date(2026, 11, 1)
        self.rotation = RotationOrder.objects.create(
            group=self.group,
            member=self.members[self.beneficiary.pk],
            group_settings=self.settings,
            contribution_period=self.period,
            cycle_number=1,
            position=1,
            status=RotationOrder.Status.CURRENT,
        )
        for i, membership in enumerate(self.members.values()):
            Contribution.objects.create(
                member=membership,
                group_settings=self.settings,
                amount=Decimal("1000.00"),
                currency="MZN",
                source=Contribution.Source.MANUAL,
                status=Contribution.Status.CONFIRMED,
                contribution_period=self.period,
                reference=f"RN06-{i:03}",
            )

    def propose(self):
        return DisbursementService.create(
            group_id=self.group.id,
            cycle_number=1,
            created_by=self.manager,
        )

    def test_legacy_false_toggle_cannot_auto_approve(self):
        disbursement = self.propose()
        self.assertEqual(disbursement.status, Disbursement.Status.AWAITING_CONSENSUS)
        self.assertEqual(disbursement.required_approvals, 2)
        self.assertEqual(len(disbursement.eligible_approver_ids), 2)
        self.assertEqual(disbursement.proposed_by, self.manager)

    def test_two_distinct_independent_members_required(self):
        disbursement = self.propose()
        one = DisbursementService.approve(
            disbursement_id=disbursement.id, approved_by=self.voter1
        )
        self.assertEqual(one.status, Disbursement.Status.AWAITING_CONSENSUS)
        second = DisbursementService.approve(
            disbursement_id=disbursement.id, approved_by=self.voter2
        )
        self.assertEqual(second.status, Disbursement.Status.APPROVED)
        self.assertEqual(disbursement.approvals.count(), 2)
        completed = DisbursementService.complete(
            disbursement_id=disbursement.id, completed_by=self.manager
        )
        self.assertEqual(completed.status, Disbursement.Status.COMPLETED)
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.COMPLETED)

    def test_same_member_cannot_vote_twice(self):
        disbursement = self.propose()
        DisbursementService.approve(
            disbursement_id=disbursement.id, approved_by=self.voter1
        )
        with self.assertRaises(DuplicateDisbursementApproval):
            DisbursementService.approve(
                disbursement_id=disbursement.id, approved_by=self.voter1
            )
        self.assertEqual(disbursement.approvals.count(), 1)

    def test_proposer_beneficiary_and_outsider_cannot_vote(self):
        disbursement = self.propose()
        for user in [self.manager, self.beneficiary, self.outsider]:
            with self.subTest(user_id=user.id):
                with self.assertRaises(IneligibleApprover):
                    DisbursementService.approve(
                        disbursement_id=disbursement.id, approved_by=user
                    )
        self.assertEqual(disbursement.approvals.count(), 0)

    def test_new_member_cannot_join_existing_proposal_approval(self):
        disbursement = self.propose()
        added = User.objects.create_user(
            phone_number="+258849991234", password="testpass123"
        )
        GroupMember.objects.create(
            group=self.group, user=added,
            status=GroupMember.Status.ACTIVE, role=GroupMember.Role.MEMBER,
        )
        with self.assertRaises(IneligibleApprover):
            DisbursementService.approve(
                disbursement_id=disbursement.id, approved_by=added
            )

    def test_legacy_approved_record_without_votes_cannot_be_completed(self):
        disbursement = self.propose()
        disbursement.status = Disbursement.Status.APPROVED
        disbursement.save(update_fields=["status"])
        with self.assertRaises(InsufficientDisbursementApprovals):
            DisbursementService.complete(
                disbursement_id=disbursement.id, completed_by=self.manager
            )
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.CURRENT)

    def test_suspended_voter_invalidates_quorum_before_completion(self):
        disbursement = self.propose()
        for user in (self.voter1, self.voter2):
            DisbursementService.approve(
                disbursement_id=disbursement.id, approved_by=user
            )
        membership = self.members[self.voter2.pk]
        membership.status = GroupMember.Status.SUSPENDED
        membership.save(update_fields=["status", "updated_at"])
        with self.assertRaises(InsufficientDisbursementApprovals):
            DisbursementService.complete(
                disbursement_id=disbursement.id, completed_by=self.manager
            )

    def test_two_member_groups_fail_closed(self):
        self.members[self.voter1.pk].status = GroupMember.Status.LEFT
        self.members[self.voter1.pk].save(update_fields=["status", "updated_at"])
        self.members[self.voter2.pk].status = GroupMember.Status.LEFT
        self.members[self.voter2.pk].save(update_fields=["status", "updated_at"])
        with self.assertRaises(InsufficientEligibleApprovers):
            self.propose()

    def test_consensus_flag_false_rejected_in_api_and_service(self):
        cfg = dict(
            contribution_amount="1000.00",
            contribution_frequency="MONTHLY",
            maximum_members=4,
            rotation_strategy="FIXED_ORDER",
            requires_consensus=False,
            allow_manual_contributions=True,
            currency="MZN",
        )
        self.assertFalse(CreateGroupSettingsSerializer(data=cfg).is_valid())
        self.assertFalse(
            UpdateGroupSettingsSerializer(
                data={"requires_consensus": False}
            ).is_valid()
        )
        with self.assertRaises(DomainException):
            GroupService.update_settings(
                group_id=self.group.id,
                updated_by=self.manager,
                data={"requires_consensus": False},
            )

    def test_authenticated_member_can_vote_via_endpoint(self):
        disbursement = self.propose()
        client = APIClient()
        client.force_authenticate(user=self.voter1)
        endpoint = reverse(
            "group-disbursement-approve",
            kwargs={
                "group_id": self.group.id,
                "disbursement_id": disbursement.id,
            },
        )
        response = client.post(endpoint, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["data"]["status"],
            Disbursement.Status.AWAITING_CONSENSUS,
        )
        self.assertEqual(
            response.data["data"]["approval_count"],
            1,
        )


    def test_api_demo_four_members_and_two_independent_votes(self):
        """The exact multi-login RN06 scenario used in the defense rehearsal."""
        client = APIClient()
        create_url = reverse(
            "group-disbursement-list-create",
            kwargs={"group_id": self.group.id},
        )
        client.force_authenticate(user=self.manager)
        created = client.post(
            create_url, {"cycle_number": 1}, format="json"
        )
        self.assertEqual(created.status_code, 201)
        disbursement_id = created.data["data"]["id"]
        approve_url = reverse(
            "group-disbursement-approve",
            kwargs={
                "group_id": self.group.id,
                "disbursement_id": disbursement_id,
            },
        )
        complete_url = reverse(
            "group-disbursement-complete",
            kwargs={
                "group_id": self.group.id,
                "disbursement_id": disbursement_id,
            },
        )
        self.assertEqual(
            created.data["data"]["status"],
            Disbursement.Status.AWAITING_CONSENSUS,
        )

        # The proposing manager cannot vote or complete before quorum.
        self.assertEqual(client.post(approve_url, format="json").status_code, 400)
        self.assertEqual(client.post(complete_url, format="json").status_code, 400)

        client.force_authenticate(user=self.voter1)
        first = client.post(approve_url, format="json")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(
            first.data["data"]["status"],
            Disbursement.Status.AWAITING_CONSENSUS,
        )
        self.assertEqual(first.data["data"]["approval_count"], 1)
        self.assertEqual(client.post(approve_url, format="json").status_code, 400)

        client.force_authenticate(user=self.voter2)
        second = client.post(approve_url, format="json")
        self.assertEqual(second.status_code, 200)
        self.assertEqual(
            second.data["data"]["status"],
            Disbursement.Status.APPROVED,
        )
        self.assertEqual(second.data["data"]["approval_count"], 2)

        client.force_authenticate(user=self.manager)
        finished = client.post(complete_url, format="json")
        self.assertEqual(finished.status_code, 200)
        self.assertEqual(
            finished.data["data"]["status"],
            Disbursement.Status.COMPLETED,
        )
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.COMPLETED)

    def test_ex_member_contribution_cannot_mask_missing_active_payer(self):
        """Four confirmations must belong to four currently active payers."""
        former = GroupMember.objects.create(
            group=self.group, user=self.outsider,
            status=GroupMember.Status.LEFT, role=GroupMember.Role.MEMBER,
        )
        Contribution.objects.create(
            member=former, group_settings=self.settings,
            amount=Decimal("1000.00"), currency="MZN",
            contribution_period=self.period,
            status=Contribution.Status.CONFIRMED,
            reference="RN06-EX-001",
        )
        missing = Contribution.objects.get(member=self.members[self.voter2.pk])
        missing.status = Contribution.Status.PENDING
        missing.save(update_fields=["status", "updated_at"])

        # Previous code counted 4 confirmed rows as 4 active members.
        with self.assertRaises(IncompleteContributions):
            self.propose()
        self.assertFalse(Disbursement.objects.filter(group=self.group).exists())

    def test_unresolved_ex_member_funds_block_proposal_instead_of_inflating_total(self):
        """Do not silently disburse a departed member's confirmed money."""
        former = GroupMember.objects.create(
            group=self.group, user=self.outsider,
            status=GroupMember.Status.LEFT, role=GroupMember.Role.MEMBER,
        )
        Contribution.objects.create(
            member=former, group_settings=self.settings,
            amount=Decimal("1000.00"), currency="MZN",
            contribution_period=self.period,
            status=Contribution.Status.CONFIRMED,
            reference="RN06-EX-002",
        )
        with self.assertRaises(IncompleteContributions):
            self.propose()

    def test_reversal_after_votes_blocks_admin_completion(self):
        """Quorum alone must not complete a now-unfunded cycle."""
        disbursement = self.propose()
        for voter in (self.voter1, self.voter2):
            DisbursementService.approve(
                disbursement_id=disbursement.id, approved_by=voter
            )
        reversed_payment = Contribution.objects.get(
            member=self.members[self.voter1.pk]
        )
        reversed_payment.status = Contribution.Status.REVERSED
        reversed_payment.save(update_fields=["status", "updated_at"])

        with self.assertRaises(IncompleteContributions):
            DisbursementService.complete(
                disbursement_id=disbursement.id, completed_by=self.manager
            )
        disbursement.refresh_from_db()
        self.rotation.refresh_from_db()
        self.assertNotEqual(disbursement.status, Disbursement.Status.COMPLETED)
        self.assertEqual(self.rotation.status, RotationOrder.Status.CURRENT)

    def test_changed_contribution_value_after_votes_blocks_completion(self):
        """Ledger amount at completion cannot diverge from proposed amount."""
        disbursement = self.propose()
        for voter in (self.voter1, self.voter2):
            DisbursementService.approve(
                disbursement_id=disbursement.id, approved_by=voter
            )
        payment = Contribution.objects.get(member=self.members[self.voter1.pk])
        payment.amount = Decimal("1.00")
        payment.save(update_fields=["amount", "updated_at"])

        with self.assertRaises(IncompleteContributions):
            DisbursementService.complete(
                disbursement_id=disbursement.id, completed_by=self.manager
            )
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.CURRENT)

    def test_member_added_after_votes_does_not_change_proposal_without_review(self):
        """Even a fully paid late joiner cannot expand a frozen proposal."""
        disbursement = self.propose()
        for voter in (self.voter1, self.voter2):
            DisbursementService.approve(
                disbursement_id=disbursement.id, approved_by=voter
            )
        added = GroupMember.objects.create(
            group=self.group, user=self.outsider,
            status=GroupMember.Status.ACTIVE, role=GroupMember.Role.MEMBER,
        )
        Contribution.objects.create(
            member=added, group_settings=self.settings,
            amount=Decimal("1000.00"), currency="MZN",
            contribution_period=self.period,
            status=Contribution.Status.CONFIRMED,
            reference="RN06-LATE-001",
        )
        with self.assertRaises(IncompleteContributions):
            DisbursementService.complete(
                disbursement_id=disbursement.id, completed_by=self.manager
            )
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.CURRENT)

    def test_wrong_currency_cannot_count_as_cycle_funding(self):
        payment = Contribution.objects.get(member=self.members[self.voter1.pk])
        payment.currency = "USD"
        payment.save(update_fields=["currency", "updated_at"])
        with self.assertRaises(IncompleteContributions):
            self.propose()

    def test_ex_member_contribution_added_after_votes_blocks_completion(self):
        disbursement = self.propose()
        for voter in (self.voter1, self.voter2):
            DisbursementService.approve(
                disbursement_id=disbursement.id, approved_by=voter
            )
        former = GroupMember.objects.create(
            group=self.group, user=self.outsider,
            status=GroupMember.Status.LEFT, role=GroupMember.Role.MEMBER,
        )
        Contribution.objects.create(
            member=former, group_settings=self.settings,
            amount=Decimal("1000.00"), currency="MZN",
            contribution_period=self.period,
            status=Contribution.Status.CONFIRMED,
            reference="RN06-EX-LATE-001",
        )
        with self.assertRaises(IncompleteContributions):
            DisbursementService.complete(
                disbursement_id=disbursement.id, completed_by=self.manager
            )
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.CURRENT)

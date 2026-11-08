"""Durable contribution intent and retry tests (mocked RPC boundary only)."""
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from accounts.models import User
from blockchain.models import BlockchainAnchorStatus
from blockchain.services.contribution_anchor_service import (
    ContributionAnchorHashMismatch,
)
from contributions.models import Contribution, ContributionAnchorIntent
from contributions.services.anchor_outbox_service import ContributionAnchorOutboxService
from contributions.services.contribution_hash_service import ContributionHashService
from contributions.services.contribution_service import (
    ContributionService,
    InvalidContributionAmount,
)
from groups.models import Group, GroupMember, GroupSettings


class ContributionAnchorOutboxTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            phone_number="+258841991001", password="test-only-password"
        )
        self.member_user = User.objects.create_user(
            phone_number="+258841991002", password="test-only-password"
        )
        self.group = Group.objects.create(name="RN06 pending anchor")
        self.settings = GroupSettings.objects.create(
            group=self.group, version=1,
            contribution_amount=Decimal("1000.00"),
            currency="MZN",
            contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
            maximum_members=4,
            rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
            requires_consensus=True, allow_manual_contributions=True,
            is_active=True,
        )
        GroupMember.objects.create(
            group=self.group, user=self.manager,
            role=GroupMember.Role.MANAGER, status=GroupMember.Status.ACTIVE,
        )
        self.member = GroupMember.objects.create(
            group=self.group, user=self.member_user,
            role=GroupMember.Role.MEMBER, status=GroupMember.Status.ACTIVE,
        )

    def queue(self):
        # TestCase wraps itself in an outer test transaction, so an on_commit
        # callback cannot fire until the DB is actually committed.
        return ContributionService.register_manual_contribution(
            group_id=self.group.pk,
            registered_by=self.manager,
            data={
                "group_member_id": self.member.pk,
                "amount": Decimal("1000.00"),
                "contribution_period": date(2026, 11, 1),
            },
        )

    def test_ledger_row_and_frozen_hash_are_saved_before_any_rpc(self):
        with patch(
            "contributions.services.contribution_service."
            "ContributionAnchorOutboxService.process"
        ) as process:
            contribution = self.queue()
        intent = ContributionAnchorIntent.objects.get(contribution=contribution)
        self.assertEqual(intent.status, ContributionAnchorIntent.Status.PENDING)
        self.assertEqual(
            intent.content_hash, ContributionHashService.calculate(contribution)
        )
        self.assertEqual(intent.attempt_count, 0)
        process.assert_not_called()

    def test_retry_eventually_confirms_once_and_repeated_call_is_noop(self):
        contribution = self.queue()
        intent = contribution.anchor_intent
        with patch(
            "contributions.services.anchor_outbox_service.ContributionAnchorService"
        ) as svc:
            svc.return_value.anchor.return_value = SimpleNamespace(
                status=BlockchainAnchorStatus.CONFIRMED
            )
            self.assertEqual(
                ContributionAnchorOutboxService.process(intent.pk),
                ContributionAnchorIntent.Status.CONFIRMED,
            )
            self.assertEqual(
                ContributionAnchorOutboxService.process(intent.pk),
                ContributionAnchorIntent.Status.CONFIRMED,
            )
            self.assertEqual(svc.return_value.anchor.call_count, 1)
        intent.refresh_from_db()
        self.assertEqual(intent.attempt_count, 1)
        self.assertEqual(intent.status, ContributionAnchorIntent.Status.CONFIRMED)

    def test_failed_rpc_leaves_retryable_intent_without_rollback_of_contribution(self):
        contribution = self.queue()
        intent = contribution.anchor_intent
        with patch(
            "contributions.services.anchor_outbox_service.ContributionAnchorService"
        ) as svc:
            svc.return_value.anchor.side_effect = TimeoutError("RPC unavailable")
            self.assertEqual(
                ContributionAnchorOutboxService.process(intent.pk),
                ContributionAnchorIntent.Status.PENDING,
            )
            intent.refresh_from_db()
            self.assertEqual(intent.last_error_code, "TimeoutError")
            self.assertEqual(intent.attempt_count, 1)
            self.assertTrue(Contribution.objects.filter(pk=contribution.pk).exists())

            svc.return_value.anchor.side_effect = None
            svc.return_value.anchor.return_value = SimpleNamespace(
                status=BlockchainAnchorStatus.CONFIRMED
            )
            self.assertEqual(
                ContributionAnchorOutboxService.process(intent.pk),
                ContributionAnchorIntent.Status.CONFIRMED,
            )
        intent.refresh_from_db()
        self.assertEqual(intent.attempt_count, 2)
        self.assertEqual(intent.last_error_code, "")

    def test_changed_or_conflicting_hash_requires_review_never_blind_retry(self):
        contribution = self.queue()
        intent = contribution.anchor_intent
        with patch(
            "contributions.services.anchor_outbox_service.ContributionAnchorService"
        ) as svc:
            svc.return_value.anchor.side_effect = ContributionAnchorHashMismatch(
                "Different hash"
            )
            self.assertEqual(
                ContributionAnchorOutboxService.process(intent.pk),
                ContributionAnchorIntent.Status.REVIEW_REQUIRED,
            )
            self.assertEqual(
                ContributionAnchorOutboxService.process(intent.pk),
                ContributionAnchorIntent.Status.REVIEW_REQUIRED,
            )
            svc.return_value.anchor.assert_called_once()
        intent.refresh_from_db()
        self.assertEqual(intent.attempt_count, 1)

    def test_invalid_contribution_does_not_leave_intent(self):
        with self.assertRaises(InvalidContributionAmount):
            ContributionService.register_manual_contribution(
                group_id=self.group.pk,
                registered_by=self.manager,
                data={
                    "group_member_id": self.member.pk,
                    "amount": Decimal("400.00"),
                    "contribution_period": date(2026, 11, 1),
                },
            )
        self.assertFalse(ContributionAnchorIntent.objects.exists())

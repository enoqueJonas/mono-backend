"""Durable contribution intent and retry tests (mocked RPC boundary only)."""
from datetime import date, timedelta
from io import StringIO
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from django.test import TestCase

from accounts.models import User
from blockchain.models import BlockchainAnchorStatus
from blockchain.services.contribution_anchor_service import (
    ContributionAnchorHashMismatch,
    ContributionAnchorService,
    ContributionAnchorSubmissionUncertain,
)
from contributions.models import Contribution, ContributionAnchorIntent
from contributions.serializers.contribution import ContributionSerializer
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
        self.assertEqual(
            ContributionSerializer(contribution).data["anchoring_status"],
            ContributionAnchorIntent.Status.CONFIRMED,
        )

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

    def test_manual_recovery_command_processes_pending_intent(self):
        contribution = self.queue()
        output = StringIO()
        with patch(
            "contributions.management.commands.reconcile_contribution_anchors."
            "ContributionAnchorOutboxService"
        ) as worker:
            worker.pending_ids.return_value = [contribution.anchor_intent.pk]
            worker.process.return_value = ContributionAnchorIntent.Status.CONFIRMED
            call_command(
                "reconcile_contribution_anchors",
                "--limit", "1",
                stdout=output,
            )
            worker.pending_ids.assert_called_once_with(limit=1)
            worker.process.assert_called_once_with(contribution.anchor_intent.pk)
        self.assertIn("attempted=1", output.getvalue())
        self.assertIn("confirmed=1", output.getvalue())

    def test_uncertain_submission_is_quarantined_instead_of_auto_rebroadcast(self):
        contribution = self.queue()
        intent = contribution.anchor_intent
        with patch(
            "contributions.services.anchor_outbox_service.ContributionAnchorService"
        ) as svc:
            svc.return_value.anchor.side_effect = (
                ContributionAnchorSubmissionUncertain("broadcast outcome unknown")
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
        self.assertIsNone(intent.next_attempt_at)
        self.assertEqual(intent.last_error_code, "ContributionAnchorSubmissionUncertain")

    def test_stale_processing_claim_is_reconciliation_only(self):
        contribution = self.queue()
        intent = contribution.anchor_intent
        intent.status = ContributionAnchorIntent.Status.PROCESSING
        intent.claimed_at = timezone.now() - timedelta(minutes=20)
        intent.save(update_fields=["status", "claimed_at"])
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
            self.assertFalse(svc.return_value.anchor.call_args.kwargs["allow_submit"])

    def test_reconcile_only_does_not_call_register_contribution(self):
        contribution = self.queue()
        client = MagicMock()
        client.get_contribution.return_value = {"exists": False}
        anchor = ContributionAnchorService(client=client)
        with self.assertRaises(ContributionAnchorSubmissionUncertain):
            anchor.anchor(
                contribution,
                expected_hash=ContributionHashService.calculate(contribution),
                allow_submit=False,
            )
        client.register_contribution.assert_not_called()

    def test_rpc_failure_uses_backoff_in_due_worker_queue(self):
        contribution = self.queue()
        intent = contribution.anchor_intent
        with patch(
            "contributions.services.anchor_outbox_service.ContributionAnchorService"
        ) as svc:
            svc.return_value.anchor.side_effect = TimeoutError("test timeout")
            self.assertEqual(
                ContributionAnchorOutboxService.process(intent.pk),
                ContributionAnchorIntent.Status.PENDING,
            )
        intent.refresh_from_db()
        self.assertGreater(intent.next_attempt_at, timezone.now())
        self.assertNotIn(
            intent.pk,
            ContributionAnchorOutboxService.pending_ids(limit=100),
        )
        intent.next_attempt_at = timezone.now() - timedelta(seconds=1)
        intent.save(update_fields=["next_attempt_at"])
        self.assertIn(
            intent.pk,
            ContributionAnchorOutboxService.pending_ids(limit=100),
        )

    def test_dry_run_is_read_only_and_reports_outstanding_intents(self):
        contribution = self.queue()
        output = StringIO()
        with patch(
            "contributions.management.commands.reconcile_contribution_anchors."
            "ContributionAnchorOutboxService"
        ) as service:
            call_command(
                "reconcile_contribution_anchors", "--dry-run",
                stdout=output,
            )
            service.pending_ids.assert_not_called()
            service.process.assert_not_called()
        self.assertIn("dry_run=1", output.getvalue())
        self.assertIn("outstanding_pending=1", output.getvalue())
        self.assertTrue(
            ContributionAnchorIntent.objects.filter(
                contribution=contribution,
                status=ContributionAnchorIntent.Status.PENDING,
            ).exists()
        )

    def test_multi_cycle_worker_requires_explicit_opt_in_and_postgresql(self):
        with self.assertRaises(CommandError):
            call_command(
                "reconcile_contribution_anchors",
                "--cycles", "2",
                "--poll-seconds", "1",
            )

    def test_review_only_reconciles_existing_anchor_without_allowing_send(self):
        contribution = self.queue()
        intent = contribution.anchor_intent
        intent.status = ContributionAnchorIntent.Status.REVIEW_REQUIRED
        intent.save(update_fields=["status"])
        with patch(
            "contributions.services.anchor_outbox_service.ContributionAnchorService"
        ) as svc:
            svc.return_value.anchor.return_value = SimpleNamespace(
                status=BlockchainAnchorStatus.CONFIRMED
            )
            result = ContributionAnchorOutboxService.process(
                intent.pk, reconcile_only=True
            )
            self.assertEqual(result, ContributionAnchorIntent.Status.CONFIRMED)
            self.assertFalse(svc.return_value.anchor.call_args.kwargs["allow_submit"])

    def test_review_only_command_selects_quarantine_without_send_permission(self):
        contribution = self.queue()
        intent = contribution.anchor_intent
        intent.status = ContributionAnchorIntent.Status.REVIEW_REQUIRED
        intent.save(update_fields=["status"])
        output = StringIO()
        with patch(
            "contributions.management.commands.reconcile_contribution_anchors."
            "ContributionAnchorOutboxService"
        ) as worker:
            worker.process.return_value = ContributionAnchorIntent.Status.CONFIRMED
            call_command(
                "reconcile_contribution_anchors",
                "--review-only", "--limit", "1",
                stdout=output,
            )
            worker.pending_ids.assert_not_called()
            worker.process.assert_called_once_with(
                intent.pk, reconcile_only=True
            )
        self.assertIn("review_only=1", output.getvalue())

    def test_unknown_network_broadcast_is_wrapped_as_uncertain(self):
        contribution = self.queue()
        client = MagicMock()
        client.get_contribution.return_value = {"exists": False}
        client.register_contribution.side_effect = TimeoutError(
            "synthetic RPC timeout after broadcast"
        )
        with self.assertRaises(ContributionAnchorSubmissionUncertain):
            ContributionAnchorService(client=client).anchor(
                contribution,
                expected_hash=ContributionHashService.calculate(contribution),
            )
        client.register_contribution.assert_called_once()

    def test_exhausted_retry_budget_goes_to_review_without_infinite_polling(self):
        contribution = self.queue()
        intent = contribution.anchor_intent
        intent.attempt_count = ContributionAnchorOutboxService.MAX_ATTEMPTS - 1
        intent.save(update_fields=["attempt_count"])
        with patch(
            "contributions.services.anchor_outbox_service.ContributionAnchorService"
        ) as svc:
            svc.return_value.anchor.side_effect = ConnectionError("test-only outage")
            self.assertEqual(
                ContributionAnchorOutboxService.process(intent.pk),
                ContributionAnchorIntent.Status.REVIEW_REQUIRED,
            )
            svc.return_value.anchor.assert_called_once()
        intent.refresh_from_db()
        self.assertEqual(
            intent.attempt_count, ContributionAnchorOutboxService.MAX_ATTEMPTS
        )
        self.assertIsNone(intent.next_attempt_at)
        self.assertNotIn(
            intent.pk, ContributionAnchorOutboxService.pending_ids(limit=100)
        )

    def test_health_gate_fails_on_review_without_broadcast(self):
        contribution = self.queue()
        intent = contribution.anchor_intent
        intent.status = ContributionAnchorIntent.Status.REVIEW_REQUIRED
        intent.save(update_fields=["status"])
        output = StringIO()
        with patch(
            "contributions.management.commands.reconcile_contribution_anchors."
            "ContributionAnchorOutboxService"
        ) as worker:
            with self.assertRaises(CommandError):
                call_command(
                    "reconcile_contribution_anchors",
                    "--dry-run", "--fail-on-review",
                    stdout=output,
                )
            worker.pending_ids.assert_not_called()
            worker.process.assert_not_called()
        self.assertIn("outstanding_review=1", output.getvalue())

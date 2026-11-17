from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

from django.test import TestCase, override_settings

from accounts.models import User
from contributions.models import Contribution
from disbursements.models import Disbursement, DisbursementExecution
from disbursements.services.disbursement_service import (
    DisbursementService, InvalidDisbursementStatus,
)
from disbursements.services.financial_execution_service import (
    FinancialExecutionService, PayoutEvidenceMismatch, PayoutNotReady,
)
from groups.models import Group, GroupMember, GroupSettings, RotationOrder


class FakeRegistry:
    """An injected chain test double; does not represent a mined transaction."""
    def __init__(self):
        self.intent_calls = 0
        self.settlement_calls = 0
        self.fail_settlement_once = False

    def anchor_intent(self, *_args):
        self.intent_calls += 1
        return SimpleNamespace(transaction_hash="0x" + "a" * 64)

    def anchor_settlement(self, *_args):
        self.settlement_calls += 1
        if self.fail_settlement_once:
            self.fail_settlement_once = False
            raise TimeoutError("Ganache receipt delayed")
        return SimpleNamespace(transaction_hash="0x" + "b" * 64)


class FakeGateway:
    """Authenticated-looking result is injected only by tests, not from the browser."""
    def __init__(self):
        self.sends = 0
        self.response = "SUCCESS"
        self.wrong_amount = False

    def send(self, execution):
        self.sends += 1
        return {"status": "PENDING", "transaction_id": "TX-123"}

    def query(self, execution):
        if self.response == "SUCCESS":
            return {
                "status": "SUCCESS",
                "reference": execution.reference,
                "transaction_id": "TX-123",
                "recipient_msisdn": execution.recipient_msisdn,
                "currency": execution.currency,
                "amount": "1.00" if self.wrong_amount else str(execution.amount),
            }
        return {"status": self.response}


@override_settings(DISBURSEMENT_PAYOUT_REQUIRED=True)
class FinancialExecutionTests(TestCase):
    def setUp(self):
        self.manager, self.recipient, self.voter1, self.voter2 = [
            User.objects.create_user(
                phone_number=f"+25884188000{i}", password="password123"
            ) for i in range(4)
        ]
        self.group = Group.objects.create(name="Xitique financeiro")
        self.settings = GroupSettings.objects.create(
            group=self.group, version=1,
            contribution_amount=Decimal("1000.00"), currency="MZN",
            contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
            maximum_members=6,
            rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
            requires_consensus=True,
            allow_manual_contributions=True, is_active=True,
        )
        self.members = []
        for user, role in [
            (self.manager, GroupMember.Role.MANAGER),
            (self.recipient, GroupMember.Role.MEMBER),
            (self.voter1, GroupMember.Role.MEMBER),
            (self.voter2, GroupMember.Role.MEMBER),
        ]:
            member = GroupMember.objects.create(
                group=self.group, user=user, role=role,
                status=GroupMember.Status.ACTIVE,
            )
            self.members.append(member)
        period = date(2026, 11, 1)
        self.rotation = RotationOrder.objects.create(
            group=self.group, member=self.members[1],
            group_settings=self.settings, contribution_period=period,
            cycle_number=1, position=1, status=RotationOrder.Status.CURRENT,
        )
        for i, member in enumerate(self.members):
            Contribution.objects.create(
                member=member, group_settings=self.settings,
                amount=Decimal("1000.00"), currency="MZN",
                source=Contribution.Source.MANUAL, status=Contribution.Status.CONFIRMED,
                contribution_period=period, reference=f"PAYOUT-{i}",
            )
        self.item = DisbursementService.create(
            group_id=self.group.id, cycle_number=1, created_by=self.manager
        )
        for voter in (self.voter1, self.voter2):
            DisbursementService.approve(
                disbursement_id=self.item.id, approved_by=voter
            )
        self.registry = FakeRegistry()
        self.gateway = FakeGateway()

    def _prepare_and_send(self):
        item = FinancialExecutionService.prepare(
            disbursement_id=self.item.id, actor=self.manager
        )
        FinancialExecutionService.anchor_intent(
            execution_id=item.id, actor=self.manager, registry=self.registry
        )
        return FinancialExecutionService.send(
            execution_id=item.id, actor=self.manager, gateway=self.gateway
        )

    def test_cannot_complete_without_provider_and_chain_proof(self):
        with self.assertRaises(InvalidDisbursementStatus):
            DisbursementService.complete(
                disbursement_id=self.item.id, completed_by=self.manager
            )
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, Disbursement.Status.APPROVED)

    def test_verified_pipeline_anchors_two_hashes_and_advances_rotation(self):
        payout = self._prepare_and_send()
        self.assertEqual(payout.status, DisbursementExecution.Status.PENDING)
        payout = FinancialExecutionService.query_provider(
            execution_id=payout.id, actor=self.manager, gateway=self.gateway
        )
        self.assertEqual(payout.status, DisbursementExecution.Status.PROVIDER_CONFIRMED)
        FinancialExecutionService.anchor_settlement(
            execution_id=payout.id, actor=self.manager, registry=self.registry
        )
        self.item.refresh_from_db()
        self.rotation.refresh_from_db()
        payout.refresh_from_db()
        self.assertEqual(self.item.status, Disbursement.Status.COMPLETED)
        self.assertEqual(self.rotation.status, RotationOrder.Status.COMPLETED)
        self.assertEqual(payout.status, DisbursementExecution.Status.SETTLEMENT_ANCHORED)
        self.assertEqual(self.registry.intent_calls, 1)
        self.assertEqual(self.registry.settlement_calls, 1)
        self.assertEqual(self.gateway.sends, 1)
        self.assertEqual(len(payout.intent_hash), 64)
        self.assertEqual(len(payout.settlement_hash), 64)

    def test_ambiguous_or_pending_provider_response_never_completes(self):
        payout = self._prepare_and_send()
        self.gateway.response = "UNKNOWN"
        FinancialExecutionService.query_provider(
            execution_id=payout.id, actor=self.manager, gateway=self.gateway
        )
        payout.refresh_from_db()
        self.assertEqual(payout.status, DisbursementExecution.Status.UNKNOWN)
        with self.assertRaises(PayoutNotReady):
            FinancialExecutionService.send(
                execution_id=payout.id, actor=self.manager, gateway=self.gateway
            )
        with self.assertRaises(PayoutNotReady):
            FinancialExecutionService.anchor_settlement(
                execution_id=payout.id, actor=self.manager, registry=self.registry
            )
        self.assertEqual(self.gateway.sends, 1)
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.CURRENT)

    def test_provider_mismatch_is_rejected(self):
        payout = self._prepare_and_send()
        self.gateway.wrong_amount = True
        with self.assertRaises(PayoutEvidenceMismatch):
            FinancialExecutionService.query_provider(
                execution_id=payout.id, actor=self.manager, gateway=self.gateway
            )
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, Disbursement.Status.APPROVED)

    def test_onchain_failure_after_payment_is_recoverable_without_resend(self):
        payout = self._prepare_and_send()
        FinancialExecutionService.query_provider(
            execution_id=payout.id, actor=self.manager, gateway=self.gateway
        )
        self.registry.fail_settlement_once = True
        with self.assertRaises(TimeoutError):
            FinancialExecutionService.anchor_settlement(
                execution_id=payout.id, actor=self.manager, registry=self.registry
            )
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, Disbursement.Status.APPROVED)
        FinancialExecutionService.anchor_settlement(
            execution_id=payout.id, actor=self.manager, registry=self.registry
        )
        self.assertEqual(self.gateway.sends, 1)

    def test_reusing_the_same_payout_reference_is_idempotent(self):
        first = FinancialExecutionService.prepare(
            disbursement_id=self.item.id, actor=self.manager
        )
        second = FinancialExecutionService.prepare(
            disbursement_id=self.item.id, actor=self.manager
        )
        self.assertEqual(first.id, second.id)
        self.assertEqual(first.reference, second.reference)

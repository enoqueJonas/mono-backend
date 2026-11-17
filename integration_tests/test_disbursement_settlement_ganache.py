"""Real PostgreSQL + Ganache proof, with a STRICTLY SYNTHETIC payout provider.

This never calls Vodacom/e-Mola or sends actual funds. It proves the DB+EVM
ordering and that rotation does not advance before both immutable anchors.
"""
from datetime import date
from decimal import Decimal

import pytest
from django.db import connection
from django.test import override_settings

from accounts.models import User
from blockchain.clients.disbursement_registry_client import DisbursementRegistryClient
from contributions.models import Contribution
from disbursements.models import Disbursement, DisbursementExecution
from disbursements.services.disbursement_service import (
    DisbursementService, InvalidDisbursementStatus,
)
from disbursements.services.financial_execution_service import FinancialExecutionService
from groups.models import Group, GroupMember, GroupSettings, RotationOrder
from integration_tests.test_registry_custody_ganache import _artifact, _deploy, _node


class SyntheticProvider:
    """Only a deterministic test double; does not claim settlement in M-Pesa."""
    sends = 0

    def send(self, execution):
        self.sends += 1
        return {"status": "PENDING", "transaction_id": "SYNTHETIC-TX-1"}

    def query(self, execution):
        return {
            "status": "SUCCESS",
            "reference": execution.reference,
            "amount": str(execution.amount),
            "currency": execution.currency,
            "recipient_msisdn": execution.recipient_msisdn,
            "transaction_id": "SYNTHETIC-TX-1",
        }


@pytest.mark.django_db(transaction=True)
def test_real_ganache_two_proofs_without_real_payment():
    assert connection.vendor == "postgresql", "Expected genuine PostgreSQL"
    w3 = _node()
    contract = _deploy(w3, _artifact("DisbursementRegistry"), w3.eth.accounts[0])
    members = [
        User.objects.create_user(
            phone_number=f"+25884199700{i}", password="synthetic-only-test"
        )
        for i in range(4)
    ]
    group = Group.objects.create(name="Simulacao exclusiva RN06+B2C")
    group_settings = GroupSettings.objects.create(
        group=group, version=1, is_active=True,
        contribution_amount=Decimal("1000.00"), currency="MZN",
        contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
        maximum_members=6,
        rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
        requires_consensus=True, allow_manual_contributions=True,
    )
    group_members = [
        GroupMember.objects.create(
            group=group, user=user, status=GroupMember.Status.ACTIVE,
            role=GroupMember.Role.MANAGER if i == 0 else GroupMember.Role.MEMBER,
        )
        for i, user in enumerate(members)
    ]
    rotation = RotationOrder.objects.create(
        group=group, member=group_members[1],
        group_settings=group_settings,
        contribution_period=date(2026, 11, 1),
        cycle_number=1, position=1, status=RotationOrder.Status.CURRENT,
    )
    for i, member in enumerate(group_members):
        Contribution.objects.create(
            member=member, group_settings=group_settings,
            amount=Decimal("1000.00"), currency="MZN",
            source=Contribution.Source.MANUAL,
            status=Contribution.Status.CONFIRMED,
            contribution_period=date(2026, 11, 1),
            reference=f"SETTLEMENT-SYNTHETIC-{i}",
        )
    with override_settings(
        DISBURSEMENT_PAYOUT_REQUIRED=True,
        DISBURSEMENT_REGISTRY_ADDRESS=contract.address,
    ):
        proposal = DisbursementService.create(
            group_id=group.id, cycle_number=1, created_by=members[0]
        )
        for voter in members[2:4]:
            DisbursementService.approve(
                disbursement_id=proposal.id, approved_by=voter
            )
        with pytest.raises(InvalidDisbursementStatus):
            DisbursementService.complete(
                disbursement_id=proposal.id, completed_by=members[0]
            )
        execution = FinancialExecutionService.prepare(
            disbursement_id=proposal.id, actor=members[0]
        )
        client = DisbursementRegistryClient()
        FinancialExecutionService.anchor_intent(
            execution_id=execution.id, actor=members[0], registry=client
        )
        proof_after_intent = client.get(proposal.id)
        assert proof_after_intent["intent_hash"] != "0" * 64
        assert proof_after_intent["settlement_at"] == 0
        provider = SyntheticProvider()
        FinancialExecutionService.send(
            execution_id=execution.id, actor=members[0], gateway=provider
        )
        proposal.refresh_from_db()
        rotation.refresh_from_db()
        assert proposal.status == Disbursement.Status.APPROVED
        assert rotation.status == RotationOrder.Status.CURRENT
        FinancialExecutionService.query_provider(
            execution_id=execution.id, actor=members[0], gateway=provider
        )
        proposal.refresh_from_db()
        assert proposal.status == Disbursement.Status.APPROVED
        FinancialExecutionService.anchor_settlement(
            execution_id=execution.id, actor=members[0], registry=client
        )
        execution.refresh_from_db()
        proposal.refresh_from_db()
        rotation.refresh_from_db()
        proof = client.get(proposal.id)
        assert proof["intent_hash"] == execution.intent_hash
        assert proof["settlement_hash"] == execution.settlement_hash
        assert proof["intent_at"] > 0 and proof["settlement_at"] >= proof["intent_at"]
        assert proposal.status == Disbursement.Status.COMPLETED
        assert rotation.status == RotationOrder.Status.COMPLETED
        assert execution.status == DisbursementExecution.Status.SETTLEMENT_ANCHORED
        assert provider.sends == 1

    print(
        "DISBURSEMENT_E2E PostgreSQL=True Ganache=True "
        "two_proofs=True votes=2 synthetic_provider_only=True "
        "real_financial_payment=False duplicate_send=False"
    )

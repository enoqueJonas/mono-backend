"""Actual PostgreSQL + Ganache + fictitious group/member transfer, no real PSP.

The resulting on-chain events prove that the prototype recorded hashes of
its own simulated decisions and virtual settlement. They are not receipts
from M-Pesa or e-Mola and do not prove a real-world payment.
"""
from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.conf import settings
from django.db import connection
from django.test import override_settings

from accounts.models import User
from blockchain.clients.disbursement_registry_client import DisbursementRegistryClient
from contributions.models import ContributionAnchorIntent
from contributions.services.contribution_service import ContributionService
from disbursements.models import Disbursement
from disbursements.services.disbursement_service import DisbursementService
from disbursements.services.sandbox_payout_service import SandboxPayoutService
from groups.models import Group, GroupMember, GroupSettings, RotationOrder
from integration_tests.test_registry_custody_ganache import _artifact, _deploy, _node
from wallets.models import SandboxAccount, SandboxTransfer
from wallets.services.sandbox_ledger import SandboxLedgerService


def _make_fixture():
    users = [
        User.objects.create_user(
            phone_number=f"+25884755160{i}", password="test-only-do-not-reuse"
        ) for i in range(4)
    ]
    manager, beneficiary, voter1, voter2 = users
    group = Group.objects.create(name="Xitique E2E sandbox")
    settings_obj = GroupSettings.objects.create(
        group=group, version=1, is_active=True,
        contribution_amount=Decimal("1000.00"), currency="MZN",
        contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
        maximum_members=5,
        rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
        requires_consensus=True, allow_manual_contributions=True,
    )
    membership = {}
    for user in users:
        membership[user.pk] = GroupMember.objects.create(
            group=group,
            user=user,
            status=GroupMember.Status.ACTIVE,
            role=GroupMember.Role.MANAGER if user == manager else GroupMember.Role.MEMBER,
        )
    rotation = RotationOrder.objects.create(
        group=group,
        member=membership[beneficiary.pk],
        group_settings=settings_obj,
        cycle_number=1,
        position=1,
        contribution_period=date(2026, 11, 1),
        status=RotationOrder.Status.CURRENT,
    )
    # An authenticated provider request has already been validated by the
    # wallet view; here we exercise the service + ledger and actual anchor.
    for i, user in enumerate(users):
        ContributionService.register_mobile_wallet_contribution(data={
            "group_id": group.pk,
            "group_member_id": membership[user.pk].pk,
            "amount": Decimal("1000.00"),
            "currency": "MZN",
            "contribution_period": date(2026, 11, 1),
            "reference": f"MONO-GANACHE-VIRTUAL-{i}",
        })
    assert ContributionAnchorIntent.objects.count() == 4
    assert not ContributionAnchorIntent.objects.exclude(
        status=ContributionAnchorIntent.Status.CONFIRMED
    ).exists(), "Test contributions did not reconcile against actual Ganache"

    disbursement = DisbursementService.create(
        group_id=group.pk, cycle_number=1, created_by=manager,
    )
    DisbursementService.approve(
        disbursement_id=disbursement.pk, approved_by=voter1,
    )
    DisbursementService.approve(
        disbursement_id=disbursement.pk, approved_by=voter2,
    )
    disbursement.refresh_from_db()
    assert disbursement.status == Disbursement.Status.APPROVED
    return group, manager, beneficiary, disbursement, rotation


@pytest.mark.django_db(transaction=True)
def test_full_virtual_payout_with_real_ganache_receipts():
    assert connection.vendor == "postgresql"
    assert settings.BLOCKCHAIN_CHAIN_ID == 1337
    w3 = _node()
    assert w3.eth.chain_id == 1337
    issuer = w3.eth.accounts[0]
    contribution_registry = _deploy(w3, _artifact("ContributionRegistry"), issuer)
    payout_registry = _deploy(w3, _artifact("DisbursementRegistry"), issuer)

    with override_settings(
        SANDBOX_PAYMENTS_ENABLED=True,
        CONTRIBUTION_REGISTRY_ADDRESS=contribution_registry.address,
        DISBURSEMENT_REGISTRY_ADDRESS=payout_registry.address,
    ):
        group, manager, beneficiary, disbursement, rotation = _make_fixture()
        group_key = SandboxLedgerService.group_key(group.pk, "MZN")
        assert SandboxAccount.objects.get(key=group_key).balance == Decimal("4000.00")
        assert payout_registry.functions.getDisbursement(
            DisbursementRegistryClient._id_bytes32(str(disbursement.pk))
        ).call()[-2:] == [False, False]

        # Actual operator-signed on-chain authorization → SQL virtual transfer
        # → actual operator-signed settlement hash → advance rotation.
        result = SandboxPayoutService.execute(
            disbursement_id=disbursement.pk, completed_by=manager
        )
        assert result.status == Disbursement.Status.COMPLETED
        assert SandboxAccount.objects.get(key=group_key).balance == Decimal("0.00")
        recipient_key = SandboxLedgerService.member_key(beneficiary.pk, "MZN")
        assert SandboxAccount.objects.get(key=recipient_key).balance == Decimal("4000.00")
        assert SandboxTransfer.objects.filter(purpose=SandboxTransfer.Purpose.PAYOUT).count() == 1
        transfer = SandboxTransfer.objects.get(purpose=SandboxTransfer.Purpose.PAYOUT)
        assert transfer.entries.count() == 2
        assert sum(transfer.entries.values_list("signed_amount", flat=True)) == 0

        onchain = DisbursementRegistryClient().get(str(disbursement.pk))
        assert onchain["authorized"] and onchain["settled"]
        assert onchain["authorization_hash"] == SandboxPayoutService.authorization_hash(disbursement)
        assert onchain["settlement_hash"] == SandboxPayoutService.settlement_hash(transfer)
        rotation.refresh_from_db()
        assert rotation.status == RotationOrder.Status.COMPLETED

        # Idempotent replay: no additional transaction, no second fictional debit.
        height = w3.eth.block_number
        again = SandboxPayoutService.execute(
            disbursement_id=disbursement.pk, completed_by=manager
        )
        assert again.status == Disbursement.Status.COMPLETED
        assert SandboxAccount.objects.get(key=group_key).balance == Decimal("0.00")
        assert SandboxTransfer.objects.filter(purpose=SandboxTransfer.Purpose.PAYOUT).count() == 1
        assert w3.eth.block_number == height
        print(
            "SANDBOX_PAYOUT_E2E postgres=True ganache=True "
            "rn06=True payout_virtual=True proof_authorized=True "
            "proof_settled=True duplicate_debit=False real_funds=False"
        )


@pytest.mark.django_db(transaction=True)
def test_after_virtual_debit_rpc_failure_reconciles_without_double_payment():
    assert connection.vendor == "postgresql"
    w3 = _node()
    issuer = w3.eth.accounts[0]
    contributions = _deploy(w3, _artifact("ContributionRegistry"), issuer)
    payout = _deploy(w3, _artifact("DisbursementRegistry"), issuer)
    with override_settings(
        SANDBOX_PAYMENTS_ENABLED=True,
        CONTRIBUTION_REGISTRY_ADDRESS=contributions.address,
        DISBURSEMENT_REGISTRY_ADDRESS=payout.address,
    ):
        group, manager, beneficiary, disbursement, _ = _make_fixture()
        original = DisbursementRegistryClient.anchor_verified_settlement
        attempts = []

        def fail_after_mining(self, *args, **kwargs):
            receipt = original(self, *args, **kwargs)
            assert receipt.status
            attempts.append(receipt.transaction_hash)
            raise TimeoutError("Simulated response loss after EVM settlement mined")

        with patch.object(
            DisbursementRegistryClient,
            "anchor_verified_settlement",
            new=fail_after_mining,
        ):
            with pytest.raises(TimeoutError):
                SandboxPayoutService.execute(
                    disbursement_id=disbursement.pk, completed_by=manager
                )

        disbursement.refresh_from_db()
        assert disbursement.status == Disbursement.Status.PROCESSING
        assert SandboxTransfer.objects.filter(purpose=SandboxTransfer.Purpose.PAYOUT).count() == 1
        balance = SandboxAccount.objects.get(
            key=SandboxLedgerService.group_key(group.pk, "MZN")
        ).balance
        assert balance == Decimal("0.00")
        block_before = w3.eth.block_number

        # Reconcile the state actually mined; do not submit another EVM
        # settlement nor debit virtual funds twice.
        done = SandboxPayoutService.execute(
            disbursement_id=disbursement.pk, completed_by=manager
        )
        assert done.status == Disbursement.Status.COMPLETED
        assert SandboxTransfer.objects.filter(purpose=SandboxTransfer.Purpose.PAYOUT).count() == 1
        assert SandboxAccount.objects.get(
            key=SandboxLedgerService.group_key(group.pk, "MZN")
        ).balance == balance
        assert w3.eth.block_number == block_before
        assert len(attempts) == 1
        print("SANDBOX_PAYOUT_RECOVERY mined_then_timeout=True resubmission=False duplicate_debit=False")

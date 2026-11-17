"""End-to-end external-disbursement CLAIM (not funds transfer) in PostgreSQL/Ganache.

Actual payment is executed outside Mono. This test uses authenticated app
claims and a real smart contract that anchors their hashes, not a bank sandbox.
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
from contributions.models import Contribution
from disbursements.models import Disbursement, ExternalPaymentReport, TreasuryMandate
from disbursements.services.disbursement_service import DisbursementService
from disbursements.services.noncustodial_service import (
    NonCustodialDisbursementService as ExternalService,
)
from groups.models import Group, GroupMember, GroupSettings, RotationOrder
from integration_tests.test_registry_custody_ganache import _artifact, _deploy, _node
from wallets.models import SandboxTransfer


def _approved_fixture():
    users = [
        User.objects.create_user(
            phone_number=f"+25884555140{i}", password="disposable-test-only",
        ) for i in range(4)
    ]
    manager, beneficiary, treasurer, voter = users
    group = Group.objects.create(name="External wallet custody demonstration")
    group_settings = GroupSettings.objects.create(
        group=group, version=1, is_active=True,
        contribution_amount=Decimal("1000.00"), currency="MZN",
        contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
        maximum_members=5,
        rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
        requires_consensus=True, allow_manual_contributions=True,
    )
    memberships = {}
    for user, role in (
        (manager, GroupMember.Role.MANAGER),
        (beneficiary, GroupMember.Role.MEMBER),
        (treasurer, GroupMember.Role.TREASURER),
        (voter, GroupMember.Role.MEMBER),
    ):
        memberships[user.pk] = GroupMember.objects.create(
            group=group, user=user, role=role, status=GroupMember.Status.ACTIVE,
        )
    rotation = RotationOrder.objects.create(
        group=group, member=memberships[beneficiary.pk],
        group_settings=group_settings, contribution_period=date(2026, 11, 1),
        cycle_number=1, position=1, status=RotationOrder.Status.CURRENT,
    )
    for i, membership in enumerate(memberships.values()):
        Contribution.objects.create(
            member=membership, group_settings=group_settings,
            amount=Decimal("1000.00"), currency="MZN",
            status=Contribution.Status.CONFIRMED,
            source=Contribution.Source.MANUAL,
            contribution_period=date(2026, 11, 1),
            reference=f"EXTERNAL-E2E-CONTRIBUTION-{i}",
        )
    ExternalService.appoint_custodian(
        group_id=group.pk, appointed_by=manager,
        group_member_id=memberships[treasurer.pk].pk,
        provider=TreasuryMandate.Provider.MPESA,
        wallet_alias="M-Pesa ***1402",
    )
    d = DisbursementService.create(
        group_id=group.pk, cycle_number=1, created_by=manager,
    )
    DisbursementService.approve(disbursement_id=d.pk, approved_by=treasurer)
    DisbursementService.approve(disbursement_id=d.pk, approved_by=voter)
    d.refresh_from_db()
    assert d.status == Disbursement.Status.APPROVED
    return group, manager, beneficiary, treasurer, d, rotation


@pytest.mark.django_db(transaction=True)
def test_actual_chain_anchor_for_external_claim_and_beneficiary_acknowledgment():
    assert connection.vendor == "postgresql"
    assert settings.BLOCKCHAIN_CHAIN_ID == 1337
    w3 = _node()
    contract = _deploy(w3, _artifact("DisbursementRegistry"), w3.eth.accounts[0])

    with override_settings(
        NON_CUSTODIAL_DISBURSEMENTS_ENABLED=True,
        SANDBOX_PAYMENTS_ENABLED=False,
        DISBURSEMENT_REGISTRY_ADDRESS=contract.address,
    ):
        group, manager, beneficiary, treasurer, d, rotation = _approved_fixture()
        client = DisbursementRegistryClient()
        opened = ExternalService.open_for_external_payment(
            disbursement_id=d.pk, requested_by=manager, client=client,
        )
        assert opened.status == Disbursement.Status.AWAITING_PAYMENT
        assert client.get(str(d.pk))["authorized"]

        declared = ExternalService.report_external_payment(
            disbursement_id=d.pk, reported_by=treasurer,
            reference="MPESA-OUTSIDE-MONO-0001",
        )
        assert declared.status == Disbursement.Status.AWAITING_CONFIRMATION
        confirmation = ExternalService.respond_to_report(
            disbursement_id=d.pk, responded_by=beneficiary, received=True,
        )
        assert confirmation.status == Disbursement.Status.EVIDENCE_PENDING
        rotation.refresh_from_db()
        assert rotation.status == RotationOrder.Status.CURRENT
        assert SandboxTransfer.objects.count() == 0

        completed = ExternalService.finalize_acknowledged_payment(
            disbursement_id=d.pk, requested_by=manager, client=client,
        )
        assert completed.status == Disbursement.Status.COMPLETED
        proof = client.get_beneficiary_acknowledgment(str(d.pk))
        assert proof["exists"] is True
        report = ExternalPaymentReport.objects.get(disbursement=d)
        assert proof["evidence_hash"] == ExternalService.acknowledgment_hash(report)
        assert client.get(str(d.pk))["settled"] is False
        rotation.refresh_from_db()
        assert rotation.status == RotationOrder.Status.COMPLETED
        assert SandboxTransfer.objects.count() == 0

        height = w3.eth.block_number
        again = ExternalService.finalize_acknowledged_payment(
            disbursement_id=d.pk, requested_by=manager, client=client,
        )
        assert again.status == Disbursement.Status.COMPLETED
        assert w3.eth.block_number == height

    print(
        "NON_CUSTODIAL_E2E postgres=True ganache=True rn06=True "
        "treasurer_declared=True beneficiary_acknowledged=True "
        "authorization_anchored=True acknowledgment_anchored=True "
        "provider_settlement_verified=False funds_transferred_by_mono=False"
    )


@pytest.mark.django_db(transaction=True)
def test_uncertain_acknowledgment_mined_before_timeout_recovers_without_rebroadcast():
    assert connection.vendor == "postgresql"
    w3 = _node()
    contract = _deploy(w3, _artifact("DisbursementRegistry"), w3.eth.accounts[0])
    with override_settings(
        NON_CUSTODIAL_DISBURSEMENTS_ENABLED=True,
        SANDBOX_PAYMENTS_ENABLED=False,
        DISBURSEMENT_REGISTRY_ADDRESS=contract.address,
    ):
        group, manager, beneficiary, treasurer, d, rotation = _approved_fixture()
        client = DisbursementRegistryClient()
        ExternalService.open_for_external_payment(
            disbursement_id=d.pk, requested_by=manager, client=client,
        )
        ExternalService.report_external_payment(
            disbursement_id=d.pk, reported_by=treasurer,
            reference="MPESA-OUTSIDE-MONO-0002",
        )
        ExternalService.respond_to_report(
            disbursement_id=d.pk, responded_by=beneficiary, received=True,
        )
        original = client.anchor_beneficiary_acknowledgment

        def mined_then_timeout(*args, **kwargs):
            receipt = original(*args, **kwargs)
            assert receipt.status
            raise TimeoutError("Synthetic loss of acknowledgment RPC response")

        with patch.object(
            client, "anchor_beneficiary_acknowledgment", side_effect=mined_then_timeout,
        ):
            with pytest.raises(TimeoutError):
                ExternalService.finalize_acknowledged_payment(
                    disbursement_id=d.pk, requested_by=manager, client=client,
                )

        d.refresh_from_db()
        assert d.status == Disbursement.Status.EVIDENCE_PENDING
        height = w3.eth.block_number
        finished = ExternalService.finalize_acknowledged_payment(
            disbursement_id=d.pk, requested_by=manager, client=client,
        )
        assert finished.status == Disbursement.Status.COMPLETED
        assert w3.eth.block_number == height
        assert SandboxTransfer.objects.count() == 0
    print("NON_CUSTODIAL_RECOVERY acknowledged_mined=True duplicate_broadcast=False")

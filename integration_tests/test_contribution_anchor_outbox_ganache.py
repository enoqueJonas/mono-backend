"""PostgreSQL + real Ganache crash/reconciliation proof for contribution anchors.

The failure injected here is *local receipt persistence* after a mined EVM
transaction. No payment provider, real user, or production signer is involved.
"""
from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.conf import settings
from django.db import connection
from django.test import override_settings

from accounts.models import User
from blockchain.clients.contribution_registry_client import ContributionRegistryClient
from blockchain.models import BlockchainAnchor, BlockchainAnchorStatus
from contributions.models import ContributionAnchorIntent
from contributions.services.anchor_outbox_service import ContributionAnchorOutboxService
from contributions.services.contribution_service import ContributionService
from groups.models import Group, GroupMember, GroupSettings
from integration_tests.test_registry_custody_ganache import _artifact, _deploy, _node


@pytest.mark.django_db(transaction=True)
def test_mined_contribution_recovers_after_sql_receipt_write_failure():
    assert connection.vendor == "postgresql"
    assert settings.DATABASES["default"]["NAME"] in {
        "mono_integration", "test_mono_integration",
    }

    w3 = _node()
    contract = _deploy(
        w3, _artifact("ContributionRegistry"), w3.eth.accounts[0]
    )
    manager = User.objects.create_user(
        phone_number="+258841995311", password="synthetic-only-test"
    )
    member_user = User.objects.create_user(
        phone_number="+258841995312", password="synthetic-only-test"
    )
    group = Group.objects.create(name="RN06 EVM outbox synthetic group")
    GroupSettings.objects.create(
        group=group, version=1, is_active=True,
        contribution_amount=Decimal("1000.00"), currency="MZN",
        contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
        maximum_members=4,
        rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
        requires_consensus=True, allow_manual_contributions=True,
    )
    GroupMember.objects.create(
        group=group, user=manager,
        role=GroupMember.Role.MANAGER, status=GroupMember.Status.ACTIVE,
    )
    member = GroupMember.objects.create(
        group=group, user=member_user,
        role=GroupMember.Role.MEMBER, status=GroupMember.Status.ACTIVE,
    )

    original_send = ContributionRegistryClient.register_contribution
    rpc_was_after_commit = []

    def ensure_no_sql_transaction_during_rpc(client, *args, **kwargs):
        rpc_was_after_commit.append(not connection.in_atomic_block)
        assert not connection.in_atomic_block, "EVM RPC happened inside SQL atomic"
        return original_send(client, *args, **kwargs)

    with override_settings(CONTRIBUTION_REGISTRY_ADDRESS=contract.address):
        with patch.object(
            ContributionRegistryClient,
            "register_contribution",
            new=ensure_no_sql_transaction_during_rpc,
        ), patch(
            "blockchain.services.contribution_anchor_service.BlockchainAnchor.objects.create",
            side_effect=RuntimeError("synthetic receipt persistence failure"),
        ):
            contribution = ContributionService.register_manual_contribution(
                group_id=group.pk,
                registered_by=manager,
                data={
                    "group_member_id": member.pk,
                    "amount": Decimal("1000.00"),
                    "contribution_period": date(2026, 11, 1),
                },
            )

        intent = ContributionAnchorIntent.objects.get(contribution=contribution)
        assert rpc_was_after_commit == [True]
        assert intent.status == ContributionAnchorIntent.Status.PENDING
        assert intent.last_error_code == "RuntimeError"
        assert not BlockchainAnchor.objects.filter(contribution=contribution).exists()
        assert contract.functions.contributionExists(
            ContributionRegistryClient._uuid_to_bytes32(str(contribution.pk))
        ).call()
        before = w3.eth.block_number

        # On re-entry, the worker must read the original event rather than
        # sending a second transaction and overwriting the SQL record.
        result = ContributionAnchorOutboxService.process(intent.pk)
        assert result == ContributionAnchorIntent.Status.CONFIRMED
        intent.refresh_from_db()
        assert intent.attempt_count == 2
        assert BlockchainAnchor.objects.filter(contribution=contribution).count() == 1
        saved = BlockchainAnchor.objects.get(contribution=contribution)
        assert saved.status == BlockchainAnchorStatus.CONFIRMED
        assert saved.content_hash == intent.content_hash
        assert w3.eth.block_number == before, "Recovery sent an unnecessary EVM transaction"

        assert ContributionAnchorOutboxService.process(intent.pk) == (
            ContributionAnchorIntent.Status.CONFIRMED
        )
        assert BlockchainAnchor.objects.filter(contribution=contribution).count() == 1

    print(
        "CONTRIBUTION_OUTBOX_E2E "
        "rpc_outside_sql=True mined_before_receipt_failure=True "
        "event_recovery=True duplicate_send=False"
    )

@pytest.mark.django_db(transaction=True)
def test_unknown_broadcast_mined_transaction_reconciles_only_by_event():
    """A transport timeout AFTER mining must never cause blind rebroadcast."""
    assert connection.vendor == "postgresql"
    w3 = _node()
    contract = _deploy(w3, _artifact("ContributionRegistry"), w3.eth.accounts[0])
    manager = User.objects.create_user(
        phone_number="+258841995321", password="synthetic-only-test"
    )
    member_user = User.objects.create_user(
        phone_number="+258841995322", password="synthetic-only-test"
    )
    group = Group.objects.create(name="RN06 uncertain-broadcast synthetic group")
    GroupSettings.objects.create(
        group=group, version=1, is_active=True,
        contribution_amount=Decimal("1000.00"), currency="MZN",
        contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
        maximum_members=4,
        rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
        requires_consensus=True, allow_manual_contributions=True,
    )
    GroupMember.objects.create(
        group=group, user=manager,
        role=GroupMember.Role.MANAGER, status=GroupMember.Status.ACTIVE,
    )
    member = GroupMember.objects.create(
        group=group, user=member_user,
        role=GroupMember.Role.MEMBER, status=GroupMember.Status.ACTIVE,
    )

    original_send = ContributionRegistryClient.register_contribution

    def submit_then_report_timeout(client, *args, **kwargs):
        receipt = original_send(client, *args, **kwargs)
        assert receipt.status, "Expected synthetic EVM transaction to be mined"
        raise TimeoutError("synthetic RPC timeout after mining")

    with override_settings(CONTRIBUTION_REGISTRY_ADDRESS=contract.address):
        with patch.object(
            ContributionRegistryClient,
            "register_contribution",
            new=submit_then_report_timeout,
        ):
            contribution = ContributionService.register_manual_contribution(
                group_id=group.pk,
                registered_by=manager,
                data={
                    "group_member_id": member.pk,
                    "amount": Decimal("1000.00"),
                    "contribution_period": date(2026, 11, 1),
                },
            )

        intent = ContributionAnchorIntent.objects.get(contribution=contribution)
        assert intent.status == ContributionAnchorIntent.Status.REVIEW_REQUIRED
        assert intent.last_error_code == "ContributionAnchorSubmissionUncertain"
        assert not BlockchainAnchor.objects.filter(contribution=contribution).exists()
        assert contract.functions.contributionExists(
            ContributionRegistryClient._uuid_to_bytes32(str(contribution.pk))
        ).call()
        at_mining = w3.eth.block_number

        # An ordinary scheduled process must never retry REVIEW_REQUIRED.
        assert ContributionAnchorOutboxService.process(intent.pk) == (
            ContributionAnchorIntent.Status.REVIEW_REQUIRED
        )
        assert w3.eth.block_number == at_mining

        # Explicit operator reconciliation can inspect, verify, and persist
        # the same transaction, but is prohibited from broadcasting anew.
        assert ContributionAnchorOutboxService.process(
            intent.pk, reconcile_only=True
        ) == ContributionAnchorIntent.Status.CONFIRMED
        intent.refresh_from_db()
        assert intent.attempt_count == 2
        assert BlockchainAnchor.objects.filter(contribution=contribution).count() == 1
        assert w3.eth.block_number == at_mining

    print(
        "CONTRIBUTION_UNCERTAIN_SEND_E2E "
        "mined_then_timeout=True quarantined=True "
        "review_only_recovered=True second_broadcast=False"
    )

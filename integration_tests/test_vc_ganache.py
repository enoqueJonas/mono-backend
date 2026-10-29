"""Full Django/API -> Web3 -> Ganache integration of a signed contribution VC.

Requires a separately running local Ganache funded with the fixed *test-only*
private key declared in config.settings_test. Never use production keys.
The contribution is seeded in the test DB (wallet confirmation is NOT tested).
"""
import json
import os
import time
from copy import deepcopy
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from django.conf import settings
from rest_framework.test import APIClient
from web3 import Web3

from accounts.models import User
from contributions.models import Contribution
from credentials.models import VerifiableCredential
from groups.models import Group, GroupMember, GroupSettings
from identity.services.did_service import DIDService

GANACHE_URL = os.environ.get("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "blockchain" / "abi" / "CredentialRegistry.json"
)


def _node():
    web3 = Web3(Web3.HTTPProvider(GANACHE_URL, request_kwargs={"timeout": 5}))
    for _ in range(30):
        if web3.is_connected():
            return web3
        time.sleep(1)
    pytest.fail("Ganache JSON-RPC unavailable; integration test not executed")


@pytest.mark.django_db(transaction=True)
def test_signed_vc_emission_verification_revocation_on_ganache():
    web3 = _node()
    assert web3.eth.chain_id == 1337

    artifact = json.loads(CONTRACT_ARTIFACT.read_text(encoding="utf-8"))
    contract_factory = web3.eth.contract(
        abi=artifact["abi"], bytecode=artifact["bytecode"]
    )
    deploy_tx = contract_factory.constructor().transact(
        {"from": web3.eth.accounts[0]}
    )
    deploy_receipt = web3.eth.wait_for_transaction_receipt(deploy_tx)
    assert deploy_receipt.status == 1
    contract = web3.eth.contract(
        address=deploy_receipt.contractAddress, abi=artifact["abi"]
    )

    # App settings are evaluated at the moment AnchorService constructs its client.
    settings.CREDENTIAL_REGISTRY_ADDRESS = deploy_receipt.contractAddress
    settings.BLOCKCHAIN_RPC_URL = GANACHE_URL
    settings.BLOCKCHAIN_CHAIN_ID = 1337

    manager = User.objects.create_user(
        phone_number="+258841000001", password="test-strong-password"
    )
    holder = User.objects.create_user(
        phone_number="+258841000002", password="test-strong-password"
    )
    group = Group.objects.create(name="Grupo de Teste de Integração")
    group_settings = GroupSettings.objects.create(
        group=group,
        version=1,
        contribution_amount=Decimal("1000.00"),
        currency="MZN",
        contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
        maximum_members=10,
        rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
        requires_consensus=False,
        allow_manual_contributions=True,
        is_active=True,
    )
    GroupMember.objects.create(
        group=group, user=manager,
        role=GroupMember.Role.MANAGER, status=GroupMember.Status.ACTIVE,
    )
    membership = GroupMember.objects.create(
        group=group, user=holder,
        role=GroupMember.Role.MEMBER, status=GroupMember.Status.ACTIVE,
    )
    DIDService.create_for_group(group=group)
    DIDService.create_for_user(user=holder)
    Contribution.objects.create(
        member=membership, group_settings=group_settings,
        amount=Decimal("1000.00"), currency="MZN",
        status=Contribution.Status.CONFIRMED,
        source=Contribution.Source.MANUAL,
        reference="AUDIT-CONTRIB-001", contribution_period=date(2026, 9, 1),
    )

    client = APIClient()
    client.force_authenticate(user=manager)
    issue = client.post(
        f"/api/v1/credentials/{group.id}/credentials/",
        {
            "group_member_id": str(membership.id),
            "period_start": "2026-09-01",
            "period_end": "2026-09-30",
        },
        format="json",
    )
    assert issue.status_code == 201, issue.data
    record = VerifiableCredential.objects.get(group_member=membership)
    signed = record.credential_document
    assert signed["proof"]["proofValue"].startswith("z")
    assert record.credential_id == signed["id"]
    assert signed["validUntil"]
    from blockchain.utils.hashing import HashingService
    assert record.credential_hash == HashingService.hash_json_hex(signed)
    stored = contract.functions.getCredential(
        bytes.fromhex(record.credential_hash)
    ).call()
    assert stored[0] is True and stored[1] is False

    client.force_authenticate(user=None)
    verified = client.post(
        "/api/v1/credentials/verify/", {"credential": signed}, format="json"
    )
    assert verified.status_code == 200, verified.data
    assert verified.data["data"]["valid"] is True

    altered = deepcopy(signed)
    altered["credentialSubject"]["contributionHistory"]["totalAmount"] = "9900.00"
    tampered_response = client.post(
        "/api/v1/credentials/verify/", {"credential": altered}, format="json"
    )
    assert tampered_response.status_code == 200
    assert tampered_response.data["data"]["valid"] is False

    # A holder must not be able to revoke their own credential.
    # Reject before sending a transaction to Ganache.
    client.force_authenticate(user=holder)
    denied = client.post(
        f"/api/v1/credentials/{record.id}/revoke/",
        {"reason": "unauthorised"}, format="json"
    )
    assert denied.status_code == 403, denied.data
    before_authorised_revoke = contract.functions.getCredential(
        bytes.fromhex(record.credential_hash)
    ).call()
    assert before_authorised_revoke[1] is False

    client.force_authenticate(user=manager)
    revoked_response = client.post(
        f"/api/v1/credentials/{record.id}/revoke/",
        {"reason": "Revisão experimental"}, format="json"
    )
    assert revoked_response.status_code == 200, revoked_response.data
    state = contract.functions.getCredential(
        bytes.fromhex(record.credential_hash)
    ).call()
    assert state[0] is True and state[1] is True

    client.force_authenticate(user=None)
    after_revoke = client.post(
        "/api/v1/credentials/verify/", {"credential": signed}, format="json"
    )
    assert after_revoke.status_code == 200
    assert after_revoke.data["data"]["valid"] is False

    # Evidence summary is intentionally test-only; never log private keys/PII.
    print(
        f"GANACHE_EVIDENCE chain_id={web3.eth.chain_id}"
        f" contract={contract.address} deployment_tx={deploy_tx.hex()}"
        f" hash={record.credential_hash} verified_before=True"
        f" tampered=False revoked=True verified_after=False"
    )

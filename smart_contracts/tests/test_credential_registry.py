import pytest

from brownie import CredentialRegistry, accounts, reverts, web3

import hashlib


@pytest.fixture
def owner():
    return accounts[0]


@pytest.fixture
def registry(owner):
    return CredentialRegistry.deploy(
        {"from": owner}
    )


@pytest.fixture
def credential_hash():
    return hashlib.sha256(
        b"sample-verifiable-credential"
    ).digest()


def test_registers_credential_hash(
    registry,
    owner,
    credential_hash,
):
    tx = registry.registerCredentialHash(
        credential_hash,
        {"from": owner},
    )

    assert tx.status == 1

    assert registry.credentialExists(
        credential_hash
    ) is True

    stored = registry.getCredential(
        credential_hash
    )

    assert stored[0] is True
    assert stored[1] is False
    assert stored[2] > 0
    assert stored[3] == owner

    event = tx.events["CredentialAnchored"]

    assert len(event) == 1
    assert str(event["credentialHash"]) == web3.to_hex(
        credential_hash
    )
    assert event["anchoredBy"] == owner


def test_rejects_duplicate_hash(
    registry,
    owner,
    credential_hash,
):
    registry.registerCredentialHash(
        credential_hash,
        {"from": owner},
    )

    with reverts():
        registry.registerCredentialHash(
            credential_hash,
            {"from": owner},
        )


def test_reads_existing_credential(
    registry,
    owner,
    credential_hash,
):
    registry.registerCredentialHash(
        credential_hash,
        {"from": owner},
    )

    (
        exists,
        revoked,
        anchored_at,
        anchored_by,
    ) = registry.getCredential(
        credential_hash
    )

    assert exists is True
    assert revoked is False
    assert anchored_at > 0
    assert anchored_by == owner

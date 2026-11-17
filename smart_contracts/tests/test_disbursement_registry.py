import pytest
from brownie import DisbursementRegistry, reverts


def _b32(n):
    return n.to_bytes(32, "big")


@pytest.fixture
def registry(accounts):
    return DisbursementRegistry.deploy({"from": accounts[0]})


def test_authorization_then_verified_settlement_proof(registry, accounts):
    disbursement_id, auth_hash, settlement_hash = _b32(1), _b32(2), _b32(3)
    registry.recordAuthorization(disbursement_id, auth_hash, {"from": accounts[0]})
    a, s, authorized_at, settled_at, authorized, settled = registry.getDisbursement(disbursement_id)
    assert bytes(a) == auth_hash
    assert bytes(s) == _b32(0)
    assert authorized_at > 0
    assert settled_at == 0
    assert authorized and not settled

    registry.recordSettlement(disbursement_id, settlement_hash, {"from": accounts[0]})
    a, s, authorized_at, settled_at, authorized, settled = registry.getDisbursement(disbursement_id)
    assert bytes(s) == settlement_hash
    assert authorized and settled
    assert settled_at >= authorized_at


def test_prevents_settlement_before_authorization(registry, accounts):
    with reverts("Authorization not recorded"):
        registry.recordSettlement(_b32(1), _b32(4), {"from": accounts[0]})


def test_rejects_duplicate_or_modified_authorization(registry, accounts):
    registry.recordAuthorization(_b32(1), _b32(2), {"from": accounts[0]})
    with reverts("Authorization already recorded"):
        registry.recordAuthorization(_b32(1), _b32(3), {"from": accounts[0]})


def test_rejects_duplicate_settlement(registry, accounts):
    registry.recordAuthorization(_b32(1), _b32(2), {"from": accounts[0]})
    registry.recordSettlement(_b32(1), _b32(3), {"from": accounts[0]})
    with reverts("Settlement already recorded"):
        registry.recordSettlement(_b32(1), _b32(4), {"from": accounts[0]})


def test_only_operator_can_write(registry, accounts):
    with reverts("Only authorized operator"):
        registry.recordAuthorization(_b32(1), _b32(2), {"from": accounts[1]})
    registry.recordAuthorization(_b32(1), _b32(2), {"from": accounts[0]})
    with reverts("Only authorized operator"):
        registry.recordSettlement(_b32(1), _b32(3), {"from": accounts[1]})


def test_rejects_empty_ids_and_hashes(registry, accounts):
    with reverts("Invalid disbursement ID"):
        registry.recordAuthorization(_b32(0), _b32(2), {"from": accounts[0]})
    with reverts("Invalid authorization hash"):
        registry.recordAuthorization(_b32(1), _b32(0), {"from": accounts[0]})
    registry.recordAuthorization(_b32(1), _b32(2), {"from": accounts[0]})
    with reverts("Invalid settlement hash"):
        registry.recordSettlement(_b32(1), _b32(0), {"from": accounts[0]})

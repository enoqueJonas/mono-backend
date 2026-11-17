import pytest
from brownie import DisbursementRegistry, accounts, reverts


@pytest.fixture
def registry():
    return DisbursementRegistry.deploy({"from": accounts[0]})


def test_only_operator_can_anchor_intent(registry):
    payout_id = bytes.fromhex("01".zfill(64))
    proof = bytes.fromhex("02".zfill(64))
    with reverts("Only authorized operator"):
        registry.anchorIntent(payout_id, proof, {"from": accounts[1]})
    registry.anchorIntent(payout_id, proof, {"from": accounts[0]})
    saved = registry.getProof(payout_id)
    assert str(saved[0]).removeprefix("0x").lower() == proof.hex()
    assert saved[2] > 0


def test_settlement_requires_intent_and_cannot_be_replaced(registry):
    payout_id = bytes.fromhex("11".zfill(64))
    intent = bytes.fromhex("22".zfill(64))
    settlement = bytes.fromhex("33".zfill(64))
    with reverts("Intent missing"):
        registry.anchorSettlement(payout_id, settlement, {"from": accounts[0]})
    registry.anchorIntent(payout_id, intent, {"from": accounts[0]})
    with reverts("Intent already anchored"):
        registry.anchorIntent(payout_id, intent, {"from": accounts[0]})
    with reverts("Only authorized operator"):
        registry.anchorSettlement(payout_id, settlement, {"from": accounts[1]})
    registry.anchorSettlement(payout_id, settlement, {"from": accounts[0]})
    saved = registry.getProof(payout_id)
    assert str(saved[1]).removeprefix("0x").lower() == settlement.hex()
    assert saved[3] >= saved[2]
    with reverts("Settlement already anchored"):
        registry.anchorSettlement(payout_id, settlement, {"from": accounts[0]})

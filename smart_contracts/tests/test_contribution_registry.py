import pytest
from brownie import ContributionRegistry, reverts


def _bytes32(value: int) -> bytes:
    return value.to_bytes(32, byteorder="big")


@pytest.fixture
def registry(accounts):
    return ContributionRegistry.deploy({"from": accounts[0]})


def test_registers_and_reads_contribution(registry, accounts):
    contribution_id = _bytes32(1)
    contribution_hash = _bytes32(2)

    registry.registerContribution(
        contribution_id,
        contribution_hash,
        {"from": accounts[0]},
    )

    stored_hash, anchored_at, anchored_by, exists = (
        registry.getContribution(contribution_id)
    )

    assert stored_hash == contribution_hash
    assert anchored_at > 0
    assert anchored_by == accounts[0]
    assert exists is True
    assert registry.contributionExists(contribution_id) is True


def test_rejects_duplicate_contribution(registry, accounts):
    contribution_id = _bytes32(1)
    contribution_hash = _bytes32(2)

    registry.registerContribution(
        contribution_id,
        contribution_hash,
        {"from": accounts[0]},
    )

    with reverts("Contribution already anchored"):
        registry.registerContribution(
            contribution_id,
            contribution_hash,
            {"from": accounts[0]},
        )

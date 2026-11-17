import pytest
from blockchain.clients.disbursement_registry_client import DisbursementRegistryClient


def test_id_is_bytes32_and_has_fixed_size():
    value = DisbursementRegistryClient._id_bytes32(
        "12345678-1234-5678-1234-567812345678"
    )
    assert len(value) == 32
    assert value[:16] == bytes(16)


def test_hash_rejects_non_sha256_value():
    with pytest.raises(ValueError, match="exactly 32"):
        DisbursementRegistryClient._hash_bytes32("fa")


def test_hash_accepts_sha256_digest():
    value = DisbursementRegistryClient._hash_bytes32("ef" * 32)
    assert value == bytes.fromhex("ef" * 32)

import pytest

from blockchain.utils.hashing import HashingService


def test_sha256_string_returns_32_bytes():
    result = HashingService.sha256_string(
        "sample-verifiable-credential"
    )

    assert isinstance(result, bytes)
    assert len(result) == 32


def test_equivalent_json_documents_generate_same_hash():
    first_document = {
        "credentialSubject": {
            "name": "Enoque",
            "status": "ACTIVE",
        },
        "issuer": "did:mono:issuer-001",
    }

    second_document = {
        "issuer": "did:mono:issuer-001",
        "credentialSubject": {
            "status": "ACTIVE",
            "name": "Enoque",
        },
    }

    first_hash = HashingService.hash_json(
        first_document
    )

    second_hash = HashingService.hash_json(
        second_document
    )

    assert first_hash == second_hash


def test_different_documents_generate_different_hashes():
    first_document = {
        "credentialSubject": {
            "status": "ACTIVE",
        }
    }

    second_document = {
        "credentialSubject": {
            "status": "REVOKED",
        }
    }

    assert (
        HashingService.hash_json(first_document)
        != HashingService.hash_json(second_document)
    )


def test_unicode_is_serialized_deterministically():
    document = {
        "name": "João",
        "country": "Moçambique",
    }

    canonical_document = (
        HashingService.canonicalize_json(document)
    )

    assert "João" in canonical_document
    assert "Moçambique" in canonical_document


def test_hash_json_rejects_non_dictionary():
    with pytest.raises(
        TypeError,
        match="must be a dictionary",
    ):
        HashingService.hash_json(
            "invalid-document"  # type: ignore[arg-type]
        )

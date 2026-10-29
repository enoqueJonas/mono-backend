"""Verification tests: forged, revoked, expired and valid anchored credentials."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from credentials.application.services.verify_credential_service import VerifyCredentialService


def make_credential(*, expiry_days=3):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "id": "urn:uuid:123",
        "type": ["VerifiableCredential", "ContributionHistoryCredential"],
        "issuer": "did:key:issuer",
        "issuanceDate": (now - timedelta(days=1)).isoformat().replace("+00:00", "Z"),
        "validUntil": (now + timedelta(days=expiry_days)).isoformat().replace("+00:00", "Z"),
        "credentialSubject": {"id": "did:key:holder"},
        "proof": {
            "type": "MonoEd25519Signature2026",
            "proofPurpose": "assertionMethod",
            "created": (now - timedelta(days=1)).isoformat().replace("+00:00", "Z"),
            "verificationMethod": "did:key:issuer#key",
            "proofValue": "zvalidSignature",
        },
    }


def make_service(*, exists=True, revoked=False, signer_valid=True, trusted=True):
    anchor = Mock()
    anchor.credential_exists.return_value = exists
    anchor.get_credential.return_value = {"exists": exists, "revoked": revoked}
    signer = Mock()
    signer.verify.return_value = signer_valid
    lookup = Mock(return_value=Mock() if trusted else None)
    return VerifyCredentialService(
        anchor_service=anchor,
        signer=signer,
        issuer_lookup=lookup,
    ), anchor


def test_valid_credential_checks_signature_and_on_chain_revocation():
    service, anchor = make_service()
    assert service.verify(credential=make_credential()) is True
    anchor.credential_exists.assert_called_once()
    anchor.get_credential.assert_called_once()


@pytest.mark.parametrize("flag", ["revoked", "missing", "forged", "untrusted"])
def test_invalid_status_or_issuer_is_rejected(flag):
    service, anchor = make_service(
        exists=flag != "missing",
        revoked=flag == "revoked",
        signer_valid=flag != "forged",
        trusted=flag != "untrusted",
    )
    assert service.verify(credential=make_credential()) is False


def test_expired_credential_is_rejected_without_chain_query():
    service, anchor = make_service()
    assert service.verify(credential=make_credential(expiry_days=-2)) is False
    anchor.get_credential.assert_not_called()


def test_unsigned_credential_is_rejected():
    service, anchor = make_service()
    doc = make_credential()
    doc.pop("proof")
    assert service.verify(credential=doc) is False
    anchor.get_credential.assert_not_called()


def test_modified_document_requires_new_hash():
    service, anchor = make_service()
    original = make_credential()
    altered = deepcopy(original)
    altered["credentialSubject"]["id"] = "did:key:attacker"
    assert service.verify(credential=original)
    first_hash = anchor.get_credential.call_args.kwargs["credential_hash"].value
    assert service.verify(credential=altered)
    second_hash = anchor.get_credential.call_args.kwargs["credential_hash"].value
    assert first_hash != second_hash


def test_missing_or_malformed_timestamps_fail_closed():
    service, anchor = make_service()
    for raw in (None, "no-date", "2027-01-01T12:00:00"):
        doc = make_credential()
        doc["validUntil"] = raw
        assert service.verify(credential=doc) is False
    anchor.get_credential.assert_not_called()


def test_issuer_lookup_rejects_unknown_issuer():
    service, anchor = make_service(trusted=False)
    assert service.verify(credential=make_credential()) is False
    anchor.get_credential.assert_not_called()

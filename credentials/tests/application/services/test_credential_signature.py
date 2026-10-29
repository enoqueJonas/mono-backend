"""Exercise real Ed25519 signing and verification without connecting to Ganache."""
from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

import base58
from nacl.signing import SigningKey

from credentials.services.credential_signer import CredentialSigner


def test_signature_detects_modified_content_and_invalid_proof():
    key = SigningKey.generate()
    multibase = "z" + base58.b58encode(
        bytes([0xED, 0x01]) + key.verify_key.encode()
    ).decode("ascii")
    did = f"did:key:{multibase}"
    issuer = SimpleNamespace(
        did=did,
        public_key_multibase=multibase,
        encrypted_private_key="encrypted-test-placeholder",
        verification_method_id=f"{did}#{multibase}",
    )
    document = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "id": "urn:uuid:credential-001",
        "type": ["VerifiableCredential"],
        "issuer": did,
        "issuanceDate": "2026-10-28T10:00:00Z",
        "validUntil": "2027-10-28T10:00:00Z",
        "credentialSubject": {"id": "did:key:holder", "totalAmount": "2500.00"},
    }
    with patch(
        "credentials.services.credential_signer.decrypt_private_key",
        return_value=key.encode(),
    ):
        signed = CredentialSigner.sign(
            document=document,
            issuer_identity=issuer,
            created_at=datetime(2026, 10, 28, 10, 0, tzinfo=timezone.utc),
        ).document

    assert CredentialSigner.verify(
        signed_document=signed, issuer_identity=issuer
    )

    altered = deepcopy(signed)
    altered["credentialSubject"]["totalAmount"] = "9999.00"
    assert not CredentialSigner.verify(
        signed_document=altered, issuer_identity=issuer
    )

    wrong_purpose = deepcopy(signed)
    wrong_purpose["proof"]["proofPurpose"] = "authentication"
    assert not CredentialSigner.verify(
        signed_document=wrong_purpose, issuer_identity=issuer
    )

"""Prototype Ed25519 detached proof over deterministic JSON bytes.

This is an application-specific proof format, not W3C Data Integrity/JCS.
"""
import base64

import base58
from nacl.exceptions import BadSignatureError, CryptoError
from nacl.signing import SigningKey, VerifyKey

from blockchain.utils.hashing import HashingService
from identity.utils.keys import decrypt_private_key

PROOF_TYPE = "Ed25519CanonicalJsonProof2026"


def sign_credential(document: dict, group_did) -> dict:
    if document.get("issuer") != group_did.did:
        raise ValueError("Credential issuer does not match signing DID.")
    if "proof" in document:
        raise ValueError("Document must be unsigned.")
    payload = HashingService.canonicalize_json(document).encode("utf-8")
    signature = SigningKey(
        decrypt_private_key(group_did.encrypted_private_key)
    ).sign(payload).signature
    return {
        "type": PROOF_TYPE,
        "verificationMethod": group_did.verification_method_id,
        "proofValue": base64.urlsafe_b64encode(signature).decode("ascii"),
    }


def verify_signature(document: dict) -> bool:
    try:
        proof = document["proof"]
        issuer = document["issuer"]
        if not isinstance(proof, dict) or proof.get("type") != PROOF_TYPE:
            return False
        if not isinstance(issuer, str) or not issuer.startswith("did:key:z"):
            return False
        public_multibase = issuer[len("did:key:"):]
        if proof.get("verificationMethod") != f"{issuer}#{public_multibase}":
            return False
        public_key = base58.b58decode(public_multibase[1:])
        if len(public_key) != 34 or public_key[:2] != bytes([0xED, 0x01]):
            return False
        signature = base64.b64decode(proof["proofValue"], altchars=b"-_", validate=True)
        unsigned = {key: value for key, value in document.items() if key != "proof"}
        payload = HashingService.canonicalize_json(unsigned).encode("utf-8")
        VerifyKey(public_key[2:]).verify(payload, signature)
        return True
    except (KeyError, TypeError, ValueError, BadSignatureError, CryptoError, OverflowError):
        return False

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import base58
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey

from credentials.utils.canonical_json import canonicalize_json
from identity.models import GroupDID
from identity.utils.keys import decrypt_private_key


@dataclass(frozen=True)
class SignedCredential:
    document: dict[str, Any]
    signature_multibase: str


class CredentialSignatureError(Exception):
    """Raised when a credential cannot be signed or verified."""


class CredentialSigner:
    """
    Application-level Ed25519 credential signer.

    The signed payload is the deterministic credential document
    without the `proof` property.
    """

    PROOF_TYPE = "MonoEd25519Signature2026"
    PROOF_PURPOSE = "assertionMethod"

    @classmethod
    def sign(
        cls,
        *,
        document: dict[str, Any],
        issuer_identity: GroupDID,
        created_at: datetime | None = None,
    ) -> SignedCredential:
        if "proof" in document:
            raise CredentialSignatureError(
                "The document is already signed."
            )

        private_key_bytes = decrypt_private_key(
            issuer_identity.encrypted_private_key
        )

        signing_key = SigningKey(private_key_bytes)
        canonical_document = canonicalize_json(document)

        signature_bytes = signing_key.sign(
            canonical_document
        ).signature

        signature_multibase = (
            "z"
            + base58.b58encode(signature_bytes).decode("ascii")
        )

        proof_created_at = created_at or datetime.now(timezone.utc)

        proof = {
            "type": cls.PROOF_TYPE,
            "created": cls._format_datetime(proof_created_at),
            "verificationMethod": (
                issuer_identity.verification_method_id
            ),
            "proofPurpose": cls.PROOF_PURPOSE,
            "proofValue": signature_multibase,
        }

        signed_document = deepcopy(document)
        signed_document["proof"] = proof

        return SignedCredential(
            document=signed_document,
            signature_multibase=signature_multibase,
        )

    @classmethod
    def verify(
        cls,
        *,
        signed_document: dict[str, Any],
        issuer_identity: GroupDID,
    ) -> bool:
        proof = signed_document.get("proof")

        if not isinstance(proof, dict):
            return False

        if proof.get("type") != cls.PROOF_TYPE:
            return False

        if (
            proof.get("verificationMethod")
            != issuer_identity.verification_method_id
        ):
            return False

        proof_value = proof.get("proofValue")

        if not isinstance(proof_value, str):
            return False

        if not proof_value.startswith("z"):
            return False

        unsigned_document = deepcopy(signed_document)
        unsigned_document.pop("proof", None)

        try:
            signature_bytes = base58.b58decode(
                proof_value[1:]
            )

            verify_key = cls._build_verify_key(
                public_key_multibase=(
                    issuer_identity.public_key_multibase
                )
            )

            verify_key.verify(
                canonicalize_json(unsigned_document),
                signature_bytes,
            )

            return True

        except (
            ValueError,
            BadSignatureError,
        ):
            return False

    @staticmethod
    def _build_verify_key(
        *,
        public_key_multibase: str,
    ) -> VerifyKey:
        if not public_key_multibase.startswith("z"):
            raise CredentialSignatureError(
                "Unsupported public key encoding."
            )

        decoded = base58.b58decode(
            public_key_multibase[1:]
        )

        # did:key Ed25519 multicodec prefix: 0xed01
        if decoded[:2] != bytes([0xED, 0x01]):
            raise CredentialSignatureError(
                "The public key is not an Ed25519 did:key."
            )

        public_key_bytes = decoded[2:]

        return VerifyKey(public_key_bytes)

    @staticmethod
    def _format_datetime(value: datetime) -> str:
        value = value.astimezone(timezone.utc).replace(
            microsecond=0
        )

        return value.isoformat().replace("+00:00", "Z")

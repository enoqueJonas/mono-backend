from dataclasses import dataclass

import base58
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from nacl.signing import SigningKey


# Multicodec varint prefix for an Ed25519 public key.
ED25519_PUBLIC_KEY_MULTICODEC_PREFIX = bytes([0xED, 0x01])


@dataclass(frozen=True)
class GeneratedDIDKeyPair:
    did: str
    public_key_multibase: str
    encrypted_private_key: str


class DIDKeyEncryptionError(Exception):
    """Raised when DID key encryption or decryption fails."""


def _get_fernet() -> Fernet:
    key = settings.DID_KEY_ENCRYPTION_KEY

    if isinstance(key, str):
        key = key.encode("utf-8")

    try:
        return Fernet(key)
    except (TypeError, ValueError) as exc:
        raise DIDKeyEncryptionError(
            "DID key encryption configuration is invalid."
        ) from exc


def generate_did_key_pair() -> GeneratedDIDKeyPair:
    signing_key = SigningKey.generate()

    private_key_bytes = signing_key.encode()
    public_key_bytes = signing_key.verify_key.encode()

    multicodec_public_key = (
        ED25519_PUBLIC_KEY_MULTICODEC_PREFIX
        + public_key_bytes
    )

    public_key_multibase = (
        "z"
        + base58.b58encode(multicodec_public_key).decode("ascii")
    )

    did = f"did:key:{public_key_multibase}"

    encrypted_private_key = (
        _get_fernet()
        .encrypt(private_key_bytes)
        .decode("utf-8")
    )

    return GeneratedDIDKeyPair(
        did=did,
        public_key_multibase=public_key_multibase,
        encrypted_private_key=encrypted_private_key,
    )


def decrypt_private_key(encrypted_private_key: str) -> bytes:
    try:
        return _get_fernet().decrypt(
            encrypted_private_key.encode("utf-8")
        )
    except InvalidToken as exc:
        raise DIDKeyEncryptionError(
            "Unable to decrypt the DID private key."
        ) from exc

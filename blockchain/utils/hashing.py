import hashlib
import json
from typing import Any


class HashingService:
    @staticmethod
    def sha256_bytes(data: bytes) -> bytes:
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes.")

        return hashlib.sha256(data).digest()

    @staticmethod
    def sha256_string(data: str) -> bytes:
        if not isinstance(data, str):
            raise TypeError("Data must be a string.")

        return HashingService.sha256_bytes(
            data.encode("utf-8")
        )

    @staticmethod
    def sha256_hex(data: bytes) -> str:
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes.")

        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def canonicalize_json(
        document: dict[str, Any],
    ) -> str:
        if not isinstance(document, dict):
            raise TypeError(
                "Credential document must be a dictionary."
            )

        return json.dumps(
            document,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    @classmethod
    def hash_json(
        cls,
        document: dict[str, Any],
    ) -> bytes:
        canonical_document = cls.canonicalize_json(
            document
        )

        return cls.sha256_string(
            canonical_document
        )

    @classmethod
    def hash_json_hex(
        cls,
        document: dict[str, Any],
    ) -> str:
        return cls.hash_json(document).hex()

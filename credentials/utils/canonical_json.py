import hashlib
import json
from typing import Any


def canonicalize_json(document: dict[str, Any]) -> bytes:
    """
    Serialize controlled credential data deterministically.

    This is the canonical representation used internally for signing
    and hashing. All producers and verifiers must use this same function.
    """
    serialized = json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )

    return serialized.encode("utf-8")


def calculate_sha256(document: dict[str, Any]) -> str:
    canonical_document = canonicalize_json(document)

    return hashlib.sha256(canonical_document).hexdigest()

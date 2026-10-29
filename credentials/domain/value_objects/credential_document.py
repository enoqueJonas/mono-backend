from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class CredentialDocument:
    context: tuple[str, ...]
    credential_id: str
    credential_types: tuple[str, ...]
    issuer: str
    issuance_date: datetime
    credential_subject: Mapping[str, Any]
    evidence: Mapping[str, Any] | None = None
    valid_until: datetime | None = None
    proof: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.context:
            raise ValueError("Credential context cannot be empty.")

        if not self.credential_id.strip():
            raise ValueError("Credential ID cannot be empty.")

        if not self.credential_types:
            raise ValueError("Credential types cannot be empty.")

        if not self.issuer.strip():
            raise ValueError("Credential issuer cannot be empty.")

        if self.issuance_date.tzinfo is None:
            raise ValueError("Issuance date must be timezone-aware.")

        if not self.credential_subject:
            raise ValueError("Credential subject cannot be empty.")

        if self.valid_until is not None:
            if self.valid_until.tzinfo is None:
                raise ValueError("Valid-until date must be timezone-aware.")
            if self.valid_until <= self.issuance_date:
                raise ValueError("Valid-until must be after issuance.")

    def to_dict(self) -> dict[str, Any]:
        document: dict[str, Any] = {
            "@context": list(self.context),
            "id": self.credential_id,
            "type": list(self.credential_types),
            "issuer": self.issuer,
            "issuanceDate": self._format_datetime(self.issuance_date),
            "credentialSubject": dict(self.credential_subject),
        }

        if self.evidence is not None:
            document["evidence"] = dict(self.evidence)

        if self.valid_until is not None:
            document["validUntil"] = self._format_datetime(self.valid_until)

        if self.proof is not None:
            document["proof"] = dict(self.proof)

        return document

    @staticmethod
    def _format_datetime(value: datetime) -> str:
        return value.isoformat().replace("+00:00", "Z")

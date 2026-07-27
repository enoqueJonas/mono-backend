from __future__ import annotations

from typing import Protocol
from uuid import UUID

from credentials.application.services.context import (
    CredentialIssuanceContext,
)
from credentials.domain.value_objects import CredentialDocument
from credentials.domain.value_objects import (
    CredentialHash,
)


class CredentialRepository(Protocol):
    def save(
        self,
        *,
        document: CredentialDocument,
        context: CredentialIssuanceContext,
        issued_by_id: UUID,
        credential_hash: CredentialHash,
    ):
        """Persist a credential."""

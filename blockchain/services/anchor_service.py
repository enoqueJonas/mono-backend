from typing import Any

from blockchain.clients.credential_registry_client import (
    CredentialRegistryClient,
)
from blockchain.utils.hashing import HashingService


class AnchorService:
    def __init__(
        self,
        client: CredentialRegistryClient | None = None,
    ) -> None:
        self.client = (
            client
            or CredentialRegistryClient()
        )

    @staticmethod
    def calculate_hash(
        credential_document: dict[str, Any],
    ) -> bytes:
        return HashingService.hash_json(
            credential_document
        )

    def credential_exists(
        self,
        credential_document: dict[str, Any],
    ) -> bool:
        credential_hash = self.calculate_hash(
            credential_document
        )

        return self.client.credential_exists(
            credential_hash
        )

    def get_credential_anchor(
        self,
        credential_document: dict[str, Any],
    ) -> dict[str, Any]:
        credential_hash = self.calculate_hash(
            credential_document
        )

        return self.client.get_credential(
            credential_hash
        )

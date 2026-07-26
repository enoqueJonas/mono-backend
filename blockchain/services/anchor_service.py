from typing import Any

from blockchain.clients.credential_registry_client import (
    CredentialRegistryClient,
)
from blockchain.config.blockchain_config_factory import (
    BlockchainConfigFactory,
)
from blockchain.domain.blockchain_receipt import (
    BlockchainReceipt,
)
from blockchain.domain.credential_anchor_request import (
    CredentialAnchorRequest,
)
from blockchain.utils.hashing import HashingService


class AnchorService:
    def __init__(
        self,
        client: CredentialRegistryClient | None = None,
    ) -> None:
        self.client = client or CredentialRegistryClient(
            BlockchainConfigFactory.from_settings()
        )

    @staticmethod
    def calculate_hash(
        credential_document: dict[str, Any],
    ) -> bytes:
        return HashingService.hash_json(
            credential_document
        )

    def anchor(
        self,
        credential_document: dict[str, Any],
    ) -> BlockchainReceipt:
        credential_hash = self.calculate_hash(
            credential_document
        )

        request = CredentialAnchorRequest(
            credential_hash=credential_hash
        )

        return self.client.register_credential_hash(
            request
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

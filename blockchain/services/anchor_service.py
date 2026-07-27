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

from credentials.domain.value_objects import (
    CredentialHash,
)


class AnchorService:
    def __init__(
        self,
        client: CredentialRegistryClient | None = None,
    ) -> None:
        self.client = client or CredentialRegistryClient(
            BlockchainConfigFactory.from_settings()
        )

    def anchor(

        self,

        credential_hash: CredentialHash,

    ) -> BlockchainReceipt:

        request = CredentialAnchorRequest(

            credential_hash=credential_hash.value,

        )

        return self.client.register_credential_hash(

            request

        )

    def revoke(
        self,
        credential_hash: CredentialHash,
    ) -> BlockchainReceipt:

        return self.client.revoke_credential(
            credential_hash.value
        )

    def get_credential(
        self,
        credential_hash: CredentialHash,
    ) -> dict[str, Any]:

        return self.client.get_credential(
            credential_hash.value
        )

    def credential_exists(

        self,

        credential_hash: CredentialHash,

    ) -> bool:

        return self.client.credential_exists(

            credential_hash.value

        )

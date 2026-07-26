import json
from pathlib import Path
from typing import Any

from web3 import HTTPProvider, Web3

from blockchain.domain.blockchain_config import (
    BlockchainConfig,
)
from blockchain.domain.blockchain_receipt import (
    BlockchainReceipt,
)
from blockchain.domain.credential_anchor_request import (
    CredentialAnchorRequest,
)
from blockchain.exceptions import (
    BlockchainConnectionError,
    CredentialAlreadyAnchored,
)
from blockchain.services.transaction_service import (
    TransactionService,
)


class CredentialRegistryClient:
    def __init__(
        self,
        config: BlockchainConfig,
    ) -> None:
        self.config = config

        self.web3 = Web3(
            HTTPProvider(config.rpc_url)
        )

        if not self.web3.is_connected():
            raise BlockchainConnectionError(
                f"Unable to connect to blockchain node: "
                f"{config.rpc_url}"
            )

        contract_address = Web3.to_checksum_address(
            config.contract_address
        )

        account_address = Web3.to_checksum_address(
            config.account.address
        )

        self.config = BlockchainConfig(
            rpc_url=config.rpc_url,
            chain_id=config.chain_id,
            contract_address=contract_address,
            account=type(config.account)(
                address=account_address,
                private_key=config.account.private_key,
            ),
        )

        abi = self._load_abi()

        self.contract = self.web3.eth.contract(
            address=contract_address,
            abi=abi,
        )

        self.transaction_service = TransactionService(
            web3=self.web3,
            config=self.config,
        )

    @staticmethod
    def _load_abi() -> list[dict[str, Any]]:
        abi_path = (
            Path(__file__).resolve().parent.parent
            / "abi"
            / "CredentialRegistry.json"
        )

        with abi_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            content = json.load(file)

        # Supports either a raw ABI file or the full
        # Brownie contract artefact.
        if isinstance(content, dict) and "abi" in content:
            return content["abi"]

        if isinstance(content, list):
            return content

        raise ValueError(
            "CredentialRegistry ABI file has an "
            "unsupported structure."
        )

    def credential_exists(
        self,
        credential_hash: bytes,
    ) -> bool:
        return bool(
            self.contract.functions
            .credentialExists(credential_hash)
            .call()
        )

    def get_credential(
        self,
        credential_hash: bytes,
    ) -> dict[str, Any]:
        (
            exists,
            revoked,
            anchored_at,
            anchored_by,
        ) = (
            self.contract.functions
            .getCredential(credential_hash)
            .call()
        )

        return {
            "exists": bool(exists),
            "revoked": bool(revoked),
            "anchored_at": int(anchored_at),
            "anchored_by": anchored_by,
        }

    def register_credential_hash(
        self,
        request: CredentialAnchorRequest,
    ) -> BlockchainReceipt:
        if self.credential_exists(
            request.credential_hash
        ):
            raise CredentialAlreadyAnchored(
                "Credential hash is already anchored."
            )

        function = (
            self.contract.functions
            .registerCredentialHash(
                request.credential_hash
            )
        )

        return self.transaction_service.execute(
            function
        )

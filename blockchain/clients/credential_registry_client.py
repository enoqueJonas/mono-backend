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
    CredentialAlreadyRevoked,
)
from blockchain.mappers.blockchain_receipt_mapper import BlockchainReceiptMapper
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
        credential_hash: str,
    ) -> bool:
        return bool(
            self.contract.functions
            .credentialExists(
                self._to_bytes32(credential_hash)
            )
            .call()
        )

    def get_credential(

        self,

        credential_hash: str,

    ) -> dict[str, Any]:

        (

            exists,

            revoked,

            anchored_at,

            anchored_by,

        ) = (

            self.contract.functions

            .getCredential(

                self._to_bytes32(credential_hash)

            )

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
                self._to_bytes32(request.credential_hash)
            )
        )

        return self.transaction_service.execute(
            function
        )

    @staticmethod
    def _to_bytes32(value: str) -> bytes:
        return bytes.fromhex(value.removeprefix("0x"))

    def revoke_credential(
        self,
        credential_hash: str,
    ) -> BlockchainReceipt:

        credential = self.get_credential(
            credential_hash
        )

        if credential["revoked"]:
            raise CredentialAlreadyRevoked(
                "Credential is already revoked."
            )

        function = (
            self.contract.functions
            .revokeCredential(
                self._to_bytes32(credential_hash)
            )
        )

        return self.transaction_service.execute(
            function
        )

    def recover_anchoring_receipt(self, credential_hash: str) -> BlockchainReceipt:
        """Recover confirmed transaction metadata via the contract event log.

        This demo searches from deployment genesis (block zero). A production
        deployment must use a known deployment block/indexed event store.
        """
        state = self.get_credential(credential_hash)
        if not state["exists"] or state["revoked"]:
            raise ValueError("Cannot reconcile a missing or revoked anchor.")

        events = self.contract.events.CredentialAnchored().get_logs(
            from_block=0,
            to_block="latest",
            argument_filters={
                "credentialHash": self._to_bytes32(credential_hash)
            },
        )
        if len(events) != 1:
            raise ValueError(
                f"Expected one CredentialAnchored event, found {len(events)}."
            )
        event = events[0]
        receipt = self.web3.eth.get_transaction_receipt(
            event["transactionHash"]
        )
        result = BlockchainReceiptMapper.from_web3(
            receipt,
            wallet_address=state["anchored_by"],
            contract_address=self.config.contract_address,
        )
        if not result.status:
            raise ValueError("The recovered blockchain transaction failed.")
        return result

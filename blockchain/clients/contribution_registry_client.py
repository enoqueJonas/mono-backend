import json
from pathlib import Path
from typing import Any

from web3 import HTTPProvider, Web3

from blockchain.domain.blockchain_config import BlockchainConfig
from blockchain.domain.blockchain_receipt import BlockchainReceipt
from blockchain.exceptions import BlockchainConnectionError
from blockchain.mappers.blockchain_receipt_mapper import BlockchainReceiptMapper
from blockchain.security.registry_operator import require_registry_operator
from blockchain.services.transaction_service import TransactionService


class ContributionRegistryClient:
    def __init__(self, config: BlockchainConfig) -> None:
        self.web3 = Web3(HTTPProvider(config.rpc_url))

        if not self.web3.is_connected():
            raise BlockchainConnectionError(
                f"Unable to connect to blockchain node: {config.rpc_url}"
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
        self.contract = self.web3.eth.contract(
            address=contract_address,
            abi=self._load_abi(),
        )
        require_registry_operator(
            web3=self.web3,
            contract=self.contract,
            config=self.config,
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
            / "ContributionRegistry.json"
        )
        with abi_path.open("r", encoding="utf-8") as file:
            content = json.load(file)

        if isinstance(content, dict) and "abi" in content:
            return content["abi"]
        if isinstance(content, list):
            return content
        raise ValueError(
            "ContributionRegistry ABI file has an unsupported structure."
        )

    def contribution_exists(self, contribution_id: str) -> bool:
        return bool(
            self.contract.functions.contributionExists(
                self._uuid_to_bytes32(contribution_id)
            ).call()
        )

    def get_contribution(self, contribution_id: str) -> dict[str, Any]:
        contribution_hash, anchored_at, anchored_by, exists = (
            self.contract.functions.getContribution(
                self._uuid_to_bytes32(contribution_id)
            ).call()
        )
        return {
            "contribution_hash": bytes(contribution_hash).hex(),
            "anchored_at": int(anchored_at),
            "anchored_by": anchored_by,
            "exists": bool(exists),
        }

    def register_contribution(
        self,
        *,
        contribution_id: str,
        contribution_hash: str,
    ) -> BlockchainReceipt:
        function = self.contract.functions.registerContribution(
            self._uuid_to_bytes32(contribution_id),
            self._hash_to_bytes32(contribution_hash),
        )
        return self.transaction_service.execute(function)

    def recover_anchoring_receipt(self, contribution_id: str) -> BlockchainReceipt:
        """Recover the original mined receipt without submitting twice.

        The demo scans from block zero. Production would need indexed event
        storage and a known deployment block.
        """
        state = self.get_contribution(contribution_id)
        if not state["exists"]:
            raise ValueError("Cannot recover an absent contribution anchor.")

        events = self.contract.events.ContributionAnchored().get_logs(
            from_block=0,
            to_block="latest",
            argument_filters={
                "contributionId": self._uuid_to_bytes32(contribution_id),
            },
        )
        if len(events) != 1:
            raise ValueError(
                f"Expected one ContributionAnchored event, found {len(events)}."
            )
        event = events[0]
        if (
            bytes(event["args"]["contributionHash"]).hex()
            != state["contribution_hash"]
        ):
            raise ValueError("The contribution event disagrees with contract state.")

        receipt = self.web3.eth.get_transaction_receipt(event["transactionHash"])
        mapped = BlockchainReceiptMapper.from_web3(
            receipt,
            wallet_address=state["anchored_by"],
            contract_address=self.config.contract_address,
        )
        if not mapped.status:
            raise ValueError("Recovered contribution anchor transaction failed.")
        return mapped

    @staticmethod
    def _hash_to_bytes32(value: str) -> bytes:
        return bytes.fromhex(value.removeprefix("0x"))

    @staticmethod
    def _uuid_to_bytes32(value: str) -> bytes:
        raw = bytes.fromhex(value.replace("-", ""))
        return raw.rjust(32, b"\x00")

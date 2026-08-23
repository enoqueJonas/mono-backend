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
from blockchain.exceptions import (
    BlockchainConnectionError,
)
from blockchain.services.transaction_service import (
    TransactionService,
)


class GroupRegistryClient:
    def __init__(
        self,
        config: BlockchainConfig,
    ) -> None:
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

        self.contract = self.web3.eth.contract(
            address=contract_address,
            abi=self._load_abi(),
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
            / "GroupRegistry.json"
        )

        with abi_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            content = json.load(file)

        if isinstance(content, dict) and "abi" in content:
            return content["abi"]

        if isinstance(content, list):
            return content

        raise ValueError(
            "GroupRegistry ABI file has an "
            "unsupported structure."
        )

    def settings_exist(
        self,
        *,
        group_id: str,
        version: int,
    ) -> bool:
        return bool(
            self.contract.functions
            .groupSettingsExists(
                self._uuid_to_bytes32(group_id),
                version,
            )
            .call()
        )

    def get_group_settings(
        self,
        *,
        group_id: str,
        version: int,
    ) -> dict[str, Any]:
        (
            settings_hash,
            anchored_at,
            anchored_by,
            exists,
        ) = (
            self.contract.functions
            .getGroupSettings(
                self._uuid_to_bytes32(group_id),
                version,
            )
            .call()
        )

        return {
            "settings_hash": bytes(
                settings_hash
            ).hex(),
            "anchored_at": int(
                anchored_at
            ),
            "anchored_by": anchored_by,
            "exists": bool(exists),
        }

    def register_group_settings(
        self,
        *,
        group_id: str,
        version: int,
        settings_hash: str,
    ) -> BlockchainReceipt:
        function = (
            self.contract.functions
            .registerGroupSettings(
                self._uuid_to_bytes32(group_id),
                version,
                self._hash_to_bytes32(settings_hash),
            )
        )

        return self.transaction_service.execute(
            function
        )

    @staticmethod
    def _hash_to_bytes32(
        value: str,
    ) -> bytes:
        return bytes.fromhex(
            value.removeprefix("0x")
        )

    @staticmethod
    def _uuid_to_bytes32(
        value: str,
    ) -> bytes:
        raw = bytes.fromhex(
            value.replace("-", "")
        )

        return raw.rjust(
            32,
            b"\x00",
        )

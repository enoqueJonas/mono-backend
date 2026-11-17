import json
from pathlib import Path
from uuid import UUID

from web3 import HTTPProvider, Web3

from blockchain.config.blockchain_config_factory import BlockchainConfigFactory
from blockchain.domain.blockchain_receipt import BlockchainReceipt
from blockchain.exceptions import BlockchainConnectionError
from blockchain.security.registry_operator import require_registry_operator
from blockchain.services.transaction_service import TransactionService


class DisbursementRegistryClient:
    """Client for two distinct proofs: approved proposal and verified payout receipt.

    This client CANNOT verify a mobile-money payment and must never be called
    with an unverified provider response.
    """

    def __init__(self, config=None):
        if config is None:
            from django.conf import settings
            if not settings.DISBURSEMENT_REGISTRY_ADDRESS:
                raise ValueError("DISBURSEMENT_REGISTRY_ADDRESS is not configured.")
            config = BlockchainConfigFactory.from_settings(
                contract_address=settings.DISBURSEMENT_REGISTRY_ADDRESS,
            )

        self.config = config
        self.web3 = Web3(HTTPProvider(config.rpc_url))
        if not self.web3.is_connected():
            raise BlockchainConnectionError(
                f"Unable to connect to blockchain node: {config.rpc_url}"
            )

        with (Path(__file__).resolve().parent.parent / "abi" / "DisbursementRegistry.json").open(
            encoding="utf-8"
        ) as fp:
            artifact = json.load(fp)

        self.contract = self.web3.eth.contract(
            address=Web3.to_checksum_address(config.contract_address),
            abi=artifact["abi"] if isinstance(artifact, dict) else artifact,
        )
        require_registry_operator(
            web3=self.web3,
            contract=self.contract,
            config=config,
        )
        self.transactions = TransactionService(web3=self.web3, config=config)

    @staticmethod
    def _id_bytes32(disbursement_id: str) -> bytes:
        return UUID(str(disbursement_id)).bytes.rjust(32, b"\x00")

    @staticmethod
    def _hash_bytes32(hex_digest: str) -> bytes:
        digest = bytes.fromhex(hex_digest.removeprefix("0x"))
        if len(digest) != 32:
            raise ValueError("Expected a SHA-256 digest of exactly 32 bytes.")
        return digest

    def get(self, disbursement_id: str) -> dict:
        authorization, settlement, authorized_at, settled_at, authorized, settled = (
            self.contract.functions.getDisbursement(
                self._id_bytes32(disbursement_id)
            ).call()
        )
        return {
            "authorization_hash": bytes(authorization).hex(),
            "settlement_hash": bytes(settlement).hex(),
            "authorized_at": authorized_at,
            "settled_at": settled_at,
            "authorized": bool(authorized),
            "settled": bool(settled),
        }

    def anchor_authorization(
        self, *, disbursement_id: str, authorization_hash: str
    ) -> BlockchainReceipt:
        if self.get(disbursement_id)["authorized"]:
            raise ValueError("Authorization already anchored; reconcile original receipt.")
        return self.transactions.execute(
            self.contract.functions.recordAuthorization(
                self._id_bytes32(disbursement_id),
                self._hash_bytes32(authorization_hash),
            )
        )

    def anchor_verified_settlement(
        self, *, disbursement_id: str, settlement_hash: str
    ) -> BlockchainReceipt:
        state = self.get(disbursement_id)
        if not state["authorized"]:
            raise ValueError("No on-chain authorization; settlement refused.")
        if state["settled"]:
            raise ValueError("Settlement already anchored; reconcile original receipt.")
        return self.transactions.execute(
            self.contract.functions.recordSettlement(
                self._id_bytes32(disbursement_id),
                self._hash_bytes32(settlement_hash),
            )
        )

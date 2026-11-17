import json
from pathlib import Path
from typing import Any

from web3 import HTTPProvider, Web3

from blockchain.config.blockchain_config_factory import BlockchainConfigFactory
from blockchain.exceptions import BlockchainConnectionError
from blockchain.mappers.blockchain_receipt_mapper import BlockchainReceiptMapper
from blockchain.security.registry_operator import require_registry_operator
from blockchain.services.transaction_service import TransactionService


class DisbursementRegistryClient:
    """Immutable intent and settlement hashes, written by the authorised operator."""

    def __init__(self):
        from django.conf import settings

        address = getattr(settings, "DISBURSEMENT_REGISTRY_ADDRESS", "")
        if not address:
            raise RuntimeError("DISBURSEMENT_REGISTRY_ADDRESS is not configured.")
        original = BlockchainConfigFactory.from_settings(contract_address=address)
        self.web3 = Web3(HTTPProvider(original.rpc_url))
        if not self.web3.is_connected():
            raise BlockchainConnectionError("Disbursement registry node unavailable.")
        checksum = Web3.to_checksum_address(original.contract_address)
        account = Web3.to_checksum_address(original.account.address)
        self.config = type(original)(
            rpc_url=original.rpc_url,
            chain_id=original.chain_id,
            contract_address=checksum,
            account=type(original.account)(address=account, private_key=original.account.private_key),
        )
        path = Path(__file__).resolve().parent.parent / "abi" / "DisbursementRegistry.json"
        with path.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
        abi: list[dict[str, Any]] = loaded["abi"] if isinstance(loaded, dict) else loaded
        self.contract = self.web3.eth.contract(address=checksum, abi=abi)
        require_registry_operator(web3=self.web3, contract=self.contract, config=self.config)
        self.transactions = TransactionService(web3=self.web3, config=self.config)

    @staticmethod
    def _id(value):
        raw = bytes.fromhex(str(value).replace("-", ""))
        if len(raw) != 16:
            raise ValueError("Disbursement ID must be UUID.")
        return raw.rjust(32, b"\x00")

    @staticmethod
    def _hash(value):
        raw = bytes.fromhex(str(value).removeprefix("0x"))
        if len(raw) != 32:
            raise ValueError("Proof hash must have 32 bytes.")
        return raw

    def get(self, disbursement_id):
        a, b, t1, t2 = self.contract.functions.getProof(self._id(disbursement_id)).call()
        return {
            "intent_hash": bytes(a).hex(),
            "settlement_hash": bytes(b).hex(),
            "intent_at": int(t1),
            "settlement_at": int(t2),
        }

    def anchor_intent(self, disbursement_id, intent_hash):
        state = self.get(disbursement_id)
        if state["intent_at"]:
            if state["intent_hash"] != intent_hash:
                raise ValueError("Conflicting existing intent hash on-chain.")
            return self._recover(disbursement_id, "IntentAnchored")
        return self.transactions.execute(
            self.contract.functions.anchorIntent(self._id(disbursement_id), self._hash(intent_hash))
        )

    def anchor_settlement(self, disbursement_id, settlement_hash):
        state = self.get(disbursement_id)
        if not state["intent_at"]:
            raise ValueError("Settlement cannot precede intent anchor.")
        if state["settlement_at"]:
            if state["settlement_hash"] != settlement_hash:
                raise ValueError("Conflicting existing settlement hash on-chain.")
            return self._recover(disbursement_id, "SettlementAnchored")
        return self.transactions.execute(
            self.contract.functions.anchorSettlement(self._id(disbursement_id), self._hash(settlement_hash))
        )

    def _recover(self, disbursement_id, event_name):
        """Recover an already mined receipt; NEVER submit an idempotency collision twice."""
        event = getattr(self.contract.events, event_name)()
        logs = event.get_logs(
            from_block=0,
            to_block="latest",
            argument_filters={"disbursementId": self._id(disbursement_id)},
        )
        if len(logs) != 1:
            raise ValueError(f"Expected one {event_name} event, found {len(logs)}")
        receipt = self.web3.eth.get_transaction_receipt(logs[0]["transactionHash"])
        mapped = BlockchainReceiptMapper.from_web3(
            receipt,
            wallet_address=self.config.account.address,
            contract_address=self.config.contract_address,
        )
        if not mapped.status:
            raise ValueError("Existing disbursement anchor transaction failed.")
        return mapped

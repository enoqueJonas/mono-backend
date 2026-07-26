from typing import Any

from blockchain.domain.blockchain_receipt import (
    BlockchainReceipt,
)


class BlockchainReceiptMapper:
    @staticmethod
    def from_web3(
        receipt: Any,
        *,
        wallet_address: str,
        contract_address: str,
    ) -> BlockchainReceipt:
        transaction_hash = receipt["transactionHash"]
        block_hash = receipt["blockHash"]

        effective_gas_price = receipt.get(
            "effectiveGasPrice",
            0,
        )

        return BlockchainReceipt(
            transaction_hash=transaction_hash.hex(),
            block_hash=block_hash.hex(),
            block_number=int(receipt["blockNumber"]),
            contract_address=contract_address,
            wallet_address=wallet_address,
            gas_used=int(receipt["gasUsed"]),
            effective_gas_price=int(
                effective_gas_price or 0
            ),
            status=bool(receipt["status"]),
        )

from typing import Any

from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.exceptions import TimeExhausted

from blockchain.domain.blockchain_config import (
    BlockchainConfig,
)
from blockchain.domain.blockchain_receipt import (
    BlockchainReceipt,
)
from blockchain.exceptions import TransactionFailed
from blockchain.mappers.blockchain_receipt_mapper import (
    BlockchainReceiptMapper,
)


class TransactionService:
    def __init__(
        self,
        *,
        web3: Web3,
        config: BlockchainConfig,
        receipt_timeout: int = 120,
    ) -> None:
        self.web3 = web3
        self.config = config
        self.receipt_timeout = receipt_timeout

        derived_account = (
            self.web3.eth.account.from_key(
                config.account.private_key
            )
        )

        configured_address = Web3.to_checksum_address(
            config.account.address
        )

        if derived_account.address != configured_address:
            raise ValueError(
                "BLOCKCHAIN_ACCOUNT_ADDRESS does not "
                "match BLOCKCHAIN_PRIVATE_KEY."
            )

    def execute(
        self,
        function: ContractFunction,
    ) -> BlockchainReceipt:
        account = self.config.account

        nonce = self.web3.eth.get_transaction_count(
            account.address,
            block_identifier="pending",
        )

        estimated_gas = function.estimate_gas(
            {
                "from": account.address,
            }
        )

        # Small safety margin above the estimated amount.
        gas_limit = int(estimated_gas * 1.20)

        transaction = function.build_transaction(
            {
                "from": account.address,
                "nonce": nonce,
                "chainId": self.config.chain_id,
                "gas": gas_limit,
                "gasPrice": self.web3.eth.gas_price,
            }
        )

        signed_transaction = (
            self.web3.eth.account.sign_transaction(
                transaction,
                private_key=account.private_key,
            )
        )

        transaction_hash = (
            self.web3.eth.send_raw_transaction(
                signed_transaction.raw_transaction
            )
        )

        try:
            receipt = (
                self.web3.eth.wait_for_transaction_receipt(
                    transaction_hash,
                    timeout=self.receipt_timeout,
                )
            )
        except TimeExhausted as exc:
            raise TransactionFailed(
                "Timed out while waiting for the "
                "blockchain transaction receipt."
            ) from exc

        mapped_receipt = BlockchainReceiptMapper.from_web3(
            receipt,
            wallet_address=account.address,
            contract_address=self.config.contract_address,
        )

        if not mapped_receipt.status:
            raise TransactionFailed(
                "The blockchain transaction was mined "
                "but execution failed."
            )

        return mapped_receipt

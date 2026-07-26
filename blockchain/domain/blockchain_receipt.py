from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BlockchainReceipt:

    transaction_hash: str
    block_hash: str
    block_number: int
    contract_address: str
    wallet_address: str
    gas_used: int
    effective_gas_price: int
    status: bool

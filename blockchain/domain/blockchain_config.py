from dataclasses import dataclass

from blockchain.domain.blockchain_account import (
    BlockchainAccount,
)


@dataclass(frozen=True, slots=True)
class BlockchainConfig:
    """
    Configuration required by the blockchain infrastructure.
    """

    rpc_url: str
    chain_id: int
    contract_address: str
    account: BlockchainAccount

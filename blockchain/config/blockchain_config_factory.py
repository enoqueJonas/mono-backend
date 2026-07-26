from django.conf import settings

from blockchain.domain.blockchain_account import (
    BlockchainAccount,
)
from blockchain.domain.blockchain_config import (
    BlockchainConfig,
)


class BlockchainConfigFactory:

    @staticmethod
    def from_settings() -> BlockchainConfig:

        return BlockchainConfig(

            rpc_url=settings.BLOCKCHAIN_RPC_URL,

            chain_id=settings.BLOCKCHAIN_CHAIN_ID,

            contract_address=settings.CREDENTIAL_REGISTRY_ADDRESS,

            account=BlockchainAccount(

                address=settings.BLOCKCHAIN_ACCOUNT_ADDRESS,

                private_key=settings.BLOCKCHAIN_PRIVATE_KEY,

            ),
        )

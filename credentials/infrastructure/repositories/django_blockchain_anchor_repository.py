from django.conf import settings
from django.utils import timezone

from blockchain.models import (
    BlockchainAnchor,
    BlockchainAnchorStatus,
    BlockchainAnchorType,
)
from credentials.application.repositories import (
    BlockchainAnchorRepository,
)


class DjangoBlockchainAnchorRepository(
    BlockchainAnchorRepository,
):
    def save(
        self,
        *,
        credential,
        receipt,
    ) -> BlockchainAnchor:
        return BlockchainAnchor.objects.create(
            anchor_type=BlockchainAnchorType.CREDENTIAL,
            content_hash=credential.credential_hash,
            credential=credential,
            network=f"chain-{settings.BLOCKCHAIN_CHAIN_ID}",
            contract_address=receipt.contract_address,
            transaction_hash=receipt.transaction_hash,
            block_number=receipt.block_number,
            wallet_address=receipt.wallet_address,
            anchored_at=timezone.now(),
            status=(
                BlockchainAnchorStatus.CONFIRMED
                if receipt.status
                else BlockchainAnchorStatus.FAILED
            ),
        )

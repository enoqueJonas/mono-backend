from django.utils import timezone

from blockchain.models import BlockchainAnchor
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
            credential=credential,
            contract_address=receipt.contract_address,
            transaction_hash=receipt.transaction_hash,
            block_number=receipt.block_number,
            wallet_address=receipt.wallet_address,
            anchored_at=timezone.now(),
            status=receipt.status,
        )

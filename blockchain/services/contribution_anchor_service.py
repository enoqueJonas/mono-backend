from django.conf import settings
from django.utils import timezone

from blockchain.clients.contribution_registry_client import (
    ContributionRegistryClient,
)
from blockchain.config.blockchain_config_factory import BlockchainConfigFactory
from blockchain.models import (
    BlockchainAnchor,
    BlockchainAnchorStatus,
    BlockchainAnchorType,
)
from contributions.models import Contribution
from contributions.services.contribution_hash_service import (
    ContributionHashService,
)


class ContributionAnchorService:
    def __init__(
        self,
        client: ContributionRegistryClient | None = None,
    ) -> None:
        if not settings.CONTRIBUTION_REGISTRY_ADDRESS and client is None:
            raise ValueError(
                "CONTRIBUTION_REGISTRY_ADDRESS is not configured."
            )

        self.client = client or ContributionRegistryClient(
            BlockchainConfigFactory.from_settings(
                contract_address=settings.CONTRIBUTION_REGISTRY_ADDRESS,
            )
        )

    def anchor(self, contribution: Contribution) -> BlockchainAnchor:
        contribution_hash = ContributionHashService.calculate(contribution)

        if self.client.contribution_exists(str(contribution.id)):
            raise ValueError("This contribution is already anchored.")

        receipt = self.client.register_contribution(
            contribution_id=str(contribution.id),
            contribution_hash=contribution_hash,
        )

        return BlockchainAnchor.objects.create(
            anchor_type=BlockchainAnchorType.CONTRIBUTION,
            content_hash=contribution_hash,
            contribution=contribution,
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

    def verify_integrity(self, contribution: Contribution) -> dict:
        record = self.client.get_contribution(str(contribution.id))
        calculated_hash = ContributionHashService.calculate(contribution)
        stored_hash = record['contribution_hash'] if record['exists'] else None
        if not record['exists']:
            result = 'NOT_ANCHORED'
        elif calculated_hash == stored_hash:
            result = 'INTEGRITY_CONFIRMED'
        else:
            result = 'INTEGRITY_MISMATCH'
        return {
            'status': result,
            'contribution_id': str(contribution.id),
            'calculated_hash': calculated_hash,
            'blockchain_hash': stored_hash,
        }

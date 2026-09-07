import os

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
        contract_address = os.environ.get(
            "CONTRIBUTION_REGISTRY_ADDRESS",
            "",
        )
        if not contract_address and client is None:
            raise ValueError(
                "CONTRIBUTION_REGISTRY_ADDRESS is not configured."
            )

        self.client = client or ContributionRegistryClient(
            BlockchainConfigFactory.from_settings(
                contract_address=contract_address,
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

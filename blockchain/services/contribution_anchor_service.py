from django.conf import settings
from django.db import transaction
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


class ContributionAnchorHashMismatch(ValueError):
    """Ambiguous chain/local hashes require human review, never blind retry."""


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

    def anchor(
        self,
        contribution: Contribution,
        *,
        expected_hash: str | None = None,
    ) -> BlockchainAnchor:
        """Submit once or reconcile a previously mined transaction.

        Network calls deliberately occur *outside* any SQL transaction;
        the caller is the post-commit outbox processor.
        """
        contribution_hash = ContributionHashService.calculate(contribution)
        if expected_hash is not None and contribution_hash != expected_hash:
            raise ContributionAnchorHashMismatch(
                "Local contribution changed after its anchoring intent."
            )

        onchain = self.client.get_contribution(str(contribution.id))
        if onchain["exists"]:
            if onchain["contribution_hash"] != contribution_hash:
                raise ContributionAnchorHashMismatch(
                    "Existing on-chain contribution hash does not match intent."
                )
            # Failure could have occurred after EVM mining and before SQL write.
            receipt = self.client.recover_anchoring_receipt(str(contribution.id))
        else:
            receipt = self.client.register_contribution(
                contribution_id=str(contribution.id),
                contribution_hash=contribution_hash,
            )

        if not receipt.status:
            raise ValueError("Contribution transaction receipt was unsuccessful.")

        # This short SQL transaction occurs only *after* the RPC has finished.
        with transaction.atomic():
            existing = (
                BlockchainAnchor.objects.select_for_update()
                .filter(
                    anchor_type=BlockchainAnchorType.CONTRIBUTION,
                    contribution=contribution,
                )
                .first()
            )
            if existing is not None:
                if (
                    existing.content_hash != contribution_hash
                    or existing.transaction_hash != receipt.transaction_hash
                    or existing.status != BlockchainAnchorStatus.CONFIRMED
                ):
                    raise ContributionAnchorHashMismatch(
                        "Recorded contribution anchor differs from mined event."
                    )
                return existing

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
                status=BlockchainAnchorStatus.CONFIRMED,
            )

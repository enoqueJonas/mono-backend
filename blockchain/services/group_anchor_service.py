from django.conf import settings
from django.utils import timezone

from blockchain.clients.group_registry_client import (
    GroupRegistryClient,
)
from blockchain.config.blockchain_config_factory import (
    BlockchainConfigFactory,
)
from blockchain.models import (
    BlockchainAnchor,
    BlockchainAnchorStatus,
    BlockchainAnchorType,
)
from groups.models import GroupSettings
from groups.services.group_settings_hash_service import (
    GroupSettingsHashService,
)


class GroupAnchorService:
    def __init__(
        self,
        client: GroupRegistryClient | None = None,
    ) -> None:
        self.client = client or GroupRegistryClient(
            BlockchainConfigFactory.from_settings(
                contract_address=(
                    settings.GROUP_REGISTRY_ADDRESS
                ),
            )
        )

    def anchor(
        self,
        group_settings: GroupSettings,
    ) -> BlockchainAnchor:
        settings_hash = (
            GroupSettingsHashService.calculate(
                group_settings
            )
        )

        if self.client.settings_exist(
            group_id=str(group_settings.group_id),
            version=group_settings.version,
        ):
            raise ValueError(
                "This group settings version "
                "is already anchored."
            )

        receipt = self.client.register_group_settings(
            group_id=str(group_settings.group_id),
            version=group_settings.version,
            settings_hash=settings_hash,
        )

        return BlockchainAnchor.objects.create(
            anchor_type=(
                BlockchainAnchorType.GROUP_SETTINGS
            ),
            content_hash=settings_hash,
            group_settings=group_settings,
            network=(
                f"chain-{settings.BLOCKCHAIN_CHAIN_ID}"
            ),
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

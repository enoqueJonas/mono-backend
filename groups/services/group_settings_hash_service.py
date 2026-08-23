from groups.models import GroupSettings

from blockchain.utils.hashing import (
    HashingService,
)


class GroupSettingsHashService:
    @staticmethod
    def build_document(
        settings: GroupSettings,
    ) -> dict:
        return {
            "group_id": str(
                settings.group_id
            ),
            "version": settings.version,
            "contribution_amount": (
                format(
                    settings.contribution_amount,
                    ".2f",
                )
            ),
            "currency": settings.currency,
            "contribution_frequency": (
                settings.contribution_frequency
            ),
            "maximum_members": (
                settings.maximum_members
            ),
            "rotation_strategy": (
                settings.rotation_strategy
            ),
            "requires_consensus": (
                settings.requires_consensus
            ),
            "allow_manual_contributions": (
                settings.allow_manual_contributions
            ),
        }

    @classmethod
    def calculate(
        cls,
        settings: GroupSettings,
    ) -> str:
        document = cls.build_document(
            settings
        )

        return HashingService.hash_json_hex(
            document
        )

from blockchain.utils.hashing import HashingService
from contributions.models import Contribution


class ContributionHashService:
    @staticmethod
    def build_document(contribution: Contribution) -> dict:
        return {
            "contribution_id": str(contribution.id),
            "group_id": str(contribution.member.group_id),
            "group_member_id": str(contribution.member_id),
            "group_settings_version": contribution.group_settings.version,
            "amount": format(contribution.amount, ".2f"),
            "currency": contribution.currency,
            "contribution_period": contribution.contribution_period.isoformat(),
            "reference": contribution.reference,
            "source": contribution.source,
            "status": contribution.status,
        }

    @classmethod
    def calculate(cls, contribution: Contribution) -> str:
        return HashingService.hash_json_hex(
            cls.build_document(contribution)
        )

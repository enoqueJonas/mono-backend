from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from groups.models import GroupMember
from identity.models import GroupDID, UserDID


@dataclass(frozen=True)
class CredentialBuildData:
    credential_id: UUID
    group_member: GroupMember
    issuer_did: GroupDID
    holder_did: UserDID
    period_start: date
    period_end: date
    valid_from: datetime
    valid_until: datetime | None
    confirmed_contributions: int
    total_contributed: Decimal
    currency: str


class CredentialBuilder:
    CONTEXTS = [
        "https://www.w3.org/ns/credentials/v2",
    ]

    TYPES = [
        "VerifiableCredential",
        "XitiqueContributionCredential",
    ]

    @classmethod
    def build_unsigned(
        cls,
        *,
        data: CredentialBuildData,
    ) -> dict[str, Any]:
        group = data.group_member.group
        settings = group.settings

        document: dict[str, Any] = {
            "@context": cls.CONTEXTS,
            "id": f"urn:uuid:{data.credential_id}",
            "type": cls.TYPES,
            "issuer": data.issuer_did.did,
            "validFrom": cls._format_datetime(data.valid_from),
            "credentialSubject": {
                "id": data.holder_did.did,
                "groupId": str(group.id),
                "groupName": group.name,
                "membershipId": str(data.group_member.id),
                "periodStart": data.period_start.isoformat(),
                "periodEnd": data.period_end.isoformat(),
                "confirmedContributions": (
                    data.confirmed_contributions
                ),
                "totalContributed": cls._format_decimal(
                    data.total_contributed
                ),
                "currency": data.currency,
                "contributionAmount": cls._format_decimal(
                    settings.contribution_amount
                ),
                "contributionFrequency": (
                    settings.contribution_frequency
                ),
            },
        }

        if data.valid_until is not None:
            document["validUntil"] = cls._format_datetime(
                data.valid_until
            )

        return document

    @staticmethod
    def _format_datetime(value: datetime) -> str:
        value = value.replace(microsecond=0)

        formatted = value.isoformat()

        if formatted.endswith("+00:00"):
            return formatted.replace("+00:00", "Z")

        return formatted

    @staticmethod
    def _format_decimal(value: Decimal) -> str:
        return format(value, ".2f")

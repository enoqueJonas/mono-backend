from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from credentials.domain.protocols import ContributionLike
from credentials.domain.value_objects import CredentialDocument


class CredentialDocumentFactory:
    CONFIRMED_CONTRIBUTION_STATUS = "CONFIRMED"
    CONTEXT = (
        "https://www.w3.org/2018/credentials/v1",
    )

    CREDENTIAL_TYPES = (
        "VerifiableCredential",
        "ContributionHistoryCredential",
    )

    def build(
        self,
        *,
        credential_id: UUID,
        issuer_did: str,
        holder_did: str,
        group_id: UUID,
        group_name: str,
        period_start: date,
        period_end: date,
        issuance_date: datetime,
        contributions: Iterable[ContributionLike],
    ) -> CredentialDocument:
        contribution_list = list(contributions)

        if period_end < period_start:
            raise ValueError(
                "Credential period end cannot be before period start."
            )

        if not contribution_list:
            raise ValueError(
                "At least one contribution is required."
            )

        self._ensure_all_contributions_are_confirmed(
            contribution_list
        )
        self._ensure_contributions_are_within_period(
            contributions=contribution_list,
            period_start=period_start,
            period_end=period_end,
        )

        currency = self._get_single_currency(
            contribution_list
        )
        total_amount = sum(
            (
                contribution.amount
                for contribution in contribution_list
            ),
            start=Decimal("0.00"),
        )

        return CredentialDocument(
            context=self.CONTEXT,
            credential_id=f"urn:uuid:{credential_id}",
            credential_types=self.CREDENTIAL_TYPES,
            issuer=issuer_did,
            issuance_date=issuance_date,
            credential_subject={
                "id": holder_did,
                "group": {
                    "id": str(group_id),
                    "name": group_name,
                },
                "contributionHistory": {
                    "periodStart": period_start.isoformat(),
                    "periodEnd": period_end.isoformat(),
                    "contributionCount": len(
                        contribution_list
                    ),
                    "totalAmount": format(
                        total_amount,
                        ".2f",
                    ),
                    "currency": currency,
                },
            },
            evidence={
                "type": "ContributionHistory",
                "contributionReferences": [
                    contribution.reference
                    for contribution in contribution_list
                ],
            },
        )

    def _ensure_all_contributions_are_confirmed(
        self,
        contributions: list[ContributionLike],
    ) -> None:
        if any(
            contribution.status != self.CONFIRMED_CONTRIBUTION_STATUS
            for contribution in contributions
        ):
            raise ValueError(
                "Only confirmed contributions can be included."
            )

    @staticmethod
    def _ensure_contributions_are_within_period(
        *,
        contributions: list[ContributionLike],
        period_start: date,
        period_end: date,
    ) -> None:
        if any(
            contribution.contribution_period
            < period_start
            or contribution.contribution_period
            > period_end
            for contribution in contributions
        ):
            raise ValueError(
                "All contributions must be within "
                "the credential period."
            )

    @staticmethod
    def _get_single_currency(
        contributions: list[ContributionLike],
    ) -> str:
        currencies = {
            contribution.currency
            for contribution in contributions
        }

        if len(currencies) != 1:
            raise ValueError(
                "All contributions must use the same currency."
            )

        return currencies.pop()

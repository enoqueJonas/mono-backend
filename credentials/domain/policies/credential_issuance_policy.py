from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from credentials.domain.protocols import ContributionLike
from credentials.domain.value_objects import PolicyDecision


class CredentialIssuancePolicy:
    CONFIRMED_CONTRIBUTION_STATUS = "CONFIRMED"

    INVALID_PERIOD_REASON = (
        "Credential period end cannot be before period start."
    )

    DUPLICATE_CREDENTIAL_REASON = (
        "An active credential already exists for this "
        "member and period."
    )

    NO_CONFIRMED_CONTRIBUTIONS_REASON = (
        "Member has no confirmed contributions "
        "within the credential period."
    )

    def evaluate(
        self,
        *,
        period_start: date,
        period_end: date,
        contributions: Iterable[ContributionLike],
        active_credential_exists: bool,
    ) -> PolicyDecision:
        if period_end < period_start:
            return PolicyDecision.deny(
                self.INVALID_PERIOD_REASON
            )

        if active_credential_exists:
            return PolicyDecision.deny(
                self.DUPLICATE_CREDENTIAL_REASON
            )

        if not self._has_confirmed_contribution_within_period(
            contributions=contributions,
            period_start=period_start,
            period_end=period_end,
        ):
            return PolicyDecision.deny(
                self.NO_CONFIRMED_CONTRIBUTIONS_REASON
            )

        return PolicyDecision.allow()

    def _has_confirmed_contribution_within_period(
        self,
        *,
        contributions: Iterable[ContributionLike],
        period_start: date,
        period_end: date,
    ) -> bool:
        return any(
            contribution.status
            == self.CONFIRMED_CONTRIBUTION_STATUS
            and period_start
            <= contribution.contribution_period
            <= period_end
            for contribution in contributions
        )

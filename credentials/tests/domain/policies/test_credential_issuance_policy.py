from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from credentials.domain.policies import (
    CredentialIssuancePolicy,
)


CONFIRMED = "CONFIRMED"
PENDING = "PENDING"

PERIOD_START = date(2026, 1, 1)
PERIOD_END = date(2026, 3, 31)


def make_contribution(
    *,
    status: str = CONFIRMED,
    contribution_period: date = date(2026, 1, 1),
):
    return SimpleNamespace(
        amount=Decimal("500.00"),
        currency="MZN",
        status=status,
        contribution_period=contribution_period,
        reference="CONT-001",
    )


def evaluate(
    *,
    contributions,
    active_credential_exists: bool = False,
    period_start: date = PERIOD_START,
    period_end: date = PERIOD_END,
):
    return CredentialIssuancePolicy().evaluate(
        period_start=period_start,
        period_end=period_end,
        contributions=contributions,
        active_credential_exists=active_credential_exists,
    )


def test_allows_issuance_when_requirements_are_met() -> None:
    decision = evaluate(
        contributions=[make_contribution()]
    )

    assert decision.allowed is True
    assert decision.reason is None


def test_denies_issuance_for_invalid_period() -> None:
    decision = evaluate(
        contributions=[make_contribution()],
        period_start=date(2026, 3, 31),
        period_end=date(2026, 1, 1),
    )

    assert decision.allowed is False
    assert decision.reason == (
        "Credential period end cannot be before "
        "period start."
    )


def test_denies_issuance_when_active_credential_exists() -> None:
    decision = evaluate(
        contributions=[make_contribution()],
        active_credential_exists=True,
    )

    assert decision.allowed is False
    assert decision.reason == (
        "An active credential already exists for this "
        "member and period."
    )


def test_denies_issuance_without_contributions() -> None:
    decision = evaluate(
        contributions=[]
    )

    assert decision.allowed is False
    assert decision.reason == (
        "Member has no confirmed contributions "
        "within the credential period."
    )


def test_denies_issuance_with_only_pending_contributions() -> None:
    decision = evaluate(
        contributions=[
            make_contribution(status=PENDING)
        ]
    )

    assert decision.allowed is False
    assert decision.reason == (
        "Member has no confirmed contributions "
        "within the credential period."
    )


def test_denies_issuance_when_contribution_is_before_period() -> None:
    decision = evaluate(
        contributions=[
            make_contribution(
                contribution_period=date(2025, 12, 1)
            )
        ]
    )

    assert decision.allowed is False


def test_denies_issuance_when_contribution_is_after_period() -> None:
    decision = evaluate(
        contributions=[
            make_contribution(
                contribution_period=date(2026, 4, 1)
            )
        ]
    )

    assert decision.allowed is False


def test_allows_contribution_on_period_start_boundary() -> None:
    decision = evaluate(
        contributions=[
            make_contribution(
                contribution_period=PERIOD_START
            )
        ]
    )

    assert decision.allowed is True


def test_allows_contribution_on_period_end_boundary() -> None:
    decision = evaluate(
        contributions=[
            make_contribution(
                contribution_period=PERIOD_END
            )
        ]
    )

    assert decision.allowed is True


def test_allows_when_at_least_one_contribution_is_eligible() -> None:
    contributions = [
        make_contribution(
            status=PENDING,
            contribution_period=date(2026, 1, 1),
        ),
        make_contribution(
            status=CONFIRMED,
            contribution_period=date(2026, 2, 1),
        ),
    ]

    decision = evaluate(
        contributions=contributions
    )

    assert decision.allowed is True

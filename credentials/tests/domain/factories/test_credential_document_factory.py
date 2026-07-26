from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import UUID

import pytest

from credentials.domain.factories import (
    CredentialDocumentFactory,
)

CONFIRMED = "CONFIRMED"
PENDING = "PENDING"
CREDENTIAL_ID = UUID(
    "11111111-1111-1111-1111-111111111111"
)
GROUP_ID = UUID(
    "22222222-2222-2222-2222-222222222222"
)
ISSUED_AT = datetime(
    2026,
    7,
    26,
    10,
    30,
    tzinfo=timezone.utc,
)


def make_contribution(
    *,
    amount: str = "500.00",
    currency: str = "MZN",
    status: str = CONFIRMED,
    contribution_period: date = date(2026, 1, 1),
    reference: str = "CONT-001",
):
    return SimpleNamespace(
        amount=Decimal(amount),
        currency=currency,
        status=status,
        contribution_period=contribution_period,
        reference=reference,
    )


def build_document(
    contributions,
):
    return CredentialDocumentFactory().build(
        credential_id=CREDENTIAL_ID,
        issuer_did="did:mono:group:issuer-001",
        holder_did="did:mono:user:holder-001",
        group_id=GROUP_ID,
        group_name="Grupo Esperança",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
        issuance_date=ISSUED_AT,
        contributions=contributions,
    )


def test_builds_contribution_history_document() -> None:
    contributions = [
        make_contribution(
            amount="500.00",
            contribution_period=date(2026, 1, 1),
            reference="CONT-001",
        ),
        make_contribution(
            amount="750.00",
            contribution_period=date(2026, 2, 1),
            reference="CONT-002",
        ),
    ]

    document = build_document(contributions)

    assert document.to_dict() == {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
        ],
        "id": (
            "urn:uuid:"
            "11111111-1111-1111-1111-111111111111"
        ),
        "type": [
            "VerifiableCredential",
            "ContributionHistoryCredential",
        ],
        "issuer": "did:mono:group:issuer-001",
        "issuanceDate": "2026-07-26T10:30:00Z",
        "credentialSubject": {
            "id": "did:mono:user:holder-001",
            "group": {
                "id": (
                    "22222222-2222-2222-2222-"
                    "222222222222"
                ),
                "name": "Grupo Esperança",
            },
            "contributionHistory": {
                "periodStart": "2026-01-01",
                "periodEnd": "2026-03-31",
                "contributionCount": 2,
                "totalAmount": "1250.00",
                "currency": "MZN",
            },
        },
        "evidence": {
            "type": "ContributionHistory",
            "contributionReferences": [
                "CONT-001",
                "CONT-002",
            ],
        },
    }


def test_rejects_empty_contribution_history() -> None:
    with pytest.raises(
        ValueError,
        match="At least one contribution is required.",
    ):
        build_document([])


def test_rejects_unconfirmed_contribution() -> None:
    contribution = make_contribution(
        status=PENDING
    )

    with pytest.raises(
        ValueError,
        match=(
            "Only confirmed contributions can be included."
        ),
    ):
        build_document([contribution])


def test_rejects_contribution_outside_period() -> None:
    contribution = make_contribution(
        contribution_period=date(2025, 12, 1)
    )

    with pytest.raises(
        ValueError,
        match=(
            "All contributions must be within "
            "the credential period."
        ),
    ):
        build_document([contribution])


def test_rejects_multiple_currencies() -> None:
    contributions = [
        make_contribution(
            currency="MZN",
            reference="CONT-001",
        ),
        make_contribution(
            currency="USD",
            reference="CONT-002",
        ),
    ]

    with pytest.raises(
        ValueError,
        match=(
            "All contributions must use the same currency."
        ),
    ):
        build_document(contributions)


def test_rejects_invalid_period() -> None:
    factory = CredentialDocumentFactory()

    with pytest.raises(
        ValueError,
        match=(
            "Credential period end cannot be "
            "before period start."
        ),
    ):
        factory.build(
            credential_id=CREDENTIAL_ID,
            issuer_did="did:mono:group:issuer-001",
            holder_did="did:mono:user:holder-001",
            group_id=GROUP_ID,
            group_name="Grupo Esperança",
            period_start=date(2026, 3, 31),
            period_end=date(2026, 1, 1),
            issuance_date=ISSUED_AT,
            contributions=[make_contribution()],
        )

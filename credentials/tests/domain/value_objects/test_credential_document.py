# credentials/tests/domain/value_objects/test_credential_document.py

from datetime import datetime, timezone

import pytest

from credentials.domain.value_objects import CredentialDocument


def test_to_dict_returns_verifiable_credential_document() -> None:
    document = CredentialDocument(
        context=(
            "https://www.w3.org/2018/credentials/v1",
        ),
        credential_id="urn:uuid:credential-123",
        credential_types=(
            "VerifiableCredential",
            "ContributionCredential",
        ),
        issuer="did:mono:issuer-123",
        issuance_date=datetime(
            2026,
            7,
            26,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        credential_subject={
            "id": "did:mono:member-123",
            "groupId": "group-123",
            "contributionCount": 3,
        },
        evidence={
            "type": "ContributionHistory",
            "totalContributions": 3,
        },
    )

    assert document.to_dict() == {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
        ],
        "id": "urn:uuid:credential-123",
        "type": [
            "VerifiableCredential",
            "ContributionCredential",
        ],
        "issuer": "did:mono:issuer-123",
        "issuanceDate": "2026-07-26T10:30:00Z",
        "credentialSubject": {
            "id": "did:mono:member-123",
            "groupId": "group-123",
            "contributionCount": 3,
        },
        "evidence": {
            "type": "ContributionHistory",
            "totalContributions": 3,
        },
    }


def test_to_dict_omits_evidence_when_not_provided() -> None:
    document = CredentialDocument(
        context=("https://www.w3.org/2018/credentials/v1",),
        credential_id="urn:uuid:credential-123",
        credential_types=("VerifiableCredential",),
        issuer="did:mono:issuer-123",
        issuance_date=datetime.now(timezone.utc),
        credential_subject={
            "id": "did:mono:member-123",
        },
    )

    assert "evidence" not in document.to_dict()


@pytest.mark.parametrize(
    ("field_name", "overrides", "expected_message"),
    [
        (
            "context",
            {"context": ()},
            "Credential context cannot be empty.",
        ),
        (
            "credential_id",
            {"credential_id": "   "},
            "Credential ID cannot be empty.",
        ),
        (
            "credential_types",
            {"credential_types": ()},
            "Credential types cannot be empty.",
        ),
        (
            "issuer",
            {"issuer": ""},
            "Credential issuer cannot be empty.",
        ),
        (
            "credential_subject",
            {"credential_subject": {}},
            "Credential subject cannot be empty.",
        ),
    ],
)
def test_rejects_invalid_required_values(
    field_name: str,
    overrides: dict,
    expected_message: str,
) -> None:
    values = {
        "context": ("https://www.w3.org/2018/credentials/v1",),
        "credential_id": "urn:uuid:credential-123",
        "credential_types": ("VerifiableCredential",),
        "issuer": "did:mono:issuer-123",
        "issuance_date": datetime.now(timezone.utc),
        "credential_subject": {
            "id": "did:mono:member-123",
        },
    }

    values.update(overrides)

    with pytest.raises(ValueError, match=expected_message):
        CredentialDocument(**values)


def test_rejects_naive_issuance_date() -> None:
    with pytest.raises(
        ValueError,
        match="Issuance date must be timezone-aware.",
    ):
        CredentialDocument(
            context=("https://www.w3.org/2018/credentials/v1",),
            credential_id="urn:uuid:credential-123",
            credential_types=("VerifiableCredential",),
            issuer="did:mono:issuer-123",
            issuance_date=datetime(2026, 7, 26, 10, 30),
            credential_subject={
                "id": "did:mono:member-123",
            },
        )

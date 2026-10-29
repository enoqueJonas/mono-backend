"""Repository persistence must keep the same identity as the signed VC."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

from credentials.domain.value_objects import CredentialDocument, CredentialHash
from credentials.infrastructure.repositories import DjangoCredentialRepository


def test_persists_same_id_hash_document_and_expiry():
    issued_at = datetime(2026, 7, 26, 10, 30, tzinfo=timezone.utc)
    credential_id = UUID("12345678-1234-5678-1234-567812345678")
    document = CredentialDocument(
        context=("https://www.w3.org/2018/credentials/v1",),
        credential_id=f"urn:uuid:{credential_id}",
        credential_types=("VerifiableCredential",),
        issuer="did:key:issuer",
        issuance_date=issued_at,
        credential_subject={"id": "did:key:holder"},
        valid_until=issued_at + timedelta(days=365),
        proof={"type": "MonoEd25519Signature2026", "proofValue": "ztest"},
    )
    context = SimpleNamespace(
        group_member=SimpleNamespace(),
        group_did=SimpleNamespace(),
        user_did=SimpleNamespace(),
    )
    hash_value = CredentialHash(value="a" * 64)
    with patch(
        "credentials.infrastructure.repositories.django_credential_repository."
        "VerifiableCredential.objects.create"
    ) as create:
        DjangoCredentialRepository().save(
            document=document,
            credential_hash=hash_value,
            context=context,
            issued_by_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            period_start=issued_at.date(),
            period_end=(issued_at + timedelta(days=10)).date(),
        )

    saved = create.call_args.kwargs
    assert saved["id"] == credential_id
    assert saved["credential_hash"] == hash_value.value
    assert saved["credential_document"] == document.to_dict()
    assert saved["valid_from"] == issued_at
    assert saved["valid_until"] == document.valid_until

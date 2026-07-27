from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from credentials.infrastructure.repositories import (
    DjangoCredentialRepository,
)
from credentials.models import VerifiableCredential


@pytest.mark.django_db
def test_saves_credential():
    repository = DjangoCredentialRepository()

    issued_by = SimpleNamespace(
        id=uuid4(),
    )

    context = SimpleNamespace(
        group_member=SimpleNamespace(
            user=SimpleNamespace(
                id=uuid4(),
            ),
            group=SimpleNamespace(
                id=uuid4(),
            ),
        )
    )

    document = SimpleNamespace(
        id=uuid4(),
        issuer_did="did:mono:group:001",
        holder_did="did:mono:user:001",
        issuance_date=date.today(),
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        contributions=[
            SimpleNamespace(
                amount=Decimal("100"),
            )
        ],
    )

    credential = repository.save(
        document=document,
        context=context,
        issued_by_id=issued_by.id,
    )

    assert isinstance(
        credential,
        VerifiableCredential,
    )

    assert VerifiableCredential.objects.count() == 1

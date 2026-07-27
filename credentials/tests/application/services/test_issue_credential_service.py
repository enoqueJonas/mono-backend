from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

from credentials.application.services.issue_credential_service import (
    IssueCredentialService,
)
from credentials.domain.value_objects.credential_document import (
    CredentialDocument,
)
from blockchain.domain.blockchain_receipt import (
    BlockchainReceipt,
)
from credentials.domain.value_objects.credential_hash import (
    CredentialHash,
)


@patch(
    "credentials.application.services."
    "issue_credential_service.timezone.now"
)
def test_builds_document_with_issuance_context(mock_now):
    issued_at = SimpleNamespace()
    mock_now.return_value = issued_at

    factory = Mock()

    expected_document = Mock(spec=CredentialDocument)
    factory.build.return_value = expected_document

    service = IssueCredentialService(factory=factory)

    credential_id = UUID(
        "12345678-1234-5678-1234-567812345678"
    )

    context = SimpleNamespace(
        group_did=SimpleNamespace(
            did="did:mono:group:grupo-esperanca"
        ),
        user_did=SimpleNamespace(
            did="did:mono:user:841234567"
        ),
        group_member=SimpleNamespace(
            group=SimpleNamespace(
                id="group-001",
                name="Grupo Esperança",
            )
        ),
    )

    contributions = [
        SimpleNamespace(
            amount=Decimal("1000.00"),
            currency="MZN",
            status="CONFIRMED",
            contribution_period=date(2026, 1, 1),
            reference="CONT-001",
        ),
    ]

    result = service._build_document(
        credential_id=credential_id,
        context=context,
        contributions=contributions,
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
    )

    assert result is expected_document

    factory.build.assert_called_once_with(
        credential_id=credential_id,
        issuer_did="did:mono:group:grupo-esperanca",
        holder_did="did:mono:user:841234567",
        group_id="group-001",
        group_name="Grupo Esperança",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        issuance_date=issued_at,
        contributions=contributions,
    )


def test_anchors_document():
    hash_service = Mock()
    anchor_service = Mock()

    credential_hash = CredentialHash(
        value="a" * 64,
    )

    expected_receipt = Mock(
        spec=BlockchainReceipt,
    )

    hash_service.calculate.return_value = (
        credential_hash
    )

    anchor_service.anchor.return_value = (
        expected_receipt
    )

    service = IssueCredentialService(
        hash_service=hash_service,
        anchor_service=anchor_service,
    )

    document = Mock(
        spec=CredentialDocument,
    )

    result = service._anchor_document(
        document=document,
    )

    assert result is expected_receipt

    hash_service.calculate.assert_called_once_with(
        document
    )

    anchor_service.anchor.assert_called_once_with(
        credential_hash=credential_hash,
    )


def test_issue_orchestrates_credential_issuance():
    hash_service = Mock()
    anchor_service = Mock()
    credential_repository = Mock()
    blockchain_anchor_repository = Mock()

    service = IssueCredentialService(
        hash_service=hash_service,
        anchor_service=anchor_service,
        credential_repository=credential_repository,
        blockchain_anchor_repository=blockchain_anchor_repository,
    )

    context = Mock()
    context.group_member = Mock()

    contributions = Mock()

    document = Mock(spec=CredentialDocument)

    credential_hash = CredentialHash(
        value="a" * 64,
    )

    receipt = Mock(spec=BlockchainReceipt)

    service._load_context = Mock(
        return_value=context,
    )

    service._load_contributions = Mock(
        return_value=contributions,
    )

    service._evaluate_policy = Mock()

    service._build_document = Mock(
        return_value=document,
    )

    service._persist_issuance = Mock()

    hash_service.calculate.return_value = credential_hash
    anchor_service.anchor.return_value = receipt

    group_member_id = uuid4()
    issued_by_id = uuid4()

    period_start = date(2026, 1, 1)
    period_end = date(2026, 2, 1)

    result = service.issue(
        group_member_id=group_member_id,
        issued_by_id=issued_by_id,
        period_start=period_start,
        period_end=period_end,
    )

    assert result is document

    service._load_context.assert_called_once_with(
        group_member_id
    )

    service._load_contributions.assert_called_once_with(
        group_member=context.group_member,
        period_start=period_start,
        period_end=period_end,
    )

    service._evaluate_policy.assert_called_once_with(
        group_member=context.group_member,
        period_start=period_start,
        period_end=period_end,
        contributions=contributions,
    )

    service._build_document.assert_called_once()

    hash_service.calculate.assert_called_once_with(
        document
    )

    anchor_service.anchor.assert_called_once_with(
        credential_hash=credential_hash,
    )

    service._persist_issuance.assert_called_once_with(
        document=document,
        credential_hash=credential_hash,
        receipt=receipt,
        context=context,
        issued_by_id=issued_by_id,
    )


def test_persists_credential_and_blockchain_anchor():
    credential_repository = Mock()
    blockchain_anchor_repository = Mock()

    service = IssueCredentialService(
        credential_repository=credential_repository,
        blockchain_anchor_repository=blockchain_anchor_repository,
    )

    document = Mock(spec=CredentialDocument)

    credential_hash = CredentialHash(
        value="a" * 64,
    )

    receipt = Mock(spec=BlockchainReceipt)

    context = Mock()

    issued_by_id = uuid4()

    persisted_credential = Mock()
    persisted_anchor = Mock()

    credential_repository.save.return_value = (
        persisted_credential
    )

    blockchain_anchor_repository.save.return_value = (
        persisted_anchor
    )

    result = service._persist_issuance(
        document=document,
        credential_hash=credential_hash,
        receipt=receipt,
        context=context,
        issued_by_id=issued_by_id,
    )

    credential_repository.save.assert_called_once_with(
        document=document,
        credential_hash=credential_hash,
        context=context,
        issued_by_id=issued_by_id,
    )

    blockchain_anchor_repository.save.assert_called_once_with(
        credential=persisted_credential,
        receipt=receipt,
    )

    assert result.credential is persisted_credential
    assert result.blockchain_anchor is persisted_anchor

"""Regression tests for the API's active credential issuance orchestration."""
from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from blockchain.domain.blockchain_receipt import BlockchainReceipt
from credentials.application.services.issue_credential_service import IssueCredentialService
from credentials.domain.value_objects import CredentialDocument, CredentialHash
from credentials.exceptions import CredentialSignatureFailed


ISSUED_AT = datetime(2026, 7, 26, 10, 30, tzinfo=timezone.utc)


def document():
    return CredentialDocument(
        context=("https://www.w3.org/2018/credentials/v1",),
        credential_id=f"urn:uuid:{uuid4()}",
        credential_types=("VerifiableCredential",),
        issuer="did:key:issuer",
        issuance_date=ISSUED_AT,
        credential_subject={"id": "did:key:holder"},
    )


@patch("credentials.application.services.issue_credential_service.timezone.now")
def test_builds_document_with_issuance_context(mock_now):
    mock_now.return_value = ISSUED_AT
    factory = Mock()
    factory.build.return_value = document()
    service = IssueCredentialService(factory=factory)
    context = SimpleNamespace(
        group_did=SimpleNamespace(did="did:key:issuer"),
        user_did=SimpleNamespace(did="did:key:holder"),
        group_member=SimpleNamespace(group=SimpleNamespace(id="group-001", name="Grupo")),
    )
    contributions = [SimpleNamespace(amount=1000, status="CONFIRMED")]
    credential_id = uuid4()
    result = service._build_document(
        credential_id=credential_id,
        context=context,
        contributions=contributions,
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
    )
    assert result is factory.build.return_value
    factory.build.assert_called_once_with(
        credential_id=credential_id,
        issuer_did="did:key:issuer",
        holder_did="did:key:holder",
        group_id="group-001",
        group_name="Grupo",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        issuance_date=ISSUED_AT,
        contributions=contributions,
    )


def test_rejects_bad_signature_before_anchoring():
    signer = Mock()
    signer.sign.return_value = SimpleNamespace(document={"proof": {"proofValue": "invalid"}})
    signer.verify.return_value = False
    service = IssueCredentialService(signer=signer, anchor_service=Mock())
    from dataclasses import replace
    from datetime import timedelta
    unsigned = replace(document(), valid_until=ISSUED_AT + timedelta(days=365))
    with pytest.raises(CredentialSignatureFailed):
        service._sign_document(document=unsigned, issuer_identity=Mock())
    service.anchor_service.anchor.assert_not_called()


def test_issue_signs_and_anchors_same_document():
    signer, anchor_service = Mock(), Mock()
    credential_repo, anchor_repo, hash_service = Mock(), Mock(), Mock()
    credential_hash = CredentialHash(value="a" * 64)
    hash_service.calculate.return_value = credential_hash
    receipt = Mock(spec=BlockchainReceipt)
    anchor_service.anchor.return_value = receipt
    signer.verify.return_value = True
    signer.sign.side_effect = lambda **kwargs: SimpleNamespace(
        document={**kwargs["document"], "proof": {
            "type": "MonoEd25519Signature2026",
            "proofValue": "zsignature",
            "proofPurpose": "assertionMethod",
            "created": "2026-07-26T10:30:00Z",
        }}
    )
    saved = Mock()
    credential_repo.save.return_value = saved
    service = IssueCredentialService(
        signer=signer,
        anchor_service=anchor_service,
        credential_repository=credential_repo,
        blockchain_anchor_repository=anchor_repo,
        hash_service=hash_service,
    )
    ctx = SimpleNamespace(group_did=Mock(), group_member=Mock())
    base_document = document()
    service._load_context = Mock(return_value=ctx)
    service._load_contributions = Mock(return_value=[Mock()])
    service._evaluate_policy = Mock()
    service._build_document = Mock(return_value=base_document)

    result = service.issue(
        group_member_id=uuid4(),
        issued_by_id=uuid4(),
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
    )
    assert result is saved
    signed_doc = hash_service.calculate.call_args.args[0]
    assert signed_doc.to_dict()["proof"]["proofValue"] == "zsignature"
    assert signed_doc.to_dict()["validUntil"] == "2027-07-26T10:30:00Z"
    assert credential_repo.save.call_args.kwargs["document"] is signed_doc
    anchor_service.anchor.assert_called_once_with(credential_hash=credential_hash)
    signer.verify.assert_called_once()
    anchor_repo.save.assert_called_once_with(credential=saved, receipt=receipt)

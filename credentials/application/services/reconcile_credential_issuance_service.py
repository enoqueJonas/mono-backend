"""Recover a pre-committed credential whose ledger transaction already succeeded.

The operation is deliberately NOT a second attempt to anchor the hash:
a missing on-chain record remains pending for operator investigation.
"""
from django.db import transaction

from blockchain.models import BlockchainAnchor, BlockchainAnchorType
from blockchain.services.anchor_service import AnchorService
from credentials.domain.value_objects import CredentialHash
from credentials.infrastructure.repositories import DjangoBlockchainAnchorRepository
from credentials.models import VerifiableCredential


class ReconciliationNotReady(Exception):
    """The intent cannot yet be finalized safely."""


class ReconcileCredentialIssuanceService:
    def __init__(self, *, anchor_service=None, anchor_repository=None):
        self.anchor_service = anchor_service
        self.anchor_repository = (
            anchor_repository
            if anchor_repository is not None
            else DjangoBlockchainAnchorRepository()
        )

    @transaction.atomic
    def reconcile(self, *, credential_id) -> VerifiableCredential:
        # Lock the pending intent to make concurrent reconciliation safe.
        credential = VerifiableCredential.objects.select_for_update().get(
            id=credential_id
        )
        if credential.status == VerifiableCredential.Status.ACTIVE:
            return credential
        if credential.status != VerifiableCredential.Status.PENDING:
            raise ReconciliationNotReady(
                "Only pending credentials can be reconciled."
            )
        credential_hash = CredentialHash(value=credential.credential_hash)
        anchor = self.anchor_service or AnchorService()
        if not anchor.credential_exists(credential_hash):
            raise ReconciliationNotReady(
                "The hash is not confirmed on chain; do not blindly reanchor."
            )
        state = anchor.get_credential(credential_hash)
        if not state.get("exists") or state.get("revoked"):
            raise ReconciliationNotReady(
                "The on-chain anchor is missing or already revoked."
            )
        receipt = anchor.recover_anchoring_receipt(credential_hash)
        if not receipt.status:
            raise ReconciliationNotReady("On-chain transaction has failed.")
        local_anchors = BlockchainAnchor.objects.filter(
            credential=credential,
            anchor_type=BlockchainAnchorType.CREDENTIAL,
        )
        if not local_anchors.exists():
            self.anchor_repository.save(credential=credential, receipt=receipt)
        credential.status = VerifiableCredential.Status.ACTIVE
        credential.save(update_fields=["status"])
        return credential

from datetime import datetime
from uuid import UUID

from django.utils import timezone

from blockchain.services.anchor_service import AnchorService
from blockchain.utils.hashing import HashingService
from credentials.application.services.credential_signature_service import verify_signature
from credentials.domain.value_objects import CredentialHash
from credentials.models import VerifiableCredential


class VerifyCredentialService:
    def __init__(self, *, anchor_service: AnchorService | None = None) -> None:
        self.anchor_service = anchor_service or AnchorService()

    def verify(self, *, credential: dict) -> bool:
        # Legacy unsigned documents are not accepted as signed credentials.
        if not isinstance(credential, dict) or not verify_signature(credential):
            return False

        try:
            issued_at = datetime.fromisoformat(credential["issuanceDate"].replace("Z", "+00:00"))
            expires_at = datetime.fromisoformat(credential["expirationDate"].replace("Z", "+00:00"))
            now = timezone.now()
            if issued_at.tzinfo is None or expires_at.tzinfo is None:
                return False
            if issued_at > now or expires_at <= now or expires_at <= issued_at:
                return False
        except (KeyError, AttributeError, TypeError, ValueError):
            return False

        credential_hash = CredentialHash(
            value=HashingService.hash_json_hex(credential)
        )
        anchor = self.anchor_service.get_credential(
            credential_hash=credential_hash,
        )
        if not anchor["exists"] or anchor["revoked"]:
            return False

        stored = VerifiableCredential.objects.select_related("issuer_did").filter(
            credential_hash=credential_hash.value,
        ).first()
        if stored is None or stored.status != VerifiableCredential.Status.ACTIVE:
            return False
        if stored.issuer_did.did != credential["issuer"]:
            return False
        if stored.credential_document != credential:
            return False
        try:
            document_id = UUID(credential["id"].removeprefix("urn:uuid:"))
        except (KeyError, AttributeError, TypeError, ValueError):
            return False
        if stored.id != document_id:
            return False
        if stored.valid_until is not None and now >= stored.valid_until:
            return False
        return True

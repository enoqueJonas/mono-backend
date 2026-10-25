from django.utils import timezone

from blockchain.services.anchor_service import AnchorService
from blockchain.utils.hashing import HashingService
from credentials.domain.value_objects import CredentialHash
from credentials.models import VerifiableCredential


class VerifyCredentialService:
    def __init__(
        self,
        *,
        anchor_service: AnchorService | None = None,
    ) -> None:
        self.anchor_service = anchor_service or AnchorService()

    def verify(self, *, credential: dict) -> bool:
        credential_hash = CredentialHash(
            value=HashingService.hash_json_hex(credential)
        )
        anchor = self.anchor_service.get_credential(
            credential_hash=credential_hash,
        )
        if not anchor["exists"] or anchor["revoked"]:
            return False

        # Existing credentials store their expiry in the database rather
        # than in the anchored JSON document.
        stored = VerifiableCredential.objects.filter(
            credential_hash=credential_hash.value,
        ).first()
        if stored is None or stored.status != VerifiableCredential.Status.ACTIVE:
            return False
        if stored.valid_until is not None and timezone.now() >= stored.valid_until:
            return False

        return True

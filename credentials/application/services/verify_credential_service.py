from blockchain.services.anchor_service import AnchorService
from blockchain.utils.hashing import HashingService
from credentials.domain.value_objects import CredentialHash


class VerifyCredentialService:
    def __init__(
        self,
        *,
        anchor_service: AnchorService | None = None,
    ) -> None:
        self.anchor_service = (
            anchor_service or AnchorService()
        )

    def verify(
        self,
        *,
        credential: dict,
    ) -> bool:

        credential_hash = CredentialHash(
            value=HashingService.hash_json_hex(
                credential
            )
        )

        return self.anchor_service.credential_exists(
            credential_hash=credential_hash,
        )

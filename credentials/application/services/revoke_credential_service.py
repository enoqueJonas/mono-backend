from blockchain.services.anchor_service import AnchorService
from groups.services.group_service import GroupService
from credentials.infrastructure.repositories.django_credential_repository import (
    DjangoCredentialRepository,
)
from credentials.models import VerifiableCredential
from credentials.domain.value_objects import (
    CredentialHash,
)


class RevokeCredentialService:
    def __init__(
        self,
        *,
        credential_repository=None,
        anchor_service=None,
    ):

        self.credential_repository = (
            credential_repository
            or DjangoCredentialRepository()
        )

        self.anchor_service = (
            anchor_service
            or AnchorService()
        )

    def revoke(
        self,
        *,
        credential_id,
        reason: str = "",
        revoked_by=None,
    ):

        credential = (
            self.credential_repository.get_by_id(
                credential_id
            )
        )

        if revoked_by is None:
            raise PermissionError('Revocation requires an authenticated actor.')
        GroupService.ensure_manager(
            group_id=credential.group_member.group_id,
            user=revoked_by,
        )

        if credential.status == VerifiableCredential.Status.REVOKED:
            return credential

        self.anchor_service.revoke(
            CredentialHash(
                value=credential.credential_hash
            )
        )

        return self.credential_repository.revoke(
            credential=credential,
            reason=reason,
        )

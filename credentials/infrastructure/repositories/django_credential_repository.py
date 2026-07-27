from django.utils import timezone

from credentials.application.repositories import (
    CredentialRepository,
)
from credentials.domain.value_objects import (
    CredentialHash,
    CredentialDocument,
)
from credentials.models import VerifiableCredential


class DjangoCredentialRepository(
    CredentialRepository,
):
    def save(
        self,
        *,
        document: CredentialDocument,
        credential_hash: CredentialHash,
        context,
        issued_by_id,
        period_start,
        period_end,
    ) -> VerifiableCredential:

        return VerifiableCredential.objects.create(
            group_member=context.group_member,
            issued_by_id=issued_by_id,
            issuer_did=context.group_did,
            holder_did=context.user_did,
            period_start=period_start,
            period_end=period_end,
            valid_from=document.issuance_date,
            credential_document=document.to_dict(),
            credential_hash=credential_hash.value,
        )

    def get_by_id(
        self,
        credential_id,
    ) -> VerifiableCredential:
        return VerifiableCredential.objects.get(
            id=credential_id
        )

    def revoke(
        self,
        *,
        credential: VerifiableCredential,
        reason: str = "",
    ) -> VerifiableCredential:

        credential.status = (
            VerifiableCredential.Status.REVOKED
        )

        credential.revoked_at = timezone.now()

        credential.revocation_reason = reason

        credential.save(
            update_fields=[
                "status",
                "revoked_at",
                "revocation_reason",
            ]
        )
        return credential

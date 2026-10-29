"""Credential revocation with mandatory application-level actor authorization."""
from django.http import Http404
from rest_framework.exceptions import PermissionDenied, ValidationError

from blockchain.services.anchor_service import AnchorService
from credentials.infrastructure.repositories.django_credential_repository import (
    DjangoCredentialRepository,
)
from credentials.domain.value_objects import CredentialHash
from credentials.models import VerifiableCredential
from groups.models import GroupMember


class RevokeCredentialService:
    def __init__(self, *, credential_repository=None, anchor_service=None):
        self.credential_repository = (
            credential_repository
            if credential_repository is not None
            else DjangoCredentialRepository()
        )
        self.anchor_service = (
            anchor_service if anchor_service is not None else AnchorService()
        )

    def revoke(self, *, credential_id, actor, reason: str = ""):
        # Retrieve only by ID, then check manager membership before touching the chain.
        try:
            credential = self.credential_repository.get_by_id(credential_id)
        except VerifiableCredential.DoesNotExist as exc:
            raise Http404("Credential not found") from exc

        if actor is None or not getattr(actor, "is_authenticated", False):
            raise PermissionDenied("Authentication required for revocation.")

        manager = GroupMember.objects.filter(
            user=actor,
            group_id=credential.group_member.group_id,
            role=GroupMember.Role.MANAGER,
            status=GroupMember.Status.ACTIVE,
        ).exists()
        if not manager:
            raise PermissionDenied(
                "Only an active manager of the credential's group may revoke it."
            )
        if credential.status == VerifiableCredential.Status.REVOKED:
            raise ValidationError("Credential is already revoked.")

        self.anchor_service.revoke(
            CredentialHash(value=credential.credential_hash)
        )
        return self.credential_repository.revoke(
            credential=credential, reason=reason
        )

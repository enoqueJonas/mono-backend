from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID, uuid4

from django.db import transaction
from django.utils import timezone

from blockchain.domain.blockchain_receipt import BlockchainReceipt
from blockchain.services.anchor_service import AnchorService
from contributions.models import Contribution
from credentials.application.services.context import (
    CredentialIssuanceContext,
)
from credentials.application.services.credential_hash_service import (
    CredentialHashService,
)
from credentials.domain.factories import CredentialDocumentFactory
from credentials.domain.policies import CredentialIssuancePolicy
from credentials.domain.value_objects import (
    CredentialDocument,
    CredentialHash,
)
from credentials.exceptions import (
    CredentialAlreadyExists,
    InactiveCredentialHolder,
    InvalidCredentialPeriod,
    MissingHolderDID,
    MissingIssuerDID,
    NoConfirmedContributions,
)
from credentials.infrastructure.repositories import (
    DjangoBlockchainAnchorRepository,
    DjangoCredentialRepository,
)
from credentials.models import VerifiableCredential
from groups.models import GroupMember
from identity.models import GroupDID, UserDID


@dataclass(frozen=True)
class PersistedCredentialIssuance:
    credential: Any
    blockchain_anchor: Any


class IssueCredentialService:
    def __init__(
        self,
        *,
        policy=None,
        factory=None,
        hash_service: CredentialHashService | None = None,
        anchor_service=None,
        credential_repository=None,
        blockchain_anchor_repository=None,
    ) -> None:
        self.policy = policy or CredentialIssuancePolicy()
        self.factory = factory or CredentialDocumentFactory()
        self.hash_service = (
            hash_service
            or CredentialHashService()
        )
        self.anchor_service = anchor_service
        self.credential_repository = (
            credential_repository
            or DjangoCredentialRepository()
        )
        self.blockchain_anchor_repository = (
            blockchain_anchor_repository
            or DjangoBlockchainAnchorRepository()
        )

    @transaction.atomic
    def issue(
        self,
        *,
        group_member_id: UUID,
        issued_by_id: UUID,
        period_start: date,
        period_end: date,
    ) -> VerifiableCredential:
        context = self._load_context(
            group_member_id=group_member_id,
        )

        contributions = list(
            self._load_contributions(
                group_member=context.group_member,
                period_start=period_start,
                period_end=period_end,
            )
        )

        self._evaluate_policy(
            group_member=context.group_member,
            period_start=period_start,
            period_end=period_end,
            contributions=contributions,
        )

        credential_id = uuid4()

        document = self._build_document(
            credential_id=credential_id,
            context=context,
            contributions=contributions,
            period_start=period_start,
            period_end=period_end,
        )

        credential_hash = self.hash_service.calculate(
            document
        )

        if self.anchor_service is None:
            self.anchor_service = AnchorService()

        receipt = self.anchor_service.anchor(
            credential_hash=credential_hash,
        )

        persisted = self._persist_issuance(
            document=document,
            credential_hash=credential_hash,
            receipt=receipt,
            context=context,
            issued_by_id=issued_by_id,
            period_start=period_start,
            period_end=period_end,
        )

        return persisted.credential

    def _load_context(
        self,
        *,
        group_member_id: UUID,
    ) -> CredentialIssuanceContext:
        group_member = (
            GroupMember.objects
            .select_related(
                "group",
                "group__settings",
                "user",
            )
            .get(id=group_member_id)
        )

        group_did = (
            GroupDID.objects
            .filter(
                group=group_member.group,
                status=GroupDID.Status.ACTIVE,
            )
            .first()
        )

        if group_did is None:
            raise MissingIssuerDID()

        user_did = (
            UserDID.objects
            .filter(
                user=group_member.user,
                status=UserDID.Status.ACTIVE,
            )
            .first()
        )

        if user_did is None:
            raise MissingHolderDID()

        return CredentialIssuanceContext(
            group_member=group_member,
            group_did=group_did,
            user_did=user_did,
        )

    def _load_contributions(
        self,
        *,
        group_member: GroupMember,
        period_start: date,
        period_end: date,
    ):
        return (
            Contribution.objects
            .filter(
                member=group_member,
                status=Contribution.Status.CONFIRMED,
                contribution_period__gte=period_start,
                contribution_period__lte=period_end,
            )
            .order_by(
                "contribution_period",
                "created_at",
            )
        )

    def _evaluate_policy(
        self,
        *,
        group_member: GroupMember,
        period_start: date,
        period_end: date,
        contributions,
    ) -> None:
        if period_end < period_start:
            raise InvalidCredentialPeriod()

        if (
            group_member.status
            != GroupMember.Status.ACTIVE
        ):
            raise InactiveCredentialHolder()

        if not contributions:
            raise NoConfirmedContributions()

        credential_exists = (
            VerifiableCredential.objects
            .filter(
                group_member=group_member,
                credential_type=(
                    VerifiableCredential
                    .CredentialType
                    .CONTRIBUTION_HISTORY
                ),
                period_start=period_start,
                period_end=period_end,
                status=(
                    VerifiableCredential
                    .Status
                    .ACTIVE
                ),
            )
            .exists()
        )

        if credential_exists:
            raise CredentialAlreadyExists()

    def _build_document(
        self,
        *,
        context: CredentialIssuanceContext,
        period_start: date,
        period_end: date,
        contributions,
        credential_id: UUID,
    ) -> CredentialDocument:
        return self.factory.build(
            credential_id=credential_id,
            issuer_did=context.group_did.did,
            holder_did=context.user_did.did,
            group_id=context.group_member.group.id,
            group_name=context.group_member.group.name,
            period_start=period_start,
            period_end=period_end,
            issuance_date=timezone.now(),
            contributions=contributions,
        )

    def _persist_issuance(
        self,
        *,
        document: CredentialDocument,
        credential_hash: CredentialHash,
        receipt: BlockchainReceipt,
        context: CredentialIssuanceContext,
        issued_by_id: UUID,
        period_start: date,
        period_end: date,
    ) -> PersistedCredentialIssuance:
        credential = self.credential_repository.save(
            document=document,
            credential_hash=credential_hash,
            context=context,
            issued_by_id=issued_by_id,
            period_start=period_start,
            period_end=period_end,
        )

        blockchain_anchor = (
            self.blockchain_anchor_repository.save(
                credential=credential,
                receipt=receipt,
            )
        )

        return PersistedCredentialIssuance(
            credential=credential,
            blockchain_anchor=blockchain_anchor,
        )

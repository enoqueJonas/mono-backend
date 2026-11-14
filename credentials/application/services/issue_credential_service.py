from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
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
    CredentialSignatureFailed,
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
from credentials.services.credential_signer import CredentialSigner
from groups.models import GroupMember
from identity.models import GroupDID, UserDID


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
        signer=None,
    ) -> None:
        self.signer = signer or CredentialSigner()
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

    def issue(
        self,
        *,
        group_member_id: UUID,
        issued_by_id: UUID,
        period_start: date,
        period_end: date,
    ) -> VerifiableCredential:
        # Phase 1: commit the signed document and its hash before any
        # irreversible blockchain transaction.
        with transaction.atomic():
            context = self._load_context(group_member_id=group_member_id)
            contributions = list(self._load_contributions(
                group_member=context.group_member,
                period_start=period_start,
                period_end=period_end,
            ))
            self._evaluate_policy(
                group_member=context.group_member,
                period_start=period_start,
                period_end=period_end,
                contributions=contributions,
            )
            document = self._build_document(
                credential_id=uuid4(),
                context=context,
                contributions=contributions,
                period_start=period_start,
                period_end=period_end,
            )
            document = replace(
                document,
                valid_until=(
                    document.issuance_date
                    + timedelta(days=DjangoCredentialRepository.DEFAULT_VALIDITY_DAYS)
                ),
            )
            document = self._sign_document(
                document=document, issuer_identity=context.group_did
            )
            credential_hash = self.hash_service.calculate(document)
            prepared = self.credential_repository.save(
                document=document,
                credential_hash=credential_hash,
                context=context,
                issued_by_id=issued_by_id,
                period_start=period_start,
                period_end=period_end,
            )

        # Phase 2: irreversible ledger transaction; PENDING survives failure.
        blockchain = self.anchor_service or AnchorService()
        receipt = blockchain.anchor(credential_hash=credential_hash)

        # Phase 3: receipt and active state committed in one SQL transaction.
        self._complete_issuance(credential=prepared, receipt=receipt)
        return prepared

    def _load_context(
        self,
        *,
        group_member_id: UUID,
    ) -> CredentialIssuanceContext:
        group_member = (
            GroupMember.objects
            .select_related(
                "group",
                "user",
            )
            .select_for_update()
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
                status__in=[
                    VerifiableCredential.Status.ACTIVE,
                    VerifiableCredential.Status.PENDING,
                ],
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

    def _sign_document(
        self,
        *,
        document: CredentialDocument,
        issuer_identity: GroupDID,
    ) -> CredentialDocument:
        signed = self.signer.sign(
            document=document.to_dict(),
            issuer_identity=issuer_identity,
            created_at=document.issuance_date,
        )
        if not self.signer.verify(
            signed_document=signed.document,
            issuer_identity=issuer_identity,
        ):
            raise CredentialSignatureFailed()

        proof = signed.document.get("proof")
        if not isinstance(proof, dict):
            raise CredentialSignatureFailed()
        return replace(document, proof=proof)

    @transaction.atomic
    def _complete_issuance(
        self,
        *,
        credential: VerifiableCredential,
        receipt: BlockchainReceipt,
    ) -> VerifiableCredential:
        self.blockchain_anchor_repository.save(
            credential=credential, receipt=receipt
        )
        credential.status = VerifiableCredential.Status.ACTIVE
        credential.save(update_fields=["status"])
        return credential

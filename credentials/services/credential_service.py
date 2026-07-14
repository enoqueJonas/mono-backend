import uuid
from datetime import date, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from credentials.exceptions import (
    CredentialAlreadyExists,
    CredentialSignatureFailed,
    InactiveCredentialHolder,
    InvalidCredentialPeriod,
    MissingHolderDID,
    MissingIssuerDID,
    NoConfirmedContributions,
    NotCredentialIssuer,
)
from credentials.models import VerifiableCredential
from credentials.selectors.contribution_history_selector import (
    ContributionHistorySelector,
)
from credentials.services.credential_builder import (
    CredentialBuildData,
    CredentialBuilder,
)
from credentials.services.credential_signer import (
    CredentialSigner,
)
from credentials.utils.canonical_json import calculate_sha256
from groups.models import GroupMember
from identity.models import GroupDID, UserDID


class CredentialService:
    DEFAULT_VALIDITY_DAYS = 365

    @classmethod
    @transaction.atomic
    def issue_contribution_credential(
        cls,
        *,
        group_member: GroupMember,
        issued_by: GroupMember,
        period_start: date,
        period_end: date,
    ) -> VerifiableCredential:
        cls._validate_issuer(
            group_member=group_member,
            issued_by=issued_by,
        )

        cls._validate_period(
            period_start=period_start,
            period_end=period_end,
        )

        if group_member.status != GroupMember.Status.ACTIVE:
            raise InactiveCredentialHolder()

        existing_credential = (
            VerifiableCredential.objects.filter(
                group_member=group_member,
                credential_type=(
                    VerifiableCredential
                    .CredentialType
                    .CONTRIBUTION_HISTORY
                ),
                period_start=period_start,
                period_end=period_end,
                status=VerifiableCredential.Status.ACTIVE,
            )
            .first()
        )

        if existing_credential is not None:
            raise CredentialAlreadyExists()

        issuer_did = cls._get_issuer_did(
            group_member=group_member,
        )

        holder_did = cls._get_holder_did(
            group_member=group_member,
        )

        history = ContributionHistorySelector.summarize(
            group_member=group_member,
            period_start=period_start,
            period_end=period_end,
        )

        if history.confirmed_contributions == 0:
            raise NoConfirmedContributions()

        credential_id = uuid.uuid4()
        valid_from = timezone.now()
        valid_until = valid_from + timedelta(
            days=cls.DEFAULT_VALIDITY_DAYS
        )

        unsigned_document = CredentialBuilder.build_unsigned(
            data=CredentialBuildData(
                credential_id=credential_id,
                group_member=group_member,
                issuer_did=issuer_did,
                holder_did=holder_did,
                period_start=period_start,
                period_end=period_end,
                valid_from=valid_from,
                valid_until=valid_until,
                confirmed_contributions=(
                    history.confirmed_contributions
                ),
                total_contributed=history.total_contributed,
                currency=history.currency,
            )
        )

        signed = CredentialSigner.sign(
            document=unsigned_document,
            issuer_identity=issuer_did,
            created_at=valid_from,
        )

        signature_is_valid = CredentialSigner.verify(
            signed_document=signed.document,
            issuer_identity=issuer_did,
        )

        if not signature_is_valid:
            raise CredentialSignatureFailed()

        credential_hash = calculate_sha256(
            signed.document
        )

        try:
            credential = VerifiableCredential.objects.create(
                id=credential_id,
                group_member=group_member,
                issued_by=issued_by,
                issuer_did=issuer_did,
                holder_did=holder_did,
                credential_type=(
                    VerifiableCredential
                    .CredentialType
                    .CONTRIBUTION_HISTORY
                ),
                period_start=period_start,
                period_end=period_end,
                valid_from=valid_from,
                valid_until=valid_until,
                credential_document=signed.document,
                credential_hash=credential_hash,
                status=VerifiableCredential.Status.ACTIVE,
            )
        except IntegrityError as exc:
            raise CredentialAlreadyExists() from exc

        return credential

    @staticmethod
    def _validate_issuer(
        *,
        group_member: GroupMember,
        issued_by: GroupMember,
    ) -> None:
        same_group = (
            issued_by.group_id
            == group_member.group_id
        )

        is_active_manager = (
            issued_by.role == GroupMember.Role.MANAGER
            and issued_by.status == GroupMember.Status.ACTIVE
        )

        if not same_group or not is_active_manager:
            raise NotCredentialIssuer()

    @staticmethod
    def _validate_period(
        *,
        period_start: date,
        period_end: date,
    ) -> None:
        if period_end < period_start:
            raise InvalidCredentialPeriod()

    @staticmethod
    def _get_issuer_did(
        *,
        group_member: GroupMember,
    ) -> GroupDID:
        issuer_did = (
            GroupDID.objects
            .filter(
                group=group_member.group,
                status=GroupDID.Status.ACTIVE,
            )
            .first()
        )

        if issuer_did is None:
            raise MissingIssuerDID()

        return issuer_did

    @staticmethod
    def _get_holder_did(
        *,
        group_member: GroupMember,
    ) -> UserDID:
        holder_did = (
            UserDID.objects
            .filter(
                user=group_member.user,
                status=UserDID.Status.ACTIVE,
            )
            .first()
        )

        if holder_did is None:
            raise MissingHolderDID()

        return holder_did

    @classmethod
    def issue_for_group(
        cls,
        *,
        group_id,
        group_member_id,
        issued_by_user,
        period_start,
        period_end,
    ) -> VerifiableCredential:
        holder_membership = (
            GroupMember.objects
            .select_related(
                "group",
                "group__settings",
                "user",
            )
            .filter(
                id=group_member_id,
                group_id=group_id,
            )
            .first()
        )

        if holder_membership is None:
            raise CredentialHolderNotFound()

        issuer_membership = (
            GroupMember.objects
            .select_related(
                "group",
                "user",
            )
            .filter(
                group_id=group_id,
                user=issued_by_user,
                role=GroupMember.Role.MANAGER,
                status=GroupMember.Status.ACTIVE,
            )
            .first()
        )

        if issuer_membership is None:
            raise NotCredentialIssuer()

        return cls.issue_contribution_credential(
            group_member=holder_membership,
            issued_by=issuer_membership,
            period_start=period_start,
            period_end=period_end,
        )

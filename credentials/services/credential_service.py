import uuid
from datetime import date, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from credentials.exceptions import (
    CredentialAlreadyExists,
    CredentialHolderNotFound,
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
from credentials.application.services.issue_credential_service import (
    IssueCredentialService,
)
from credentials.utils.canonical_json import calculate_sha256
from groups.models import GroupMember
from identity.models import GroupDID, UserDID


class CredentialService:
    DEFAULT_VALIDITY_DAYS = 365

    @classmethod
    def issue_contribution_credential(
        cls,
        *,
        group_member: GroupMember,
        issued_by: GroupMember,
        period_start: date,
        period_end: date,
    ) -> VerifiableCredential:
        """Compatibility entry point; all issuance uses the anchored signed flow."""
        cls._validate_issuer(
            group_member=group_member,
            issued_by=issued_by,
        )
        return IssueCredentialService().issue(
            group_member_id=group_member.id,
            issued_by_id=issued_by.id,
            period_start=period_start,
            period_end=period_end,
        )

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

        return IssueCredentialService().issue(
            group_member_id=holder_membership.id,
            issued_by_id=issuer_membership.id,
            period_start=period_start,
            period_end=period_end,
        )
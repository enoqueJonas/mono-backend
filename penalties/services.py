from django.db import transaction
from django.utils import timezone

from core.exceptions import DomainException
from groups.models import GroupMember
from penalties.models import Penalty
from groups.services.group_service import GroupService


class InactivePenaltyMember(DomainException):
    default_message = (
        "A penalty can only be applied "
        "to an active member."
    )


class PenaltyReasonRequired(DomainException):
    default_message = (
        "A penalty must have a reason."
    )


class PenaltyNotFound(DomainException):
    default_message = "Penalty not found."


class PenaltyAlreadyResolved(DomainException):
    default_message = (
        "The penalty is already resolved."
    )


class PenaltyService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        member: GroupMember,
        reason: str,
    ) -> Penalty:

        if (
            member.status
            != GroupMember.Status.ACTIVE
        ):
            raise InactivePenaltyMember()

        if not reason or not reason.strip():
            raise PenaltyReasonRequired()

        return Penalty.objects.create(
            member=member,
            reason=reason.strip(),
            status=Penalty.Status.ACTIVE,
        )

    @staticmethod
    @transaction.atomic
    def create_for_group(
        *,
        group_id,
        member_id,
        created_by,
        reason,
    ) -> Penalty:

        GroupService.ensure_manager(
            group_id=group_id,
            user=created_by,
        )

        member = (
            GroupMember.objects
            .filter(
                id=member_id,
                group_id=group_id,
            )
            .first()
        )

        if member is None:
            raise DomainException(
                "Member not found in this group."
            )

        return PenaltyService.create(
            member=member,
            reason=reason,
        )

    @staticmethod
    @transaction.atomic
    def resolve(
        *,
        penalty_id,
    ) -> Penalty:

        penalty = (
            Penalty.objects
            .select_for_update()
            .filter(id=penalty_id)
            .first()
        )

        if penalty is None:
            raise PenaltyNotFound()

        if (
            penalty.status
            == Penalty.Status.RESOLVED
        ):
            raise PenaltyAlreadyResolved()

        penalty.status = Penalty.Status.RESOLVED
        penalty.resolved_at = timezone.now()

        penalty.save(
            update_fields=[
                "status",
                "resolved_at",
                "updated_at",
            ]
        )

        return penalty

    @staticmethod
    @transaction.atomic
    def resolve_for_group(
        *,
        group_id,
        penalty_id,
        resolved_by,
    ) -> Penalty:

        GroupService.ensure_manager(
            group_id=group_id,
            user=resolved_by,
        )

        penalty = (
            Penalty.objects
            .filter(
                id=penalty_id,
                member__group_id=group_id,
            )
            .first()
        )

        if penalty is None:
            raise PenaltyNotFound()

        return PenaltyService.resolve(
            penalty_id=penalty.id,
        )

    @staticmethod
    def has_active_penalty(
        *,
        member: GroupMember,
    ) -> bool:

        return Penalty.objects.filter(
            member=member,
            status=Penalty.Status.ACTIVE,
        ).exists()

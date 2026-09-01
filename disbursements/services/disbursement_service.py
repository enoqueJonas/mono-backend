from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from core.exceptions import DomainException
from contributions.models import Contribution
from disbursements.models import Disbursement
from groups.models import (
    Group,
    GroupMember,
    RotationOrder,
)
from groups.services.rotation_service import (
    CurrentRotationNotFound,
    RotationCycleNotFound,
    RotationService,
)


class DisbursementAlreadyExists(DomainException):
    default_message = (
        "A disbursement already exists for "
        "this rotation position."
    )


class InactiveBeneficiary(DomainException):
    default_message = (
        "The current beneficiary is not active."
    )


class NoConfirmedContributions(DomainException):
    default_message = (
        "There are no confirmed contributions "
        "available for this cycle."
    )


class IncompleteContributions(DomainException):
    default_message = (
        "Not all expected contributions are confirmed."
    )


class ArchivedGroup(DomainException):
    default_message = (
        "Archived groups cannot create disbursements."
    )


class DisbursementService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        group_id,
        cycle_number: int,
    ) -> Disbursement:

        try:
            group = Group.objects.get(
                id=group_id,
            )
        except Group.DoesNotExist:
            raise RotationCycleNotFound()

        if group.status == Group.Status.ARCHIVED:
            raise ArchivedGroup()

        current_rotation = (
            RotationService.get_current(
                group=group,
                cycle_number=cycle_number,
            )
        )

        beneficiary = current_rotation.member

        if (
            beneficiary.status
            != GroupMember.Status.ACTIVE
        ):
            raise InactiveBeneficiary()

        if Disbursement.objects.filter(
            rotation_order=current_rotation,
        ).exists():
            raise DisbursementAlreadyExists()

        settings = current_rotation.group_settings

        active_members_count = (
            GroupMember.objects
            .filter(
                group=group,
                status=GroupMember.Status.ACTIVE,
            )
            .count()
        )

        confirmed_contributions = (
            Contribution.objects
            .filter(
                member__group=group,
                status=Contribution.Status.CONFIRMED,
                group_settings=settings,
                contribution_period=(
                    current_rotation.contribution_period
                ),
            )
        )

        confirmed_count = (
            confirmed_contributions.count()
        )

        if confirmed_count == 0:
            raise NoConfirmedContributions()

        if confirmed_count < active_members_count:
            raise IncompleteContributions()

        total = (
            confirmed_contributions
            .aggregate(
                total=Sum("amount")
            )
            .get("total")
        )

        if total is None:
            total = Decimal("0.00")

        status = (
            Disbursement.Status.AWAITING_CONSENSUS
            if settings.requires_consensus
            else Disbursement.Status.APPROVED
        )

        return Disbursement.objects.create(
            group=group,
            beneficiary=beneficiary,
            rotation_order=current_rotation,
            group_settings=settings,
            cycle_number=cycle_number,
            amount=total,
            currency=settings.currency,
            status=status,
        )

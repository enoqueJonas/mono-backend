from decimal import Decimal
from django.utils import timezone
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
from groups.services.group_service import GroupService
from penalties.services import PenaltyService


class ActivePenalty(DomainException):
    default_message = (
        "O beneficiário possui uma penalização activa "
        "e não pode receber um desembolso."
    )


class InvalidDisbursementStatus(DomainException):
    default_message = (
        "O desembolso não se encontra num estado válido "
        "para esta operação."
    )


class DisbursementNotFound(DomainException):
    default_message = "Desembolso não encontrado."


class DisbursementAlreadyExists(DomainException):
    default_message = (
        "Já existe um desembolso para esta posição da rotação."
    )


class InactiveBeneficiary(DomainException):
    default_message = (
        "O beneficiário actual não está activo."
    )


class NoConfirmedContributions(DomainException):
    default_message = (
        "Não existem contribuições confirmadas disponíveis "
        "para este ciclo."
    )


class IncompleteContributions(DomainException):
    default_message = (
        "Nem todas as contribuições esperadas estão confirmadas."
    )


class ArchivedGroup(DomainException):
    default_message = (
        "Grupos arquivados não podem criar desembolsos."
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

        if PenaltyService.has_active_penalty(
            member=beneficiary,
        ):
            raise ActivePenalty()

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

    @staticmethod
    @transaction.atomic
    def approve(
        *,
        disbursement_id,
        approved_by,
    ) -> Disbursement:

        disbursement = (
            Disbursement.objects
            .select_for_update()
            .filter(id=disbursement_id)
            .first()
        )

        if disbursement is None:
            raise DisbursementNotFound()

        GroupService.ensure_manager(
            group_id=disbursement.group_id,
            user=approved_by,
        )

        if (
            disbursement.status
            != Disbursement.Status.AWAITING_CONSENSUS
        ):
            raise InvalidDisbursementStatus()

        disbursement.status = (
            Disbursement.Status.APPROVED
        )

        disbursement.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return disbursement

    @staticmethod
    @transaction.atomic
    def complete(
        *,
        disbursement_id,
        completed_by,
    ) -> Disbursement:

        disbursement = (
            Disbursement.objects
            .select_for_update()
            .select_related(
                "group",
                "rotation_order",
            )
            .filter(id=disbursement_id)
            .first()
        )

        if disbursement is None:
            raise DisbursementNotFound()

        GroupService.ensure_manager(
            group_id=disbursement.group_id,
            user=completed_by,
        )

        if (
            disbursement.status
            != Disbursement.Status.APPROVED
        ):
            raise InvalidDisbursementStatus()

        disbursement.status = (
            Disbursement.Status.COMPLETED
        )
        disbursement.completed_at = timezone.now()

        disbursement.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

        RotationService.advance(
            group=disbursement.group,
            cycle_number=disbursement.cycle_number,
        )

        return disbursement

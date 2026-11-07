from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from contributions.models import Contribution
from core.exceptions import DomainException
from disbursements.models import Disbursement, DisbursementApproval
from groups.models import Group, GroupMember
from groups.services.group_service import GroupService
from groups.services.rotation_service import (
    RotationCycleNotFound,
    RotationService,
)
from penalties.services import PenaltyService


class ActivePenalty(DomainException):
    default_message = "O beneficiário possui uma penalização activa e não pode receber um desembolso."


class InvalidDisbursementStatus(DomainException):
    default_message = "O desembolso não se encontra num estado válido para esta operação."


class DisbursementNotFound(DomainException):
    default_message = "Desembolso não encontrado."


class DisbursementAlreadyExists(DomainException):
    default_message = "Já existe um desembolso para esta posição da rotação."


class InactiveBeneficiary(DomainException):
    default_message = "O beneficiário actual não está activo."


class NoConfirmedContributions(DomainException):
    default_message = "Não existem contribuições confirmadas disponíveis para este ciclo."


class IncompleteContributions(DomainException):
    default_message = "Nem todas as contribuições esperadas estão confirmadas."


class ArchivedGroup(DomainException):
    default_message = "Grupos arquivados não podem criar, aprovar ou concluir desembolsos."


class InsufficientEligibleApprovers(DomainException):
    default_message = (
        "Não existem dois membros independentes elegíveis para aprovar o desembolso. "
        "Grupos pequenos necessitam de outra política aprovada, não implementada no protótipo."
    )


class IneligibleApprover(DomainException):
    default_message = "Este utilizador não é um aprovador independente elegível."


class DuplicateDisbursementApproval(DomainException):
    default_message = "Este membro já aprovou este desembolso."


class InsufficientDisbursementApprovals(DomainException):
    default_message = "Quórum de aprovações independentes insuficiente ou inválido."


class DisbursementService:
    @staticmethod
    def _ensure_beneficiary_can_receive(*, member) -> None:
        if member.status != GroupMember.Status.ACTIVE:
            raise InactiveBeneficiary()
        if PenaltyService.has_active_penalty(member=member):
            raise ActivePenalty()

    @staticmethod
    def _valid_approval_count(disbursement: Disbursement) -> int:
        """Count only still-active voters from the proposal's frozen allowlist."""
        if not disbursement.proposed_by_id or not disbursement.eligible_approver_ids:
            return 0  # Fail closed for old records lacking a verified proposal.

        active_user_ids = {
            str(value)
            for value in GroupMember.objects.filter(
                group_id=disbursement.group_id,
                status=GroupMember.Status.ACTIVE,
                user_id__in=disbursement.eligible_approver_ids,
            ).values_list("user_id", flat=True)
        }
        eligible = set(disbursement.eligible_approver_ids)
        valid = active_user_ids & eligible
        valid.discard(str(disbursement.proposed_by_id))
        valid.discard(str(disbursement.beneficiary.user_id))

        return DisbursementApproval.objects.filter(
            disbursement=disbursement,
            approved_by_id__in=valid,
        ).count()

    @staticmethod
    @transaction.atomic
    def create(*, group_id, cycle_number: int, created_by) -> Disbursement:
        # Authorize at the service boundary, not only in the API view.
        GroupService.ensure_manager(group_id=group_id, user=created_by)

        group = Group.objects.select_for_update().filter(id=group_id).first()
        if group is None:
            raise RotationCycleNotFound()
        if group.status == Group.Status.ARCHIVED:
            raise ArchivedGroup()

        current_rotation = RotationService.get_current(
            group=group, cycle_number=cycle_number
        )
        beneficiary = current_rotation.member
        DisbursementService._ensure_beneficiary_can_receive(member=beneficiary)

        if Disbursement.objects.filter(rotation_order=current_rotation).exists():
            raise DisbursementAlreadyExists()

        settings = current_rotation.group_settings
        active_members_count = GroupMember.objects.filter(
            group=group, status=GroupMember.Status.ACTIVE
        ).count()
        contributions = Contribution.objects.filter(
            member__group=group,
            status=Contribution.Status.CONFIRMED,
            group_settings=settings,
            contribution_period=current_rotation.contribution_period,
        )
        confirmed_count = contributions.count()
        if confirmed_count == 0:
            raise NoConfirmedContributions()
        if confirmed_count < active_members_count:
            raise IncompleteContributions()

        eligible_user_ids = [
            str(uid)
            for uid in GroupMember.objects.filter(
                group=group,
                status=GroupMember.Status.ACTIVE,
            ).exclude(
                user_id=created_by.id
            ).exclude(
                id=beneficiary.id
            ).order_by("id").values_list("user_id", flat=True)
        ]
        if len(eligible_user_ids) < 2:
            raise InsufficientEligibleApprovers()

        # Strict majority of non-proposer, non-beneficiary active members.
        quorum = max(2, len(eligible_user_ids) // 2 + 1)
        total = contributions.aggregate(total=Sum("amount")).get("total")
        if total is None:
            total = Decimal("0.00")

        # Deliberately ignore legacy requires_consensus=False; no bypass.
        return Disbursement.objects.create(
            group=group,
            beneficiary=beneficiary,
            rotation_order=current_rotation,
            group_settings=settings,
            cycle_number=cycle_number,
            amount=total,
            currency=settings.currency,
            status=Disbursement.Status.AWAITING_CONSENSUS,
            proposed_by=created_by,
            required_approvals=quorum,
            eligible_approver_ids=eligible_user_ids,
        )

    @staticmethod
    @transaction.atomic
    def approve(*, disbursement_id, approved_by) -> Disbursement:
        disbursement = (
            Disbursement.objects
            .select_for_update()
            .select_related("group", "beneficiary", "beneficiary__user")
            .filter(id=disbursement_id)
            .first()
        )
        if disbursement is None:
            raise DisbursementNotFound()
        if disbursement.group.status == Group.Status.ARCHIVED:
            raise ArchivedGroup()
        if disbursement.status != Disbursement.Status.AWAITING_CONSENSUS:
            raise InvalidDisbursementStatus()
        DisbursementService._ensure_beneficiary_can_receive(
            member=disbursement.beneficiary
        )

        user_id = str(approved_by.id)
        active = GroupMember.objects.filter(
            group_id=disbursement.group_id,
            user=approved_by,
            status=GroupMember.Status.ACTIVE,
        ).exists()
        if (
            not active
            or user_id not in disbursement.eligible_approver_ids
            or user_id == str(disbursement.proposed_by_id)
            or user_id == str(disbursement.beneficiary.user_id)
        ):
            raise IneligibleApprover()
        if DisbursementApproval.objects.filter(
            disbursement=disbursement, approved_by=approved_by
        ).exists():
            raise DuplicateDisbursementApproval()

        DisbursementApproval.objects.create(
            disbursement=disbursement,
            approved_by=approved_by,
        )
        if (
            DisbursementService._valid_approval_count(disbursement)
            >= disbursement.required_approvals
        ):
            disbursement.status = Disbursement.Status.APPROVED
            disbursement.save(update_fields=["status", "updated_at"])
        return disbursement

    @staticmethod
    @transaction.atomic
    def complete(*, disbursement_id, completed_by) -> Disbursement:
        disbursement = (
            Disbursement.objects
            .select_for_update()
            .select_related("group", "rotation_order", "beneficiary")
            .filter(id=disbursement_id)
            .first()
        )
        if disbursement is None:
            raise DisbursementNotFound()
        GroupService.ensure_manager(
            group_id=disbursement.group_id, user=completed_by
        )
        if disbursement.group.status == Group.Status.ARCHIVED:
            raise ArchivedGroup()
        if disbursement.status != Disbursement.Status.APPROVED:
            raise InvalidDisbursementStatus()
        DisbursementService._ensure_beneficiary_can_receive(
            member=disbursement.beneficiary
        )
        if (
            disbursement.required_approvals < 2
            or DisbursementService._valid_approval_count(disbursement)
            < disbursement.required_approvals
        ):
            raise InsufficientDisbursementApprovals()

        # Administrative record only: does not transfer or settle external funds.
        disbursement.status = Disbursement.Status.COMPLETED
        disbursement.completed_at = timezone.now()
        disbursement.save(
            update_fields=["status", "completed_at", "updated_at"]
        )
        RotationService.advance(
            group=disbursement.group,
            cycle_number=disbursement.cycle_number,
        )
        return disbursement

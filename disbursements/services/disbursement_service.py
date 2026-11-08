from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from contributions.models import Contribution, ContributionAnchorIntent
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
    def _verified_contribution_total(
        *,
        group,
        settings,
        period,
        frozen_contributor_user_ids=None,
        proposed_total=None,
    ) -> Decimal:
        """Fail closed if the confirmed ledger and active participant set diverge.

        This is an interim control, NOT a policy deciding how a departed
        participant's money should be distributed. It intentionally blocks
        ambiguous ledgers rather than silently excluding or paying that money.
        Cycle-start membership snapshots require a separate domain decision.
        """
        active_members = list(
            GroupMember.objects.select_for_update().filter(
                group=group,
                status=GroupMember.Status.ACTIVE,
            ).values_list("id", "user_id")
        )
        active_membership_ids = {str(member_id) for member_id, _ in active_members}
        active_user_ids = {str(user_id) for _, user_id in active_members}

        # The proposal's voter snapshot plus proposer + beneficiary is the
        # frozen ACTIVE set at proposal time. A group membership change during
        # voting must be reconciled, not silently alter financial expectations.
        if (
            frozen_contributor_user_ids is not None
            and active_user_ids != set(frozen_contributor_user_ids)
        ):
            raise IncompleteContributions()

        records = list(
            Contribution.objects.select_for_update().filter(
                member__group=group,
                group_settings=settings,
                contribution_period=period,
            ).values_list("member_id", "status", "amount", "currency")
        )
        confirmed = [
            (str(member_id), amount, currency)
            for member_id, status, amount, currency in records
            if status == Contribution.Status.CONFIRMED
        ]
        if not confirmed:
            raise NoConfirmedContributions()

        confirmed_membership_ids = {member_id for member_id, _, _ in confirmed}
        if (
            confirmed_membership_ids != active_membership_ids
            or len(confirmed) != len(active_membership_ids)
            or any(
                Decimal(amount) != Decimal(settings.contribution_amount)
                or currency != settings.currency
                for _, amount, currency in confirmed
            )
        ):
            raise IncompleteContributions()

        # New contribution submissions have a durable anchoring intent.
        # A "CONFIRMED" manual/simulated ledger row is not acceptable for a
        # new RN06 disbursement until that intent is also reconciled with the
        # recorded on-chain receipt. Historic rows without an intent are not
        # silently assigned invented proof or backfilled during this change.
        pending_anchor = ContributionAnchorIntent.objects.filter(
            contribution__member__group=group,
            contribution__group_settings=settings,
            contribution__contribution_period=period,
        ).exclude(
            status=ContributionAnchorIntent.Status.CONFIRMED
        ).exists()
        if pending_anchor:
            raise IncompleteContributions()

        total = sum((amount for _, amount, _ in confirmed), Decimal("0.00"))
        if proposed_total is not None and total != Decimal(proposed_total):
            raise IncompleteContributions()
        return total

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

        total = DisbursementService._verified_contribution_total(
            group=group,
            settings=settings,
            period=current_rotation.contribution_period,
        )

        # Strict majority of non-proposer, non-beneficiary active members.
        quorum = max(2, len(eligible_user_ids) // 2 + 1)
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

        # A vote authorizes a specific financial snapshot, not any later
        # ledger state. Revalidate member identities, period, amount, currency,
        # and total before the administrative rotation advances.
        if not disbursement.proposed_by_id or not disbursement.eligible_approver_ids:
            raise IncompleteContributions()
        frozen_contributors = set(disbursement.eligible_approver_ids)
        frozen_contributors.add(str(disbursement.proposed_by_id))
        frozen_contributors.add(str(disbursement.beneficiary.user_id))
        DisbursementService._verified_contribution_total(
            group=disbursement.group,
            settings=disbursement.group_settings,
            period=disbursement.rotation_order.contribution_period,
            frozen_contributor_user_ids=frozen_contributors,
            proposed_total=disbursement.amount,
        )

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

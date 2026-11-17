"""Non-custodial Xitique payment recording; no wallet API and no fund custody.

The custodian makes the transfer outside Mono using their own wallet. Mono
records a claim and a separate beneficiary acknowledgement. It does NOT verify
provider settlement, external balances, or legal ownership of either wallet.
"""
import re

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from core.exceptions import DomainException
from disbursements.models import Disbursement, ExternalPaymentReport, ExternalWalletCustody
from disbursements.services.disbursement_service import (
    DisbursementService, IncompleteContributions, InsufficientDisbursementApprovals,
    InvalidDisbursementStatus,
)
from groups.models import Group, GroupMember
from groups.services.group_service import GroupService
from groups.services.rotation_service import RotationService


class ExternalWalletFlowUnavailable(DomainException):
    default_message = "Fluxo de carteira móvel externa desactivado."


class MissingCustodian(DomainException):
    default_message = "O grupo ainda não designou um responsável pela carteira móvel."


class WrongCustodian(DomainException):
    default_message = "Só o responsável designado pode declarar o pagamento externo."


class ReceiptActorNotEligible(DomainException):
    default_message = "Só o beneficiário pode confirmar ou contestar o recebimento."


class PaymentEvidenceConflict(DomainException):
    default_message = "A referência ou o estado da declaração de pagamento é incompatível."


class ExternalWalletService:
    PROVIDERS = frozenset(("M_PESA", "E_MOLA"))
    PHONE_RE = re.compile(r"^\+?[0-9]{9,15}$")

    @staticmethod
    def require_enabled():
        if not getattr(settings, "NONCUSTODIAL_WALLET_FLOW_ENABLED", False):
            raise ExternalWalletFlowUnavailable()

    @classmethod
    def _check_number(cls, value):
        normalized = str(value or "").strip()
        if not cls.PHONE_RE.fullmatch(normalized):
            raise PaymentEvidenceConflict("O número da carteira móvel é inválido.")
        return normalized

    @classmethod
    @transaction.atomic
    def designate_custodian(cls, *, group_id, designated_by, member_id, provider, wallet_number):
        """Only a manager may designate an active manager/treasurer for the group."""
        cls.require_enabled()
        GroupService.ensure_manager(group_id=group_id, user=designated_by)
        group = Group.objects.select_for_update().get(pk=group_id)
        if group.status != Group.Status.ACTIVE:
            raise PaymentEvidenceConflict("Grupo não activo.")
        provider = str(provider or "").strip().upper()
        if provider not in cls.PROVIDERS:
            raise PaymentEvidenceConflict("Prestador não suportado.")
        normalized = cls._check_number(wallet_number)
        member = GroupMember.objects.filter(pk=member_id, group=group).first()
        if (
            member is None or member.status != GroupMember.Status.ACTIVE
            or member.role not in (GroupMember.Role.MANAGER, GroupMember.Role.TREASURER)
        ):
            raise WrongCustodian("O responsável deve ser gestor ou tesoureiro activo do grupo.")
        # Avoid retroactively changing the payer while any approved or reported
        # transfer is unresolved. Existing proposals freeze their own payer.
        pending = Disbursement.objects.filter(
            group=group,
            status__in=[
                Disbursement.Status.AWAITING_CONSENSUS,
                Disbursement.Status.APPROVED,
                Disbursement.Status.PAYMENT_REPORTED,
                Disbursement.Status.DISPUTED,
                Disbursement.Status.PROCESSING,
            ],
        ).exists()
        existing = ExternalWalletCustody.objects.select_for_update().filter(group=group).first()
        if pending and existing is not None and (
            existing.custodian_id != member.pk
            or existing.provider != provider
            or existing.wallet_number != normalized
        ):
            raise PaymentEvidenceConflict(
                "Não altere o responsável enquanto existirem desembolsos em curso."
            )
        if pending and existing is None:
            raise PaymentEvidenceConflict("Há propostas existentes sem um responsável congelado.")
        if existing is None:
            return ExternalWalletCustody.objects.create(
                group=group, custodian=member, provider=provider,
                wallet_number=normalized, designated_by=designated_by,
            )
        if (
            existing.custodian_id == member.pk
            and existing.provider == provider
            and existing.wallet_number == normalized
        ):
            return existing
        existing.custodian = member
        existing.provider = provider
        existing.wallet_number = normalized
        existing.designated_by = designated_by
        existing.save(update_fields=[
            "custodian", "provider", "wallet_number", "designated_by", "updated_at"
        ])
        return existing

    @classmethod
    @transaction.atomic
    def report_payment(cls, *, disbursement_id, reported_by, reference, recipient_wallet_number):
        """Record a *claim* about a manually executed mobile-wallet transfer."""
        cls.require_enabled()
        group_id = Disbursement.objects.values_list("group_id", flat=True).get(pk=disbursement_id)
        Group.objects.select_for_update().get(pk=group_id)
        disbursement = Disbursement.objects.select_for_update().select_related(
            "group", "beneficiary", "beneficiary__user", "rotation_order", "group_settings",
            "custodian_at_proposal", "custodian_at_proposal__user",
        ).get(pk=disbursement_id)
        if disbursement.group.status != Group.Status.ACTIVE:
            raise PaymentEvidenceConflict("Grupo não activo.")
        number = cls._check_number(recipient_wallet_number)
        reference = str(reference or "").strip()
        if len(reference) < 4 or len(reference) > 120:
            raise PaymentEvidenceConflict("Indique a referência da transacção externa.")
        if not disbursement.custodian_at_proposal_id:
            raise MissingCustodian()
        custodian = disbursement.custodian_at_proposal
        if (
            custodian.group_id != disbursement.group_id
            or custodian.status != GroupMember.Status.ACTIVE
            or custodian.user_id != reported_by.id
            or custodian.role not in (GroupMember.Role.MANAGER, GroupMember.Role.TREASURER)
        ):
            raise WrongCustodian()
        if reported_by.id == disbursement.beneficiary.user_id:
            raise PaymentEvidenceConflict("O beneficiário não pode declarar o próprio recebimento.")
        existing = ExternalPaymentReport.objects.select_for_update().filter(
            disbursement=disbursement
        ).first()
        if existing:
            if (
                existing.reported_by_id != reported_by.id
                or existing.reference != reference
                or existing.recipient_wallet_number != number
                or existing.provider != disbursement.custody_provider_at_proposal
                or existing.amount != disbursement.amount
                or existing.currency != disbursement.currency
            ):
                raise PaymentEvidenceConflict()
            return existing

        if disbursement.status != Disbursement.Status.APPROVED:
            raise InvalidDisbursementStatus()
        if (
            disbursement.required_approvals < 2
            or DisbursementService._valid_approval_count(disbursement) <
            disbursement.required_approvals
        ):
            raise InsufficientDisbursementApprovals()
        if not disbursement.proposed_by_id or not disbursement.eligible_approver_ids:
            raise IncompleteContributions()
        frozen = set(disbursement.eligible_approver_ids)
        frozen.add(str(disbursement.proposed_by_id))
        frozen.add(str(disbursement.beneficiary.user_id))
        DisbursementService._verified_contribution_total(
            group=disbursement.group,
            settings=disbursement.group_settings,
            period=disbursement.rotation_order.contribution_period,
            frozen_contributor_user_ids=frozen,
            proposed_total=disbursement.amount,
        )
        report = ExternalPaymentReport.objects.create(
            disbursement=disbursement,
            provider=disbursement.custody_provider_at_proposal,
            reference=reference,
            recipient_wallet_number=number,
            reported_by=reported_by,
            amount=disbursement.amount,
            currency=disbursement.currency,
        )
        disbursement.status = Disbursement.Status.PAYMENT_REPORTED
        disbursement.save(update_fields=["status", "updated_at"])
        return report

    @classmethod
    @transaction.atomic
    def confirm_receipt(cls, *, disbursement_id, confirmed_by):
        """Beneficiary acknowledges receipt; this is not independent PSP verification."""
        cls.require_enabled()
        group_id = Disbursement.objects.values_list("group_id", flat=True).get(pk=disbursement_id)
        group = Group.objects.select_for_update().get(pk=group_id)
        disbursement = Disbursement.objects.select_for_update().select_related(
            "beneficiary", "group",
        ).get(pk=disbursement_id)
        if disbursement.beneficiary.user_id != confirmed_by.id:
            raise ReceiptActorNotEligible()
        if not GroupMember.objects.filter(
            pk=disbursement.beneficiary_id, status=GroupMember.Status.ACTIVE
        ).exists():
            raise ReceiptActorNotEligible("O beneficiário deixou de ser membro activo.")
        report = ExternalPaymentReport.objects.select_for_update().filter(
            disbursement=disbursement
        ).first()
        if report is None:
            raise InvalidDisbursementStatus("O responsável ainda não declarou a transferência.")
        if disbursement.status == Disbursement.Status.COMPLETED:
            if report.status == ExternalPaymentReport.Status.CONFIRMED and report.confirmed_by_id == confirmed_by.id:
                return disbursement
            raise PaymentEvidenceConflict()
        if (
            disbursement.status != Disbursement.Status.PAYMENT_REPORTED
            or report.status != ExternalPaymentReport.Status.REPORTED
        ):
            raise InvalidDisbursementStatus()
        if report.reported_by_id == confirmed_by.id:
            raise ReceiptActorNotEligible("A declaração e a confirmação não podem ser feitas pela mesma conta.")
        report.status = ExternalPaymentReport.Status.CONFIRMED
        report.confirmed_by = confirmed_by
        report.confirmed_at = timezone.now()
        report.save(update_fields=["status", "confirmed_by", "confirmed_at"])
        disbursement.status = Disbursement.Status.COMPLETED
        disbursement.completed_at = timezone.now()
        disbursement.save(update_fields=["status", "completed_at", "updated_at"])
        RotationService.advance(group=group, cycle_number=disbursement.cycle_number)
        return disbursement

    @classmethod
    @transaction.atomic
    def dispute_receipt(cls, *, disbursement_id, disputed_by, reason):
        """Fail closed: an unverified conflict stops rotation."""
        cls.require_enabled()
        group_id = Disbursement.objects.values_list("group_id", flat=True).get(pk=disbursement_id)
        Group.objects.select_for_update().get(pk=group_id)
        disbursement = Disbursement.objects.select_for_update().select_related(
            "beneficiary",
        ).get(pk=disbursement_id)
        if disbursement.beneficiary.user_id != disputed_by.id:
            raise ReceiptActorNotEligible()
        reason = str(reason or "").strip()
        if len(reason) < 8 or len(reason) > 1000:
            raise PaymentEvidenceConflict("Descreva a divergência do recebimento.")
        report = ExternalPaymentReport.objects.select_for_update().filter(disbursement=disbursement).first()
        if (
            disbursement.status != Disbursement.Status.PAYMENT_REPORTED
            or report is None or report.status != ExternalPaymentReport.Status.REPORTED
        ):
            raise InvalidDisbursementStatus()
        report.status = ExternalPaymentReport.Status.DISPUTED
        report.disputed_at = timezone.now()
        report.dispute_reason = reason
        report.save(update_fields=["status", "disputed_at", "dispute_reason"])
        disbursement.status = Disbursement.Status.DISPUTED
        disbursement.save(update_fields=["status", "updated_at"])
        return report

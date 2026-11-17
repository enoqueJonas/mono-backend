"""Non-custodial Xitique disbursement: approval and claims, not payment execution.

The platform NEVER initiates or debits an external mobile-money wallet.
An authenticated custodian reports an independently executed transfer; the
beneficiary acknowledges or disputes the claim. Blockchain stores hashes of
those authenticated APP statements, not proof of external financial settlement.
"""
from hashlib import sha256
import json

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from blockchain.clients.disbursement_registry_client import DisbursementRegistryClient
from contributions.services.anchor_outbox_service import ContributionAnchorOutboxService
from core.exceptions import DomainException
from disbursements.models import (
    Disbursement, ExternalPaymentReport, TreasuryMandate,
)
from disbursements.services.disbursement_service import (
    DisbursementService, IncompleteContributions,
    InsufficientDisbursementApprovals, InvalidDisbursementStatus,
)
from groups.models import Group, GroupMember
from groups.services.group_service import GroupService
from groups.services.rotation_service import RotationService


class NonCustodialDisabled(DomainException):
    default_message = "O modo não custodial não está activado."


class InvalidCustodian(DomainException):
    default_message = "Apenas o responsável designado pela carteira externa pode declarar pagamentos."


class ExternalEvidenceMismatch(DomainException):
    default_message = "Evidência blockchain divergente do registo de pagamento."


class RepeatedPaymentReport(DomainException):
    default_message = "Este pagamento já foi declarado ou usa uma referência anterior."


class UnauthorizedReceiptResponse(DomainException):
    default_message = "Apenas o beneficiário pode confirmar ou contestar este recebimento."


class CustodianAlreadyAssigned(DomainException):
    default_message = "O responsável externo já foi designado; a substituição exige procedimento próprio."


class NonCustodialDisbursementService:
    @staticmethod
    def require_mode():
        if not getattr(settings, "NON_CUSTODIAL_DISBURSEMENTS_ENABLED", False):
            raise NonCustodialDisabled()

    @staticmethod
    def _digest(payload):
        return sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            .encode("utf-8")
        ).hexdigest()

    @classmethod
    def authorization_hash(cls, d):
        """Replicates the frozen RN06 authorization format already in sandbox."""
        return cls._digest({
            "schema": "mono-sandbox-authorization-v1",
            "disbursement_id": str(d.pk),
            "group_id": str(d.group_id),
            "beneficiary_id": str(d.beneficiary_id),
            "cycle_number": d.cycle_number,
            "amount": str(d.amount),
            "currency": d.currency,
            "proposed_by_id": str(d.proposed_by_id),
            "required_approvals": d.required_approvals,
            "approved_by_ids": sorted(
                str(user_id) for user_id in d.approvals.values_list(
                    "approved_by_id", flat=True
                )
            ),
        })

    @classmethod
    def acknowledgment_hash(cls, payment):
        """Hash of beneficiary's declaration; not an independently verified receipt."""
        if payment.status != ExternalPaymentReport.Status.CONFIRMED:
            raise InvalidDisbursementStatus("Só confirmações positivas podem ser ancoradas.")
        return cls._digest({
            "schema": "mono-external-beneficiary-acknowledgment-v1",
            "proof_kind": "SELF_REPORTED_EXTERNAL_PAYMENT",
            "report_id": payment.pk,
            "disbursement_id": str(payment.disbursement_id),
            "provider": payment.provider,
            "wallet_alias": payment.wallet_alias,
            "transaction_reference": payment.transfer_reference,
            "reported_by_id": str(payment.reported_by_id),
            "amount": str(payment.amount),
            "currency": payment.currency,
            "beneficiary_user_id": str(payment.beneficiary_user_id),
            "confirmed_by_id": str(payment.confirmed_by_id),
            "responded_at": payment.responded_at.isoformat(),
        })

    @staticmethod
    def _compare(actual, expected):
        if actual.lower().removeprefix("0x") != expected:
            raise ExternalEvidenceMismatch()

    @classmethod
    def _validate_rn06(cls, d):
        if d.status != Disbursement.Status.APPROVED:
            raise InvalidDisbursementStatus()
        if (
            not d.proposed_by_id
            or not d.eligible_approver_ids
            or d.required_approvals < 2
            or DisbursementService._valid_approval_count(d) < d.required_approvals
        ):
            raise InsufficientDisbursementApprovals()

        DisbursementService._ensure_beneficiary_can_receive(
            member=d.beneficiary,
        )
        contributors = set(d.eligible_approver_ids)
        contributors.add(str(d.proposed_by_id))
        contributors.add(str(d.beneficiary.user_id))
        DisbursementService._verified_contribution_total(
            group=d.group,
            settings=d.group_settings,
            period=d.rotation_order.contribution_period,
            frozen_contributor_user_ids=contributors,
            proposed_total=d.amount,
        )

    @classmethod
    @transaction.atomic
    def appoint_custodian(cls, *, group_id, appointed_by, group_member_id, provider, wallet_alias):
        cls.require_mode()
        group = Group.objects.select_for_update().get(pk=group_id)
        GroupService.ensure_manager(group_id=group.pk, user=appointed_by)
        if group.status != Group.Status.ACTIVE:
            raise InvalidDisbursementStatus("Grupo inactivo.")
        member = GroupMember.objects.filter(
            pk=group_member_id, group=group, status=GroupMember.Status.ACTIVE
        ).first()
        if member is None:
            raise InvalidCustodian("O responsável tem de ser membro activo do grupo.")
        if TreasuryMandate.objects.filter(group=group).exists():
            raise CustodianAlreadyAssigned()
        return TreasuryMandate.objects.create(
            group=group,
            custodian=member,
            provider=provider,
            wallet_alias=wallet_alias,
            appointed_by=appointed_by,
        )

    @classmethod
    def open_for_external_payment(cls, *, disbursement_id, requested_by, client=None):
        """Anchor approval first, then tell custodian to pay OUTSIDE Mono."""
        cls.require_mode()
        d = Disbursement.objects.select_related("group").get(pk=disbursement_id)
        GroupService.ensure_manager(group_id=d.group_id, user=requested_by)
        with transaction.atomic():
            group = Group.objects.select_for_update().get(pk=d.group_id)
            d = Disbursement.objects.select_for_update().select_related(
                "group", "rotation_order", "group_settings", "beneficiary",
                "beneficiary__user",
            ).get(pk=disbursement_id)
            mandate = TreasuryMandate.objects.select_related("custodian").filter(
                group=group,
                custodian__status=GroupMember.Status.ACTIVE,
            ).first()
            if mandate is None:
                raise InvalidCustodian("É necessário designar primeiro o responsável pela carteira.")
            if group.status != Group.Status.ACTIVE:
                raise InvalidDisbursementStatus("Grupo inactivo.")
            if d.status == Disbursement.Status.APPROVED:
                cls._validate_rn06(d)
            elif d.status != Disbursement.Status.AWAITING_PAYMENT:
                raise InvalidDisbursementStatus()
            expected_hash = cls.authorization_hash(d)

        client = client or DisbursementRegistryClient()
        with ContributionAnchorOutboxService._operator_lock() as acquired:
            if not acquired:
                raise ExternalEvidenceMismatch("Operador blockchain ocupado; reconcilie depois.")
            proof = client.get(str(d.pk))
            if not proof["authorized"]:
                client.anchor_authorization(
                    disbursement_id=str(d.pk), authorization_hash=expected_hash,
                )
                proof = client.get(str(d.pk))
            if not proof["authorized"]:
                raise ExternalEvidenceMismatch("Autorização não confirmada na blockchain.")
            cls._compare(proof["authorization_hash"], expected_hash)

        with transaction.atomic():
            Group.objects.select_for_update().get(pk=d.group_id)
            updated = Disbursement.objects.select_for_update().get(pk=d.pk)
            if updated.status == Disbursement.Status.APPROVED:
                # A membership change after blockchain submission blocks progression.
                current = Disbursement.objects.select_related(
                    "group", "rotation_order", "group_settings",
                    "beneficiary", "beneficiary__user",
                ).get(pk=d.pk)
                cls._validate_rn06(current)
                updated.status = Disbursement.Status.AWAITING_PAYMENT
                updated.save(update_fields=["status", "updated_at"])
            elif updated.status != Disbursement.Status.AWAITING_PAYMENT:
                raise InvalidDisbursementStatus()
            return updated

    @classmethod
    @transaction.atomic
    def report_external_payment(cls, *, disbursement_id, reported_by, reference):
        """A declaration, never a wallet API call or an automatic funds transfer."""
        cls.require_mode()
        group_id = Disbursement.objects.values_list(
            "group_id", flat=True
        ).get(pk=disbursement_id)
        group = Group.objects.select_for_update().get(pk=group_id)
        d = Disbursement.objects.select_for_update().select_related(
            "beneficiary__user"
        ).get(pk=disbursement_id)
        mandate = TreasuryMandate.objects.select_related("custodian").filter(
            group=group,
        ).first()
        if (
            mandate is None
            or mandate.custodian.status != GroupMember.Status.ACTIVE
            or mandate.custodian.user_id != reported_by.pk
        ):
            raise InvalidCustodian()
        if group.status != Group.Status.ACTIVE:
            raise InvalidDisbursementStatus("Grupo inactivo.")
        existing = ExternalPaymentReport.objects.filter(disbursement=d).first()
        if existing:
            if existing.transfer_reference != reference or existing.reported_by_id != reported_by.pk:
                raise RepeatedPaymentReport()
            return d
        if d.status != Disbursement.Status.AWAITING_PAYMENT:
            raise InvalidDisbursementStatus()
        if ExternalPaymentReport.objects.filter(
            provider=mandate.provider, transfer_reference=reference
        ).exists():
            raise RepeatedPaymentReport()
        ExternalPaymentReport.objects.create(
            disbursement=d,
            mandate=mandate,
            reported_by=reported_by,
            provider=mandate.provider,
            wallet_alias=mandate.wallet_alias,
            transfer_reference=reference,
            amount=d.amount,
            currency=d.currency,
            beneficiary_user=d.beneficiary.user,
        )
        d.status = Disbursement.Status.AWAITING_CONFIRMATION
        d.save(update_fields=["status", "updated_at"])
        return d

    @classmethod
    @transaction.atomic
    def respond_to_report(cls, *, disbursement_id, responded_by, received, dispute_reason=""):
        cls.require_mode()
        group_id = Disbursement.objects.values_list(
            "group_id", flat=True
        ).get(pk=disbursement_id)
        Group.objects.select_for_update().get(pk=group_id)
        d = Disbursement.objects.select_for_update().select_related(
            "beneficiary__user"
        ).get(pk=disbursement_id)
        if d.beneficiary.user_id != responded_by.pk or d.beneficiary.status != GroupMember.Status.ACTIVE:
            raise UnauthorizedReceiptResponse()
        if d.status != Disbursement.Status.AWAITING_CONFIRMATION:
            raise InvalidDisbursementStatus("O pagamento não está a aguardar confirmação.")
        report = ExternalPaymentReport.objects.select_for_update().get(
            disbursement=d,
        )
        if report.status != ExternalPaymentReport.Status.REPORTED:
            raise InvalidDisbursementStatus()
        report.responded_at = timezone.now()
        report.confirmed_by = responded_by
        if received:
            report.status = ExternalPaymentReport.Status.CONFIRMED
            d.status = Disbursement.Status.EVIDENCE_PENDING
        else:
            if not dispute_reason.strip():
                raise InvalidDisbursementStatus("Uma contestação exige uma justificação.")
            report.status = ExternalPaymentReport.Status.DISPUTED
            report.dispute_reason = dispute_reason.strip()
            d.status = Disbursement.Status.DISPUTED
        report.save(update_fields=[
            "status", "responded_at", "confirmed_by", "dispute_reason",
        ])
        d.save(update_fields=["status", "updated_at"])
        return d

    @classmethod
    def finalize_acknowledged_payment(cls, *, disbursement_id, requested_by, client=None):
        """Proof of beneficiary acknowledgment, never proof of actual PSP settlement."""
        cls.require_mode()
        d = Disbursement.objects.select_related("group").get(pk=disbursement_id)
        GroupService.ensure_manager(group_id=d.group_id, user=requested_by)
        with transaction.atomic():
            group = Group.objects.select_for_update().get(pk=d.group_id)
            d = Disbursement.objects.select_for_update().get(pk=disbursement_id)
            if d.status not in (
                Disbursement.Status.EVIDENCE_PENDING,
                Disbursement.Status.COMPLETED,
            ):
                raise InvalidDisbursementStatus()
            payment = ExternalPaymentReport.objects.select_related("mandate").get(
                disbursement=d,
                status=ExternalPaymentReport.Status.CONFIRMED,
                confirmed_by_id=d.beneficiary.user_id,
            )
            expected_hash = cls.acknowledgment_hash(payment)

        client = client or DisbursementRegistryClient()
        with ContributionAnchorOutboxService._operator_lock() as acquired:
            if not acquired:
                raise ExternalEvidenceMismatch("Operador blockchain ocupado; reconcilie depois.")
            proof = client.get(str(d.pk))
            if not proof["authorized"]:
                raise ExternalEvidenceMismatch("Falta a prova de autorização.")
            cls._compare(proof["authorization_hash"], cls.authorization_hash(d))
            acknowledgment = client.get_beneficiary_acknowledgment(str(d.pk))
            if not acknowledgment["exists"]:
                client.anchor_beneficiary_acknowledgment(
                    disbursement_id=str(d.pk), evidence_hash=expected_hash,
                )
                acknowledgment = client.get_beneficiary_acknowledgment(str(d.pk))
            if not acknowledgment["exists"]:
                raise ExternalEvidenceMismatch("Falta a prova de confirmação.")
            cls._compare(acknowledgment["evidence_hash"], expected_hash)

        with transaction.atomic():
            group = Group.objects.select_for_update().get(pk=d.group_id)
            updated = Disbursement.objects.select_for_update().get(pk=d.pk)
            if updated.status == Disbursement.Status.COMPLETED:
                return updated
            if updated.status != Disbursement.Status.EVIDENCE_PENDING:
                raise InvalidDisbursementStatus()
            report = ExternalPaymentReport.objects.select_for_update().get(
                disbursement=updated,
                status=ExternalPaymentReport.Status.CONFIRMED,
                confirmed_by_id=updated.beneficiary.user_id,
            )
            cls._compare(cls.acknowledgment_hash(report), expected_hash)
            updated.status = Disbursement.Status.COMPLETED
            updated.completed_at = timezone.now()
            updated.save(update_fields=["status", "completed_at", "updated_at"])
            RotationService.advance(
                group=group, cycle_number=updated.cycle_number,
            )
            return updated

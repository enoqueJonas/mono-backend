"""Experimental RN06 → blockchain authorization → virtual PSP → settlement anchor.

No external bank is contacted. The sandbox credit/debit is real only within the
isolated SQL test ledger; it is not evidence of a financial transfer in MZN.
RPC calls occur outside DB transactions. Retries reconcile before resubmitting.
"""
import hashlib
import json

from django.db import transaction

from blockchain.clients.disbursement_registry_client import DisbursementRegistryClient
from contributions.services.anchor_outbox_service import ContributionAnchorOutboxService
from core.exceptions import DomainException
from disbursements.models import Disbursement
from disbursements.services.disbursement_service import (
    DisbursementService,
    IncompleteContributions,
    InsufficientDisbursementApprovals,
    InvalidDisbursementStatus,
)
from groups.models import Group, GroupMember
from groups.services.group_service import GroupService
from groups.services.rotation_service import RotationService
from wallets.models import SandboxTransfer
from wallets.services.sandbox_ledger import SandboxLedgerService


class SandboxProofMismatch(DomainException):
    default_message = "A prova ancorada diverge do registo do desembolso."


class SandboxSignerBusy(DomainException):
    default_message = "Operador blockchain ocupado; tente reconciliar novamente."


class SandboxPayoutService:
    @staticmethod
    def _digest(obj):
        return hashlib.sha256(
            json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            .encode("utf-8")
        ).hexdigest()

    @classmethod
    def authorization_hash(cls, disbursement):
        """Freeze amounts, beneficiary and the actual voting accounts."""
        return cls._digest({
            "schema": "mono-sandbox-authorization-v1",
            "disbursement_id": str(disbursement.pk),
            "group_id": str(disbursement.group_id),
            "beneficiary_id": str(disbursement.beneficiary_id),
            "cycle_number": disbursement.cycle_number,
            "amount": str(disbursement.amount),
            "currency": disbursement.currency,
            "proposed_by_id": str(disbursement.proposed_by_id),
            "required_approvals": disbursement.required_approvals,
            "approved_by_ids": sorted(
                str(uid) for uid in disbursement.approvals.values_list(
                    "approved_by_id", flat=True
                )
            ),
        })

    @classmethod
    def settlement_hash(cls, transfer):
        """Hash the actual recorded *fictional* debit and credit, not a request."""
        return cls._digest({
            "schema": "mono-sandbox-settlement-v1",
            "transfer_id": str(transfer.pk),
            "idempotency_key": transfer.idempotency_key,
            "source_account": transfer.source.key,
            "destination_account": transfer.destination.key,
            "amount": str(transfer.amount),
            "currency": transfer.currency,
            "reference": transfer.reference,
            "is_real_payment": False,
        })

    @staticmethod
    def _assert_hash(actual, expected):
        if actual.lower().removeprefix("0x") != expected:
            raise SandboxProofMismatch()

    @classmethod
    def _check_snapshot(cls, disbursement):
        """Revalidate the same financial and quorum conditions used by RN06."""
        if disbursement.status not in (
            Disbursement.Status.APPROVED,
            Disbursement.Status.PROCESSING,
        ):
            raise InvalidDisbursementStatus()
        if (
            disbursement.required_approvals < 2
            or DisbursementService._valid_approval_count(disbursement)
            < disbursement.required_approvals
        ):
            raise InsufficientDisbursementApprovals()
        if not disbursement.proposed_by_id or not disbursement.eligible_approver_ids:
            raise IncompleteContributions()

        if disbursement.status == Disbursement.Status.APPROVED:
            DisbursementService._ensure_beneficiary_can_receive(
                member=disbursement.beneficiary
            )
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

    @classmethod
    @transaction.atomic
    def _debit_once(cls, disbursement_id):
        """Group lock serializes payouts and contribution-webhook credits."""
        group_id = Disbursement.objects.values_list(
            "group_id", flat=True
        ).get(pk=disbursement_id)
        Group.objects.select_for_update().get(pk=group_id)
        disbursement = Disbursement.objects.select_for_update().select_related(
            "group", "beneficiary", "beneficiary__user", "rotation_order",
            "group_settings",
        ).get(pk=disbursement_id)
        existing = SandboxTransfer.objects.filter(
            idempotency_key=f"DISBURSEMENT:{disbursement.pk}"
        ).first()
        if existing is not None:
            if disbursement.status not in (
                Disbursement.Status.PROCESSING,
                Disbursement.Status.COMPLETED,
            ):
                raise SandboxProofMismatch(
                    "Existing test payout conflicts with disbursement status."
                )
            if (
                existing.amount != disbursement.amount
                or existing.currency != disbursement.currency
                or existing.destination.key != SandboxLedgerService.member_key(
                    disbursement.beneficiary.user_id, disbursement.currency
                )
            ):
                raise SandboxProofMismatch()
            return existing

        cls._check_snapshot(disbursement)
        if disbursement.status != Disbursement.Status.APPROVED:
            raise InvalidDisbursementStatus()
        transfer = SandboxLedgerService.pay_disbursement(disbursement)
        disbursement.status = Disbursement.Status.PROCESSING
        disbursement.save(update_fields=["status", "updated_at"])
        return transfer

    @classmethod
    @transaction.atomic
    def _finish_once(cls, disbursement_id, settlement_hash):
        group_id = Disbursement.objects.values_list(
            "group_id", flat=True
        ).get(pk=disbursement_id)
        group = Group.objects.select_for_update().get(pk=group_id)
        disbursement = Disbursement.objects.select_for_update().select_related(
            "group", "rotation_order", "beneficiary"
        ).get(pk=disbursement_id)
        transfer = SandboxTransfer.objects.select_related(
            "source", "destination"
        ).get(idempotency_key=f"DISBURSEMENT:{disbursement_id}")
        cls._assert_hash(settlement_hash, cls.settlement_hash(transfer))
        if disbursement.status == Disbursement.Status.COMPLETED:
            return disbursement
        if disbursement.status != Disbursement.Status.PROCESSING:
            raise InvalidDisbursementStatus()
        # This is a virtual settlement; never call a real PSP here.
        from django.utils import timezone
        disbursement.status = Disbursement.Status.COMPLETED
        disbursement.completed_at = timezone.now()
        disbursement.save(update_fields=["status", "completed_at", "updated_at"])
        RotationService.advance(group=group, cycle_number=disbursement.cycle_number)
        return disbursement

    @classmethod
    def execute(cls, *, disbursement_id, completed_by, client=None):
        SandboxLedgerService.require_enabled()
        original = Disbursement.objects.select_related("group").get(pk=disbursement_id)
        GroupService.ensure_manager(group_id=original.group_id, user=completed_by)
        if original.group.status == Group.Status.ARCHIVED:
            raise InvalidDisbursementStatus("Archived groups cannot pay out.")

        client = client or DisbursementRegistryClient()
        auth_hash = cls.authorization_hash(original)
        proof = client.get(str(original.pk))
        if proof["authorized"]:
            cls._assert_hash(proof["authorization_hash"], auth_hash)
        else:
            # Never authorize an invalid, failed, or manually completed proposal.
            with transaction.atomic():
                Group.objects.select_for_update().get(pk=original.group_id)
                current = Disbursement.objects.select_for_update().select_related(
                    "group", "beneficiary", "beneficiary__user",
                    "rotation_order", "group_settings",
                ).get(pk=disbursement_id)
                cls._check_snapshot(current)
                if current.status != Disbursement.Status.APPROVED:
                    raise InvalidDisbursementStatus()

            # Reconcile the chain first after any uncertain submit.
            with ContributionAnchorOutboxService._operator_lock() as acquired:
                if not acquired:
                    raise SandboxSignerBusy()
                proof = client.get(str(original.pk))
                if not proof["authorized"]:
                    client.anchor_authorization(
                        disbursement_id=str(original.pk),
                        authorization_hash=auth_hash,
                    )
                proof = client.get(str(original.pk))
            if not proof["authorized"]:
                raise SandboxProofMismatch("Authorization is not confirmed on-chain.")
            cls._assert_hash(proof["authorization_hash"], auth_hash)

        if original.status == Disbursement.Status.COMPLETED:
            existing = SandboxTransfer.objects.select_related(
                "source", "destination"
            ).get(idempotency_key=f"DISBURSEMENT:{original.pk}")
            if not proof["settled"]:
                raise SandboxProofMismatch("Completed payout lacks settlement proof.")
            cls._assert_hash(proof["settlement_hash"], cls.settlement_hash(existing))
            return original

        transfer = cls._debit_once(original.pk)
        settlement_hash = cls.settlement_hash(transfer)
        if proof["settled"]:
            cls._assert_hash(proof["settlement_hash"], settlement_hash)
        else:
            with ContributionAnchorOutboxService._operator_lock() as acquired:
                if not acquired:
                    raise SandboxSignerBusy()
                proof = client.get(str(original.pk))
                if not proof["settled"]:
                    client.anchor_verified_settlement(
                        disbursement_id=str(original.pk),
                        settlement_hash=settlement_hash,
                    )
                proof = client.get(str(original.pk))
            if not proof["settled"]:
                raise SandboxProofMismatch("Virtual settlement is not confirmed on-chain.")
            cls._assert_hash(proof["settlement_hash"], settlement_hash)

        return cls._finish_once(original.pk, settlement_hash)

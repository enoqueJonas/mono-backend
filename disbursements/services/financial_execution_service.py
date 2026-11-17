"""RN06 -> intent on-chain -> B2C -> verified settlement -> anchor -> rotation.

No client-supplied payment result is trusted. Ambiguous provider responses
are reconciled using the same reference; the send operation is never retried.
"""
import hashlib
import json
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from blockchain.clients.disbursement_registry_client import DisbursementRegistryClient
from core.exceptions import DomainException
from disbursements.models import Disbursement, DisbursementExecution
from disbursements.services.disbursement_service import DisbursementService
from groups.services.group_service import GroupService
from wallets.mpesa_b2c import MpesaGateway


class PayoutNotReady(DomainException):
    default_message = "Desembolso financeiro indisponível ou numa fase inválida."


class PayoutEvidenceMismatch(DomainException):
    default_message = "Prova financeira não corresponde ao desembolso aprovado."


class FinancialExecutionService:
    @staticmethod
    def _enabled():
        if not getattr(settings, "DISBURSEMENT_PAYOUT_REQUIRED", False):
            raise PayoutNotReady("O módulo financeiro está desactivado.")

    @staticmethod
    def _hash(document):
        return hashlib.sha256(
            json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        ).hexdigest()

    @staticmethod
    def _get_locked(execution_id, actor):
        execution = (
            DisbursementExecution.objects.select_for_update()
            .select_related("disbursement", "disbursement__beneficiary")
            .get(pk=execution_id)
        )
        GroupService.ensure_manager(group_id=execution.disbursement.group_id, user=actor)
        return execution

    @staticmethod
    @transaction.atomic
    def prepare(*, disbursement_id, actor):
        FinancialExecutionService._enabled()
        disbursement = (
            Disbursement.objects.select_for_update()
            .select_related("beneficiary__user", "rotation_order", "group_settings")
            .get(pk=disbursement_id)
        )
        GroupService.ensure_manager(group_id=disbursement.group_id, user=actor)
        if disbursement.status != Disbursement.Status.APPROVED:
            raise PayoutNotReady()
        if (
            disbursement.required_approvals < 2
            or DisbursementService._valid_approval_count(disbursement)
            < disbursement.required_approvals
        ):
            raise PayoutNotReady("Quórum RN06 insuficiente.")
        DisbursementService._ensure_beneficiary_can_receive(member=disbursement.beneficiary)
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
        if disbursement.currency != "MZN":
            raise PayoutNotReady("Esta integração aceita apenas MZN.")
        recipient = disbursement.beneficiary.user.phone_number
        if not recipient or not str(recipient).lstrip("+").startswith("25884") and not str(recipient).lstrip("+").startswith("25885"):
            raise PayoutNotReady("Beneficiário não tem telefone M-Pesa válido.")
        execution, _ = DisbursementExecution.objects.get_or_create(
            disbursement=disbursement,
            defaults={
                "recipient_msisdn": str(recipient),
                "amount": disbursement.amount,
                "currency": disbursement.currency,
            },
        )
        if execution.amount != disbursement.amount or execution.recipient_msisdn != str(recipient):
            raise PayoutEvidenceMismatch("Os dados financeiros foram alterados após a proposta.")
        return execution

    @staticmethod
    def _intent_document(execution):
        item = execution.disbursement
        return {
            "v": 1,
            "kind": "disbursement_intent",
            "disbursement_id": str(item.id),
            "group_id": str(item.group_id),
            "beneficiary_id": str(item.beneficiary_id),
            "reference": execution.reference,
            "provider": execution.provider,
            "recipient": execution.recipient_msisdn,
            "amount": str(execution.amount),
            "currency": execution.currency,
            "approved_by": sorted(str(x) for x in item.approvals.values_list("approved_by_id", flat=True)),
        }

    @staticmethod
    def anchor_intent(*, execution_id, actor, registry=None):
        FinancialExecutionService._enabled()
        with transaction.atomic():
            execution = FinancialExecutionService._get_locked(execution_id, actor)
            if execution.status == DisbursementExecution.Status.INTENT_ANCHORED:
                return execution
            if execution.status not in (
                DisbursementExecution.Status.READY,
                DisbursementExecution.Status.INTENT_ANCHORING,
            ):
                raise PayoutNotReady()
            proof = FinancialExecutionService._hash(
                FinancialExecutionService._intent_document(execution)
            )
            if execution.intent_hash and proof != execution.intent_hash:
                raise PayoutEvidenceMismatch()
            execution.intent_hash = proof
            execution.status = DisbursementExecution.Status.INTENT_ANCHORING
            execution.save(update_fields=["intent_hash", "status", "updated_at"])
        # Network operation after SQL commit; get() recovers an already-mined receipt.
        receipt = (registry or DisbursementRegistryClient()).anchor_intent(
            str(execution.disbursement_id), proof
        )
        with transaction.atomic():
            execution = FinancialExecutionService._get_locked(execution_id, actor)
            if execution.intent_hash != proof:
                raise PayoutEvidenceMismatch()
            execution.intent_anchor_tx = receipt.transaction_hash
            execution.status = DisbursementExecution.Status.INTENT_ANCHORED
            execution.save(update_fields=["intent_anchor_tx", "status", "updated_at"])
        return execution

    @staticmethod
    def send(*, execution_id, actor, gateway=None):
        FinancialExecutionService._enabled()
        # Check configuration BEFORE claiming an external send. Missing keys
        # are not a network timeout and must not quarantine a clean payout.
        provider = gateway if gateway is not None else MpesaGateway()
        with transaction.atomic():
            execution = FinancialExecutionService._get_locked(execution_id, actor)
            if execution.status != DisbursementExecution.Status.INTENT_ANCHORED:
                raise PayoutNotReady("A intenção precisa estar ancorada.")
            # Persist the sending intent BEFORE communicating with a provider.
            # If the process crashes or times out, only query the same reference.
            execution.status = DisbursementExecution.Status.SENDING
            execution.initiated_at = timezone.now()
            execution.save(update_fields=["status", "initiated_at", "updated_at"])
        try:
            ack = provider.send(execution)
        except Exception:
            with transaction.atomic():
                execution = FinancialExecutionService._get_locked(execution_id, actor)
                execution.status = DisbursementExecution.Status.UNKNOWN
                execution.failure_reason = "Estado do fornecedor desconhecido. Consultar antes de qualquer decisão."
                execution.save(update_fields=["status", "failure_reason", "updated_at"])
            raise
        with transaction.atomic():
            execution = FinancialExecutionService._get_locked(execution_id, actor)
            execution.status = DisbursementExecution.Status.PENDING
            execution.provider_transaction_id = str(ack.get("transaction_id") or "")
            execution.save(update_fields=["status", "provider_transaction_id", "updated_at"])
        return execution

    @staticmethod
    def query_provider(*, execution_id, actor, gateway=None):
        FinancialExecutionService._enabled()
        with transaction.atomic():
            execution = FinancialExecutionService._get_locked(execution_id, actor)
            if execution.status not in (
                DisbursementExecution.Status.SENDING,
                DisbursementExecution.Status.PENDING,
                DisbursementExecution.Status.UNKNOWN,
                DisbursementExecution.Status.PROVIDER_CONFIRMED,
            ):
                raise PayoutNotReady()
            if execution.status == DisbursementExecution.Status.PROVIDER_CONFIRMED:
                return execution
        result = (gateway or MpesaGateway()).query(execution)
        with transaction.atomic():
            execution = FinancialExecutionService._get_locked(execution_id, actor)
            if execution.status == DisbursementExecution.Status.PROVIDER_CONFIRMED:
                return execution
            status = result.get("status")
            if status == "SUCCESS":
                if (
                    result.get("reference") != execution.reference
                    or result.get("recipient_msisdn") != execution.recipient_msisdn
                    or result.get("currency") != execution.currency
                    or Decimal(str(result.get("amount", "0"))) != execution.amount
                    or not result.get("transaction_id")
                ):
                    raise PayoutEvidenceMismatch()
                execution.provider_transaction_id = str(result["transaction_id"])
                execution.verified_at = timezone.now()
                execution.status = DisbursementExecution.Status.PROVIDER_CONFIRMED
                execution.save(update_fields=[
                    "provider_transaction_id", "verified_at", "status", "updated_at"
                ])
            elif status == "FAILED":
                execution.status = DisbursementExecution.Status.PROVIDER_FAILED
                execution.save(update_fields=["status", "updated_at"])
            elif status == "PENDING":
                execution.status = DisbursementExecution.Status.PENDING
                execution.save(update_fields=["status", "updated_at"])
            else:
                execution.status = DisbursementExecution.Status.UNKNOWN
                execution.save(update_fields=["status", "updated_at"])
        return execution

    @staticmethod
    def anchor_settlement(*, execution_id, actor, registry=None):
        FinancialExecutionService._enabled()
        with transaction.atomic():
            execution = FinancialExecutionService._get_locked(execution_id, actor)
            if execution.status == DisbursementExecution.Status.SETTLEMENT_ANCHORED:
                # Recover post-anchor administrative completion without any
                # second provider call or duplicate on-chain transaction.
                if execution.disbursement.status != Disbursement.Status.COMPLETED:
                    DisbursementService.complete(
                        disbursement_id=execution.disbursement_id,
                        completed_by=actor,
                    )
                return execution
            if execution.status not in (
                DisbursementExecution.Status.PROVIDER_CONFIRMED,
                DisbursementExecution.Status.SETTLEMENT_ANCHORING,
            ):
                raise PayoutNotReady("O fornecedor ainda não confirmou o pagamento.")
            if not execution.intent_anchor_tx or not execution.provider_transaction_id:
                raise PayoutEvidenceMismatch()
            document = {
                "v": 1,
                "kind": "disbursement_settlement",
                "disbursement_id": str(execution.disbursement_id),
                "reference": execution.reference,
                "provider_transaction_id": execution.provider_transaction_id,
                "amount": str(execution.amount),
                "currency": execution.currency,
                "recipient": execution.recipient_msisdn,
                "intent_hash": execution.intent_hash,
            }
            digest = FinancialExecutionService._hash(document)
            if execution.settlement_hash and digest != execution.settlement_hash:
                raise PayoutEvidenceMismatch()
            execution.settlement_hash = digest
            execution.status = DisbursementExecution.Status.SETTLEMENT_ANCHORING
            execution.save(update_fields=["settlement_hash", "status", "updated_at"])
        receipt = (registry or DisbursementRegistryClient()).anchor_settlement(
            str(execution.disbursement_id), digest
        )
        with transaction.atomic():
            execution = FinancialExecutionService._get_locked(execution_id, actor)
            if execution.settlement_hash != digest:
                raise PayoutEvidenceMismatch()
            execution.settlement_anchor_tx = receipt.transaction_hash
            execution.status = DisbursementExecution.Status.SETTLEMENT_ANCHORED
            execution.save(update_fields=["settlement_anchor_tx", "status", "updated_at"])
        # Do not advance rotation if post-settlement ledger consistency changed;
        # leave for manual dispute/reconciliation instead of paying twice.
        if execution.disbursement.status != Disbursement.Status.COMPLETED:
            DisbursementService.complete(
                disbursement_id=execution.disbursement_id,
                completed_by=actor,
            )
        return execution

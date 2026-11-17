from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.exceptions import DomainException
from core.responses import success
from disbursements.selectors.disbursement_selector import DisbursementSelector
from disbursements.serializers.disbursement import DisbursementSerializer
from disbursements.services.financial_execution_service import FinancialExecutionService


class _PayoutBase(APIView):
    permission_classes = [IsAuthenticated]

    def get_disbursement(self, group_id, disbursement_id):
        disbursement = DisbursementSelector.get_group_disbursement(
            group_id=group_id, disbursement_id=disbursement_id
        )
        if disbursement is None:
            raise DomainException("Desembolso não encontrado.")
        return disbursement


class GroupDisbursementExecuteView(_PayoutBase):
    """A privileged server-side action, never a browser-controlled wallet call."""

    def post(self, request, group_id, disbursement_id):
        item = self.get_disbursement(group_id, disbursement_id)
        execution = FinancialExecutionService.prepare(
            disbursement_id=item.id, actor=request.user
        )
        execution = FinancialExecutionService.anchor_intent(
            execution_id=execution.id, actor=request.user
        )
        execution = FinancialExecutionService.send(
            execution_id=execution.id, actor=request.user
        )
        item.refresh_from_db()
        return success(
            data=DisbursementSerializer(item).data,
            message="Pedido B2C enviado; aguarda confirmação financeira do operador.",
        )


class GroupDisbursementReconcileView(_PayoutBase):
    def post(self, request, group_id, disbursement_id):
        item = self.get_disbursement(group_id, disbursement_id)
        if not hasattr(item, "execution"):
            raise DomainException("Nenhuma execução financeira foi iniciada.")
        execution = FinancialExecutionService.query_provider(
            execution_id=item.execution.id, actor=request.user
        )
        if execution.status == execution.Status.PROVIDER_CONFIRMED:
            FinancialExecutionService.anchor_settlement(
                execution_id=execution.id, actor=request.user
            )
        item.refresh_from_db()
        return success(
            data=DisbursementSerializer(item).data,
            message="Estado consultado no fornecedor e actualizado.",
        )


class GroupDisbursementRecoverProofView(_PayoutBase):
    """Explicit recovery without re-sending money after interrupted anchoring."""

    def post(self, request, group_id, disbursement_id):
        item = self.get_disbursement(group_id, disbursement_id)
        if not hasattr(item, "execution"):
            raise DomainException("Execução financeira não encontrada.")
        execution = item.execution
        if execution.status in (
            execution.Status.READY,
            execution.Status.INTENT_ANCHORING,
        ):
            FinancialExecutionService.anchor_intent(
                execution_id=execution.id, actor=request.user
            )
        elif execution.status in (
            execution.Status.PROVIDER_CONFIRMED,
            execution.Status.SETTLEMENT_ANCHORING,
            execution.Status.SETTLEMENT_ANCHORED,
        ):
            FinancialExecutionService.anchor_settlement(
                execution_id=execution.id, actor=request.user
            )
        else:
            raise DomainException(
                "Não é seguro repetir o pagamento; consulte primeiro o fornecedor."
            )
        item.refresh_from_db()
        return success(
            data=DisbursementSerializer(item).data,
            message="Ancoragem reconciliada sem reenvio de pagamento.",
        )

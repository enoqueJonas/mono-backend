from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.exceptions import DomainException
from core.responses import success
from disbursements.serializers.create_disbursement import (
    CreateDisbursementSerializer,
)
from disbursements.serializers.disbursement import (
    DisbursementSerializer,
)
from disbursements.selectors.disbursement_selector import (
    DisbursementSelector,
)
from disbursements.services.disbursement_service import (
    DisbursementService,
)
from disbursements.services.sandbox_payout_service import SandboxPayoutService
from groups.services.group_member_service import (
    GroupMemberService,
)
from groups.services.group_service import GroupService


class GroupDisbursementListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        GroupMemberService.ensure_active_member(
            group_id=group_id,
            user=request.user,
        )

        disbursements = (
            DisbursementSelector.list_group_disbursements(
                group_id=group_id,
            )
        )

        return success(
            data=DisbursementSerializer(
                disbursements,
                many=True,
            ).data
        )

    def post(self, request, group_id):
        GroupService.ensure_manager(
            group_id=group_id,
            user=request.user,
        )

        serializer = CreateDisbursementSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        disbursement = DisbursementService.create(
            group_id=group_id,
            created_by=request.user,
            cycle_number=serializer.validated_data[
                "cycle_number"
            ],
        )

        return success(
            data=DisbursementSerializer(
                disbursement
            ).data,
            message="Desembolso criado com sucesso.",
            status_code=201,
        )


class GroupDisbursementDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(
        self,
        request,
        group_id,
        disbursement_id,
    ):
        GroupMemberService.ensure_active_member(
            group_id=group_id,
            user=request.user,
        )

        disbursement = (
            DisbursementSelector.get_group_disbursement(
                group_id=group_id,
                disbursement_id=disbursement_id,
            )
        )

        if disbursement is None:
            raise DomainException(
                "Desembolso não encontrado."
            )

        return success(
            data=DisbursementSerializer(
                disbursement
            ).data
        )


class GroupDisbursementApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        group_id,
        disbursement_id,
    ):
        disbursement = (
            DisbursementSelector.get_group_disbursement(
                group_id=group_id,
                disbursement_id=disbursement_id,
            )
        )

        if disbursement is None:
            raise DomainException(
                "Desembolso não encontrado."
            )

        approved = DisbursementService.approve(
            disbursement_id=disbursement.id,
            approved_by=request.user,
        )

        return success(
            data=DisbursementSerializer(
                approved
            ).data,
            message="Voto registado; desembolso aprovado somente após quórum.",
        )


class GroupDisbursementCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        group_id,
        disbursement_id,
    ):
        disbursement = (
            DisbursementSelector.get_group_disbursement(
                group_id=group_id,
                disbursement_id=disbursement_id,
            )
        )

        if disbursement is None:
            raise DomainException(
                "Desembolso não encontrado."
            )

        completed = DisbursementService.complete(
            disbursement_id=disbursement.id,
            completed_by=request.user,
        )

        return success(
            data=DisbursementSerializer(
                completed
            ).data,
            message=(
                "Desembolso concluído com sucesso."
            ),
        )


class GroupSandboxDisbursementExecuteView(APIView):
    """Runs a fully FICTITIOUS payout with blockchain proofs; never real money."""
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id, disbursement_id):
        GroupService.ensure_manager(group_id=group_id, user=request.user)
        disbursement = DisbursementSelector.get_group_disbursement(
            group_id=group_id, disbursement_id=disbursement_id
        )
        if disbursement is None:
            raise DomainException("Desembolso não encontrado.")
        result = SandboxPayoutService.execute(
            disbursement_id=disbursement.pk,
            completed_by=request.user,
        )
        return success(
            data=DisbursementSerializer(result).data,
            message="Desembolso fictício validado na sandbox e ancorado no Ganache; não houve transferência real.",
        )


# Non-custodial workflow: these endpoints never call a payment provider.
from disbursements.models import TreasuryMandate, ExternalPaymentReport
from disbursements.serializers.external_payment import (
    AcknowledgeExternalPaymentSerializer,
    AppointTreasuryMandateSerializer,
    ExternalPaymentReportSerializer,
    ReportExternalPaymentSerializer,
    TreasuryMandateSerializer,
)
from disbursements.services.noncustodial_service import (
    NonCustodialDisbursementService,
)


class GroupTreasuryMandateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        GroupMemberService.ensure_active_member(group_id=group_id, user=request.user)
        NonCustodialDisbursementService.require_mode()
        mandate = TreasuryMandate.objects.filter(group_id=group_id).first()
        return success(
            data=TreasuryMandateSerializer(mandate).data if mandate else None,
        )

    def post(self, request, group_id):
        serializer = AppointTreasuryMandateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mandate = NonCustodialDisbursementService.appoint_custodian(
            group_id=group_id,
            appointed_by=request.user,
            group_member_id=serializer.validated_data["group_member_id"],
            provider=serializer.validated_data["provider"],
            wallet_alias=serializer.validated_data["wallet_alias"],
        )
        return success(
            data=TreasuryMandateSerializer(mandate).data,
            message="Responsável da carteira externa designado.",
            status_code=201,
        )


class NonCustodialDisbursementActionView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, group_id, disbursement_id):
        d = DisbursementSelector.get_group_disbursement(
            group_id=group_id, disbursement_id=disbursement_id,
        )
        if d is None:
            raise DomainException("Desembolso não encontrado.")
        return d


class ExternalDisbursementOpenView(NonCustodialDisbursementActionView):
    def post(self, request, group_id, disbursement_id):
        d = self._get(group_id, disbursement_id)
        d = NonCustodialDisbursementService.open_for_external_payment(
            disbursement_id=d.pk, requested_by=request.user,
        )
        return success(
            data=DisbursementSerializer(d).data,
            message="Autorização ancorada; transferência a efectuar fora do Mono.",
        )


class ExternalDisbursementReportView(NonCustodialDisbursementActionView):
    def get(self, request, group_id, disbursement_id):
        NonCustodialDisbursementService.require_mode()
        d = self._get(group_id, disbursement_id)
        member = GroupMemberService.ensure_active_member(
            group_id=group_id, user=request.user,
        )
        mandate = TreasuryMandate.objects.filter(group_id=group_id).first()
        if (
            member.role != "MANAGER"
            and member.pk != d.beneficiary_id
            and (mandate is None or mandate.custodian_id != member.pk)
        ):
            raise DomainException("Acesso ao comprovativo reservado aos intervenientes.")
        report = ExternalPaymentReport.objects.filter(disbursement=d).first()
        return success(
            data=ExternalPaymentReportSerializer(report).data if report else None,
        )

    def post(self, request, group_id, disbursement_id):
        d = self._get(group_id, disbursement_id)
        serializer = ReportExternalPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = NonCustodialDisbursementService.report_external_payment(
            disbursement_id=d.pk, reported_by=request.user,
            reference=serializer.validated_data["transfer_reference"],
        )
        return success(
            data=DisbursementSerializer(updated).data,
            message="Pagamento externo declarado; aguarda confirmação do beneficiário.",
        )


class ExternalDisbursementAcknowledgeView(NonCustodialDisbursementActionView):
    def post(self, request, group_id, disbursement_id):
        d = self._get(group_id, disbursement_id)
        serializer = AcknowledgeExternalPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = NonCustodialDisbursementService.respond_to_report(
            disbursement_id=d.pk,
            responded_by=request.user,
            received=serializer.validated_data["received"],
            dispute_reason=serializer.validated_data.get("dispute_reason", ""),
        )
        return success(
            data=DisbursementSerializer(updated).data,
            message=(
                "Recebimento declarado; aguarda ancoragem da evidência."
                if serializer.validated_data["received"]
                else "Pagamento contestado; não foi concluído."
            ),
        )


class ExternalDisbursementFinalizeView(NonCustodialDisbursementActionView):
    def post(self, request, group_id, disbursement_id):
        d = self._get(group_id, disbursement_id)
        updated = NonCustodialDisbursementService.finalize_acknowledged_payment(
            disbursement_id=d.pk, requested_by=request.user,
        )
        return success(
            data=DisbursementSerializer(updated).data,
            message=(
                "Declaração do beneficiário ancorada e rotação concluída. "
                "Isto não certifica liquidação por prestador externo."
            ),
        )

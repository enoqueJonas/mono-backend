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
from disbursements.models import ExternalWalletCustody
from disbursements.serializers.external_payment import (
    DesignateCustodianSerializer, ReportExternalPaymentSerializer,
    DisputeExternalPaymentSerializer,
)
from disbursements.services.external_wallet_service import ExternalWalletService
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


class GroupExternalWalletCustodyView(APIView):
    """Group custody is explicit; it is not a payment authorization to Mono."""
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        ExternalWalletService.require_enabled()
        GroupMemberService.ensure_active_member(group_id=group_id, user=request.user)
        custody = ExternalWalletCustody.objects.filter(group_id=group_id).first()
        if custody is None:
            return success(data=None)
        return success(data={
            "custodian": str(custody.custodian_id),
            "custodian_user_id": str(custody.custodian.user_id),
            "provider": custody.provider,
            "wallet_number": custody.wallet_number,
            "verification_level": "SELF_DECLARED_NOT_PROVIDER_VERIFIED",
        })

    def post(self, request, group_id):
        serializer = DesignateCustodianSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        custody = ExternalWalletService.designate_custodian(
            group_id=group_id,
            designated_by=request.user,
            member_id=serializer.validated_data["member_id"],
            provider=serializer.validated_data["provider"],
            wallet_number=serializer.validated_data["wallet_number"],
        )
        return success(data={
            "custodian": str(custody.custodian_id),
            "provider": custody.provider,
            "wallet_number": custody.wallet_number,
            "verification_level": "SELF_DECLARED_NOT_PROVIDER_VERIFIED",
        }, message="Responsável pela carteira externa designado.")


class GroupExternalPaymentReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id, disbursement_id):
        disbursement = DisbursementSelector.get_group_disbursement(
            group_id=group_id, disbursement_id=disbursement_id
        )
        if disbursement is None:
            raise DomainException("Desembolso não encontrado.")
        serializer = ReportExternalPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = ExternalWalletService.report_payment(
            disbursement_id=disbursement.pk,
            reported_by=request.user,
            **serializer.validated_data,
        )
        return success(data={
            "reference": report.reference,
            "provider": report.provider,
            "status": report.status,
            "verification_level": "UNVERIFIED_CLAIM",
        }, message="Transferência externa declarada; aguarda confirmação do beneficiário.")


class GroupExternalPaymentConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id, disbursement_id):
        disbursement = DisbursementSelector.get_group_disbursement(
            group_id=group_id, disbursement_id=disbursement_id
        )
        if disbursement is None:
            raise DomainException("Desembolso não encontrado.")
        outcome = ExternalWalletService.confirm_receipt(
            disbursement_id=disbursement.pk,
            confirmed_by=request.user,
        )
        return success(
            data=DisbursementSerializer(outcome).data,
            message="Recepção declarada pelo beneficiário; sem verificação independente do operador.",
        )


class GroupExternalPaymentDisputeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id, disbursement_id):
        disbursement = DisbursementSelector.get_group_disbursement(
            group_id=group_id, disbursement_id=disbursement_id
        )
        if disbursement is None:
            raise DomainException("Desembolso não encontrado.")
        serializer = DisputeExternalPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = ExternalWalletService.dispute_receipt(
            disbursement_id=disbursement.pk,
            disputed_by=request.user,
            reason=serializer.validated_data["reason"],
        )
        return success(data={"status": report.status}, message=(
            "Divergência registada. A rotação permanece bloqueada até resolução."
        ))

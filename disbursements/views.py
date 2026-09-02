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
            cycle_number=serializer.validated_data[
                "cycle_number"
            ],
        )

        return success(
            data=DisbursementSerializer(
                disbursement
            ).data,
            message="Disbursement created successfully.",
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
                "Disbursement not found."
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
                "Disbursement not found."
            )

        approved = DisbursementService.approve(
            disbursement_id=disbursement.id,
            approved_by=request.user,
        )

        return success(
            data=DisbursementSerializer(
                approved
            ).data,
            message="Disbursement approved successfully.",
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
                "Disbursement not found."
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
                "Disbursement completed successfully."
            ),
        )

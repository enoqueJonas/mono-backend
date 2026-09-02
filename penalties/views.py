from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.exceptions import DomainException
from core.responses import success
from groups.services.group_member_service import (
    GroupMemberService,
)
from penalties.selectors import PenaltySelector
from penalties.serializers import (
    CreatePenaltySerializer,
    PenaltySerializer,
)
from penalties.services import PenaltyService


class GroupPenaltyListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        GroupMemberService.ensure_active_member(
            group_id=group_id,
            user=request.user,
        )

        penalties = (
            PenaltySelector.list_group_penalties(
                group_id=group_id,
            )
        )

        return success(
            data=PenaltySerializer(
                penalties,
                many=True,
            ).data
        )

    def post(self, request, group_id):
        serializer = CreatePenaltySerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        penalty = PenaltyService.create_for_group(
            group_id=group_id,
            member_id=serializer.validated_data[
                "member_id"
            ],
            created_by=request.user,
            reason=serializer.validated_data[
                "reason"
            ],
        )

        return success(
            data=PenaltySerializer(penalty).data,
            message="Penalty created successfully.",
            status_code=201,
        )


class GroupPenaltyResolveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        group_id,
        penalty_id,
    ):
        penalty = (
            PenaltySelector.get_group_penalty(
                group_id=group_id,
                penalty_id=penalty_id,
            )
        )

        if penalty is None:
            raise DomainException(
                "Penalty not found."
            )

        resolved = (
            PenaltyService.resolve_for_group(
                group_id=group_id,
                penalty_id=penalty.id,
                resolved_by=request.user,
            )
        )

        return success(
            data=PenaltySerializer(resolved).data,
            message="Penalty resolved successfully.",
        )

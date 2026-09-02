from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import success
from groups.models import Group, RotationOrder
from groups.serializers.rotation import (
    GenerateRotationSerializer,
    RotationOrderSerializer,
)
from groups.services.group_member_service import (
    GroupMemberService,
)
from groups.services.group_service import (
    GroupNotFound,
    GroupService,
)
from groups.services.rotation_service import (
    RotationService,
)


class GroupRotationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        GroupMemberService.ensure_active_member(
            group_id=group_id,
            user=request.user,
        )

        cycle_number = request.query_params.get(
            "cycle_number"
        )

        rotations = (
            RotationOrder.objects
            .select_related(
                "member",
                "member__user",
                "group_settings",
            )
            .filter(
                group_id=group_id,
            )
        )

        if cycle_number is not None:
            rotations = rotations.filter(
                cycle_number=cycle_number,
            )

        rotations = rotations.order_by(
            "cycle_number",
            "position",
        )

        return success(
            data=RotationOrderSerializer(
                rotations,
                many=True,
            ).data
        )

    def post(self, request, group_id):
        GroupService.ensure_manager(
            group_id=group_id,
            user=request.user,
        )

        serializer = GenerateRotationSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )

        try:
            group = Group.objects.get(
                id=group_id
            )
        except Group.DoesNotExist:
            raise GroupNotFound()

        rotation = RotationService.generate_cycle(
            group=group,
            cycle_number=(
                serializer.validated_data[
                    "cycle_number"
                ]
            ),
            contribution_period=(
                serializer.validated_data[
                    "contribution_period"
                ]
            ),
        )

        return success(
            data=RotationOrderSerializer(
                rotation,
                many=True,
            ).data,
            message=(
                "Rotation cycle generated successfully."
            ),
            status_code=201,
        )

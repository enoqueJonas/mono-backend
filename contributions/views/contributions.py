from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from contributions.serializers.create_contribution import CreateContributionSerializer
from contributions.serializers.contribution import ContributionSerializer
from contributions.services.contribution_service import ContributionService
from contributions.selectors.contribution_selector import ContributionSelector
from groups.services.group_member_service import GroupMemberService
from core.responses import success


class GroupContributionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):

        GroupMemberService.ensure_active_member(
            group_id=group_id,
            user=request.user,
        )

        contributions = ContributionSelector.list_group_contributions(
            group_id=group_id
        )

        return success(
            data=ContributionSerializer(contributions, many=True).data
        )

    def post(self, request, group_id):
        serializer = CreateContributionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        contribution = ContributionService.register_manual_contribution(
            group_id=group_id,
            registered_by=request.user,
            data=serializer.validated_data,
        )

        return success(
            data=ContributionSerializer(contribution).data,
            message="Contribution registered successfully.",
            status_code=201,
        )

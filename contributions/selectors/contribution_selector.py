from contributions.models import Contribution


class ContributionSelector:

    @staticmethod
    def list_group_contributions(*, group_id):
        return (
            Contribution.objects
            .select_related(
                "member",
                "member__user",
                "member__group",
            )
            .filter(member__group_id=group_id)
            .order_by("-contribution_period", "-created_at")
        )

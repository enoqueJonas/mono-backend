from penalties.models import Penalty


class PenaltySelector:

    @staticmethod
    def list_group_penalties(*, group_id):
        return (
            Penalty.objects
            .select_related(
                "member",
                "member__user",
                "member__group",
            )
            .filter(member__group_id=group_id)
            .order_by("-created_at")
        )

    @staticmethod
    def get_group_penalty(
        *,
        group_id,
        penalty_id,
    ):
        return (
            Penalty.objects
            .select_related(
                "member",
                "member__user",
                "member__group",
            )
            .filter(
                id=penalty_id,
                member__group_id=group_id,
            )
            .first()
        )

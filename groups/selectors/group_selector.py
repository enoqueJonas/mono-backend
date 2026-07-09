from groups.models import Group


class GroupSelector:

    @staticmethod
    def list_user_groups(*, user):
        return (
            Group.objects
            .filter(members__user=user, members__status="ACTIVE")
            .select_related("settings")
            .distinct()
            .order_by("-created_at")
        )

    @staticmethod
    def get_group_for_user(*, group_id, user):
        return (
            Group.objects
            .filter(
                id=group_id,
                members__user=user,
                members__status="ACTIVE",
            )
            .select_related("settings")
            .first()
        )

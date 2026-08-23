from groups.models import Group
from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce

from contributions.models import Contribution
from groups.models import Group, GroupMember


class GroupSelector:

    @staticmethod
    def list_user_groups(*, user):
        return (
            Group.objects
            .filter(members__user=user, members__status="ACTIVE")
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
            .first()
        )

    @staticmethod
    def list_user_groups(*, user):

        return (

            Group.objects

            .filter(

                members__user=user,

                members__status=GroupMember.Status.ACTIVE,

            )


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

                members__status=GroupMember.Status.ACTIVE,

            )


            .first()

        )

    @staticmethod
    def get_group_statistics(*, group: Group) -> dict:

        active_members = GroupMember.objects.filter(
            group=group,
            status=GroupMember.Status.ACTIVE,

        ).count()

        contribution_stats = Contribution.objects.filter(
            member__group=group,
        ).aggregate(
            confirmed_contributions=Count(
                "id",
                filter=Q(status=Contribution.Status.CONFIRMED),
            ),

            pending_contributions=Count(
                "id",
                filter=Q(status=Contribution.Status.PENDING),
            ),

            total_confirmed_amount=Coalesce(
                Sum(
                    "amount",
                    filter=Q(status=Contribution.Status.CONFIRMED),
                ),
                Value(0),
                output_field=DecimalField(
                    max_digits=14,
                    decimal_places=2,
                ),
            ),
        )

        return {
            "active_members": active_members,
            "maximum_members": group.current_settings.maximum_members,
            "confirmed_contributions": (
                contribution_stats["confirmed_contributions"]
            ),
            "pending_contributions": (
                contribution_stats["pending_contributions"]
            ),
            "total_confirmed_amount": (
                contribution_stats["total_confirmed_amount"]
            ),
        }

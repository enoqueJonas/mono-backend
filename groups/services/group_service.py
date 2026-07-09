from django.db import transaction

from groups.models import Group, GroupMember, GroupSettings


class GroupService:

    @staticmethod
    @transaction.atomic
    def create_group(*, created_by, data: dict) -> Group:
        settings_data = data.pop("settings")

        group = Group.objects.create(
            name=data["name"],
            description=data.get("description", ""),
        )

        GroupSettings.objects.create(
            group=group,
            **settings_data,
        )

        GroupMember.objects.create(
            group=group,
            user=created_by,
            role=GroupMember.Role.MANAGER,
            status=GroupMember.Status.ACTIVE,
        )

        return group

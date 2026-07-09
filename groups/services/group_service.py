from groups.models import Group, GroupMember
from core.exceptions import DomainException
from accounts.utils.phone import normalize_mz_phone
from accounts.models import User
from django.db import transaction

from groups.models import Group, GroupMember, GroupSettings


class GroupNotFound(DomainException):
    default_message = "Group not found."


class UserNotFound(DomainException):
    default_message = "User not found."


class NotGroupManager(DomainException):
    default_message = "Only group managers can perform this action."


class UserAlreadyMember(DomainException):
    default_message = "User is already a member of this group."


class GroupIsFull(DomainException):
    default_message = "Group has reached the maximum number of members."


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

    @staticmethod
    def ensure_manager(*, group_id, user):
        membership = GroupMember.objects.filter(
            group_id=group_id,
            user=user,
            role=GroupMember.Role.MANAGER,
            status=GroupMember.Status.ACTIVE,
        ).first()

        if membership is None:
            raise NotGroupManager()

        return membership

    @staticmethod
    def add_member(*, group_id, added_by, phone_number):
        try:
            group = Group.objects.select_related("settings").get(id=group_id)
        except Group.DoesNotExist:
            raise GroupNotFound()

        GroupService.ensure_manager(
            group_id=group.id,
            user=added_by,
        )

        normalized_phone = normalize_mz_phone(phone_number)

        user = User.objects.filter(
            phone_number=normalized_phone
        ).first()

        if user is None:
            raise UserNotFound()

        if GroupMember.objects.filter(group=group, user=user).exists():
            raise UserAlreadyMember()

        active_members_count = GroupMember.objects.filter(
            group=group,
            status=GroupMember.Status.ACTIVE,
        ).count()

        if active_members_count >= group.settings.maximum_members:
            raise GroupIsFull()

        return GroupMember.objects.create(
            group=group,
            user=user,
            role=GroupMember.Role.MEMBER,
            status=GroupMember.Status.ACTIVE,
        )

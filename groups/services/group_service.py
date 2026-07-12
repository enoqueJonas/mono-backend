from django.db import transaction
from django.utils import timezone

from groups.models import Group, GroupMember, GroupSettings
from contributions.models import Contribution
from accounts.models import User
from groups.models import Group, GroupMember
from core.exceptions import DomainException
from accounts.utils.phone import normalize_mz_phone
from identity.services.did_service import DIDService


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

        DIDService.create_for_group(group=group)

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

        existing_member = GroupMember.objects.filter(
            group=group,
            user=user,
        ).first()

        if existing_member is not None:
            if existing_member.status != GroupMember.Status.LEFT:
                raise UserAlreadyMember()

            existing_member.status = GroupMember.Status.ACTIVE
            existing_member.role = GroupMember.Role.MEMBER
            existing_member.joined_at = timezone.now()
            existing_member.left_at = None

            existing_member.save(
                update_fields=[
                    "status",
                    "role",
                    "joined_at",
                    "left_at",
                    "updated_at",
                ]
            )

            return existing_member

        return GroupMember.objects.create(
            group=group,
            user=user,
            role=GroupMember.Role.MEMBER,
            status=GroupMember.Status.ACTIVE,
        )


class GroupAlreadyArchived(DomainException):
    default_message = "Group is already archived."


class GroupService:

    @staticmethod
    def archive_group(*, group_id, archived_by):
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise GroupNotFound()

        GroupService.ensure_manager(
            group_id=group.id,
            user=archived_by,
        )

        if group.status == Group.Status.ARCHIVED:
            raise GroupAlreadyArchived()

        group.status = Group.Status.ARCHIVED
        group.save(update_fields=["status", "updated_at"])

        return group

        STRUCTURAL_SETTING_FIELDS = {
            "contribution_amount",
            "contribution_frequency",
            "maximum_members",
            "rotation_strategy",
            "requires_consensus",
        }

    @staticmethod
    @transaction.atomic
    def update_settings(
        *,
        group_id,
        updated_by,
        data: dict,
    ):
        try:
            group = (
                Group.objects
                .select_related("settings")
                .get(id=group_id)
            )
        except Group.DoesNotExist:
            raise GroupNotFound()

        GroupService.ensure_manager(
            group_id=group.id,
            user=updated_by,
        )

        if group.status == Group.Status.ARCHIVED:
            raise ArchivedGroup()

        supplied_structural_fields = (
            GroupService.STRUCTURAL_SETTING_FIELDS
            .intersection(data.keys())
        )

        has_confirmed_contributions = (
            Contribution.objects.filter(
                member__group=group,
                status=Contribution.Status.CONFIRMED,
            ).exists()
        )

        if (
            supplied_structural_fields
            and has_confirmed_contributions
        ):
            raise StructuralSettingsLocked()

        if "maximum_members" in data:
            active_members_count = GroupMember.objects.filter(
                group=group,
                status=GroupMember.Status.ACTIVE,
            ).count()

            if data["maximum_members"] < active_members_count:
                raise MaximumMembersBelowCurrentCount()

        settings = group.settings

        for field, value in data.items():
            setattr(settings, field, value)

        settings.save(
            update_fields=[
                *data.keys(),
                "updated_at",
            ]
        )

        return settings

    @staticmethod
    @transaction.atomic
    def remove_member(
        *,
        group_id,
        group_member_id,
        removed_by,
    ) -> GroupMember:
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise GroupNotFound()

        GroupService.ensure_manager(
            group_id=group.id,
            user=removed_by,
        )

        if group.status == Group.Status.ARCHIVED:
            raise ArchivedGroup()

        member = (
            GroupMember.objects
            .select_related("user", "group")
            .filter(
                id=group_member_id,
                group=group,
            )
            .first()
        )

        if member is None:
            raise GroupMemberNotFound()

        if member.status == GroupMember.Status.LEFT:
            raise MemberAlreadyLeft()

        if member.user_id == removed_by.id:
            raise ManagerCannotRemoveSelf()

        member.status = GroupMember.Status.LEFT
        member.left_at = timezone.now()

        member.save(
            update_fields=[
                "status",
                "left_at",
                "updated_at",
            ]
        )

        return member


class ArchivedGroup(DomainException):
    default_message = "Archived groups cannot be modified."


class StructuralSettingsLocked(DomainException):
    default_message = (
        "Structural group settings cannot be changed "
        "after the first confirmed contribution."
    )


class MaximumMembersBelowCurrentCount(DomainException):
    default_message = (
        "Maximum members cannot be lower than the current "
        "number of active members."
    )


class GroupMemberNotFound(DomainException):
    default_message = "Group member not found."


class MemberAlreadyLeft(DomainException):
    default_message = "This member has already left the group."


class ManagerCannotRemoveSelf(DomainException):
    default_message = (
        "The group manager cannot remove themselves through this operation."
    )

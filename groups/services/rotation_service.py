import random

from django.db import transaction

from core.exceptions import DomainException
from groups.models import (
    Group,
    GroupMember,
    GroupSettings,
    RotationOrder,
)


class RotationAlreadyExists(DomainException):
    default_message = (
        "Rotation order already exists for this cycle."
    )


class NoActiveMembers(DomainException):
    default_message = (
        "The group has no active members."
    )


class CurrentRotationNotFound(DomainException):
    default_message = (
        "No current beneficiary exists for this cycle."
    )


class RotationCycleNotFound(DomainException):
    default_message = (
        "Rotation cycle does not exist."
    )


class RotationService:

    @staticmethod
    @transaction.atomic
    def generate_cycle(
        *,
        group: Group,
        cycle_number: int,
        contribution_period,
        group_settings=None,
    ) -> list[RotationOrder]:

        if RotationOrder.objects.filter(
            group=group,
            cycle_number=cycle_number,
        ).exists():
            raise RotationAlreadyExists()

        members = list(
            GroupMember.objects.filter(
                group=group,
                status=GroupMember.Status.ACTIVE,
            )
        )

        if not members:
            raise NoActiveMembers()

        settings = (
            group_settings
            or group.current_settings
        )

        if (
            settings.rotation_strategy
            == GroupSettings.RotationStrategy.FIXED_ORDER
        ):
            members.sort(
                key=lambda member: member.joined_at
            )

        elif (
            settings.rotation_strategy
            == GroupSettings.RotationStrategy.RANDOM
        ):
            random.shuffle(members)

        rotation_items = []

        for index, member in enumerate(
            members,
            start=1,
        ):
            rotation_items.append(
                RotationOrder(
                    group=group,
                    member=member,
                    group_settings=settings,
                    contribution_period=contribution_period,
                    cycle_number=cycle_number,
                    position=index,
                    status=(
                        RotationOrder.Status.CURRENT
                        if index == 1
                        else RotationOrder.Status.PENDING
                    ),
                )
            )

        RotationOrder.objects.bulk_create(
            rotation_items
        )

        return list(
            RotationOrder.objects.filter(
                group=group,
                cycle_number=cycle_number,
            ).order_by("position")
        )

    @staticmethod
    def get_current(
        *,
        group: Group,
        cycle_number: int,
    ) -> RotationOrder:

        current = (
            RotationOrder.objects
            .select_related(
                "member",
                "member__user",
            )
            .filter(
                group=group,
                cycle_number=cycle_number,
                status=RotationOrder.Status.CURRENT,
            )
            .first()
        )

        if current is None:
            cycle_exists = (
                RotationOrder.objects
                .filter(
                    group=group,
                    cycle_number=cycle_number,
                )
                .exists()
            )

            if not cycle_exists:
                raise RotationCycleNotFound()

            raise CurrentRotationNotFound()

        return current

    @staticmethod
    @transaction.atomic
    def advance(
        *,
        group: Group,
        cycle_number: int,
    ) -> RotationOrder | None:

        rotation_items = (
            RotationOrder.objects
            .select_for_update()
            .filter(
                group=group,
                cycle_number=cycle_number,
            )
            .order_by("position")
        )

        if not rotation_items.exists():
            raise RotationCycleNotFound()

        current = (
            rotation_items
            .filter(
                status=RotationOrder.Status.CURRENT,
            )
            .first()
        )

        if current is None:
            raise CurrentRotationNotFound()

        current.status = (
            RotationOrder.Status.COMPLETED
        )

        current.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        next_item = (
            rotation_items
            .filter(
                position__gt=current.position,
                status=RotationOrder.Status.PENDING,
            )
            .order_by("position")
            .first()
        )

        if next_item is None:
            return None

        next_item.status = (
            RotationOrder.Status.CURRENT
        )

        next_item.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return next_item

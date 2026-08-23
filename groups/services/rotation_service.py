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


class RotationService:

    @staticmethod
    @transaction.atomic
    def generate_cycle(
        *,
        group: Group,
        cycle_number: int,
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

        settings = group.current_settings

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

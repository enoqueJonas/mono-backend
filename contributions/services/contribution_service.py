from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from core.exceptions import DomainException
from contributions.models import Contribution
from groups.models import Group, GroupMember


class InvalidContributionCurrency(DomainException):
    default_message = (
        "Contribution currency does not match "
        "group settings."
    )


class DuplicateContribution(DomainException):
    default_message = (
        "A contribution already exists for "
        "this member and period."
    )


class DuplicateContributionReference(DomainException):
    default_message = (
        "A contribution with this reference "
        "already exists."
    )


class GroupNotFound(DomainException):
    default_message = "Group not found."


class MemberNotFound(DomainException):
    default_message = "Member not found in this group."


class NotGroupManager(DomainException):
    default_message = "Only group managers can register manual contributions."


class InactiveMember(DomainException):
    default_message = "Only active members can receive contributions."


class InvalidContributionAmount(DomainException):
    default_message = "Contribution amount does not match group settings."


class ContributionService:

    @staticmethod
    @transaction.atomic
    def register_manual_contribution(
        *,
        group_id,
        registered_by,
        data: dict,
    ) -> Contribution:
        try:
            group = Group.objects.get(
                id=group_id,
            )
        except Group.DoesNotExist:
            raise GroupNotFound()

        current_settings = group.current_settings
        manager_membership = GroupMember.objects.filter(
            group=group,
            user=registered_by,
            role=GroupMember.Role.MANAGER,
            status=GroupMember.Status.ACTIVE,
        ).first()

        if manager_membership is None:
            raise NotGroupManager()

        member = GroupMember.objects.filter(
            id=data["group_member_id"],
            group=group,
        ).first()

        if member is None:
            raise MemberNotFound()

        if member.status != GroupMember.Status.ACTIVE:
            raise InactiveMember()

        expected_amount = Decimal(
            current_settings.contribution_amount
        )
        received_amount = Decimal(data["amount"])

        if received_amount != expected_amount:
            raise InvalidContributionAmount()

        reference = ContributionService._generate_manual_reference()

        contribution = Contribution.objects.create(
            member=member,
            amount=received_amount,
            group_settings=current_settings,
            currency=current_settings.currency,
            contribution_period=data["contribution_period"],
            reference=reference,
            source=Contribution.Source.MANUAL,
            status=Contribution.Status.CONFIRMED,
        )

        return contribution

    @staticmethod
    @transaction.atomic
    def register_mobile_wallet_contribution(
        *,
        data: dict,
    ) -> Contribution:

        try:
            group = Group.objects.get(
                id=data["group_id"],
            )
        except Group.DoesNotExist:
            raise GroupNotFound()

        current_settings = group.current_settings

        member = (
            GroupMember.objects
            .filter(
                id=data["group_member_id"],
                group=group,
            )
            .first()
        )

        if member is None:
            raise MemberNotFound()

        if member.status != GroupMember.Status.ACTIVE:
            raise InactiveMember()

        expected_amount = Decimal(
            current_settings.contribution_amount
        )

        received_amount = Decimal(
            data["amount"]
        )

        if received_amount != expected_amount:
            raise InvalidContributionAmount()

        if (
            data["currency"]
            != current_settings.currency
        ):
            raise InvalidContributionCurrency()

        if Contribution.objects.filter(
            reference=data["reference"],
        ).exists():
            raise DuplicateContributionReference()

        if Contribution.objects.filter(
            member=member,
            contribution_period=data[
                "contribution_period"
            ],
        ).exists():
            raise DuplicateContribution()

        contribution = Contribution.objects.create(
            member=member,
            group_settings=current_settings,
            amount=received_amount,
            currency=current_settings.currency,
            contribution_period=data[
                "contribution_period"
            ],
            reference=data["reference"],
            source=Contribution.Source.MOBILE_WALLET,
            status=Contribution.Status.CONFIRMED,
        )

        return contribution

    @staticmethod
    def _generate_manual_reference() -> str:
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
        return f"MAN-{timestamp}"

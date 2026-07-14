from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce

from contributions.models import Contribution
from groups.models import GroupMember


@dataclass(frozen=True)
class ContributionHistorySummary:
    confirmed_contributions: int
    total_contributed: Decimal
    currency: str


class ContributionHistorySelector:

    @staticmethod
    def summarize(
        *,
        group_member: GroupMember,
        period_start: date,
        period_end: date,
    ) -> ContributionHistorySummary:
        contributions = Contribution.objects.filter(
            member=group_member,
            status=Contribution.Status.CONFIRMED,
            contribution_period__gte=period_start,
            contribution_period__lte=period_end,
        )

        summary = contributions.aggregate(
            confirmed_contributions=Count("id"),
            total_contributed=Coalesce(
                Sum("amount"),
                Value(Decimal("0.00")),
                output_field=DecimalField(
                    max_digits=14,
                    decimal_places=2,
                ),
            ),
        )

        first_contribution = contributions.order_by(
            "contribution_period",
            "created_at",
        ).first()

        currency = (
            first_contribution.currency
            if first_contribution is not None
            else group_member.group.settings.currency
        )

        return ContributionHistorySummary(
            confirmed_contributions=(
                summary["confirmed_contributions"]
            ),
            total_contributed=summary["total_contributed"],
            currency=currency,
        )

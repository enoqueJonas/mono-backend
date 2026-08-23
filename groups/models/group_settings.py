from django.db import models

from core.models import BaseModel


class GroupSettings(BaseModel):
    class ContributionFrequency(models.TextChoices):
        DAILY = "DAILY", "Daily"
        WEEKLY = "WEEKLY", "Weekly"
        BIWEEKLY = "BIWEEKLY", "Biweekly"
        MONTHLY = "MONTHLY", "Monthly"

    class RotationStrategy(models.TextChoices):
        FIXED_ORDER = "FIXED_ORDER", "Fixed order"
        RANDOM = "RANDOM", "Random"

    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="settings_versions",
    )

    version = models.PositiveIntegerField(
        default=1,
    )

    contribution_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default="MZN",
    )

    contribution_frequency = models.CharField(
        max_length=20,
        choices=ContributionFrequency.choices,
    )

    maximum_members = models.PositiveIntegerField()

    rotation_strategy = models.CharField(
        max_length=20,
        choices=RotationStrategy.choices,
    )

    requires_consensus = models.BooleanField(
        default=True,
    )

    allow_manual_contributions = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "group_settings"
        ordering = [
            "group",
            "-version",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "group",
                    "version",
                ],
                name="unique_group_settings_version",
            ),
            models.UniqueConstraint(
                fields=["group"],
                condition=models.Q(
                    is_active=True,
                ),
                name="unique_active_group_settings",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Settings v{self.version} "
            f"for {self.group.name}"
        )

    def validate_currency(
        self,
        value: str,
    ) -> str:
        return value.upper()

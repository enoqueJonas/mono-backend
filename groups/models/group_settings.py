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

    group = models.OneToOneField(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="settings",
    )
    contribution_amount = models.DecimalField(max_digits=12, decimal_places=2)
    contribution_frequency = models.CharField(
        max_length=20,
        choices=ContributionFrequency.choices,
    )
    maximum_members = models.PositiveIntegerField()
    rotation_strategy = models.CharField(
        max_length=20,
        choices=RotationStrategy.choices,
    )
    requires_consensus = models.BooleanField(default=True)
    allow_manual_contributions = models.BooleanField(default=False)

    class Meta:
        db_table = "group_settings"

    def __str__(self):
        return f"Settings for {self.group.name}"

from django.db import models

from core.models import BaseModel


class Contribution(BaseModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        FAILED = "FAILED", "Failed"
        REVERSED = "REVERSED", "Reversed"

    class Source(models.TextChoices):
        MANUAL = "MANUAL", "Manual"
        MOBILE_WALLET = "MOBILE_WALLET", "Mobile Wallet"

    member = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.CASCADE,
        related_name="contributions",
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    currency = models.CharField(
        max_length=3,
        default="MZN",
    )

    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.MANUAL,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )

    contribution_period = models.DateField()

    reference = models.CharField(max_length=100, unique=True)

    class Meta:

        db_table = "contributions"

        constraints = [

            models.UniqueConstraint(

                fields=["member", "contribution_period"],

                name="unique_member_contribution_period",

            )

        ]

    def __str__(self):
        return f"{self.member} - {self.amount} - {self.contribution_period}"

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

    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="contributions",
    )
    member = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.CASCADE,
        related_name="contributions",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
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
    reference = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "contributions"

    def __str__(self):
        return f"{self.member} - {self.amount}"

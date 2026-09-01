import uuid

from django.db import models


class Disbursement(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        AWAITING_CONSENSUS = (
            "AWAITING_CONSENSUS",
            "Awaiting consensus",
        )
        APPROVED = "APPROVED", "Approved"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.PROTECT,
        related_name="disbursements",
    )

    beneficiary = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="disbursements",
    )

    rotation_order = models.OneToOneField(
        "groups.RotationOrder",
        on_delete=models.PROTECT,
        related_name="disbursement",
    )

    group_settings = models.ForeignKey(
        "groups.GroupSettings",
        on_delete=models.PROTECT,
        related_name="disbursements",
    )

    cycle_number = models.PositiveIntegerField()

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )

    requested_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    failure_reason = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "group",
                    "cycle_number",
                ],
                name="disb_group_cycle_idx",
            ),
            models.Index(
                fields=["status"],
                name="disb_status_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.group.name} - "
            f"Cycle {self.cycle_number} - "
            f"{self.beneficiary.user.phone_number}"
        )

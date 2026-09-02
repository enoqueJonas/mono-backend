from django.db import models

from core.models import BaseModel
from groups.models import GroupMember


class Penalty(BaseModel):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        RESOLVED = "RESOLVED", "Resolved"

    member = models.ForeignKey(
        GroupMember,
        on_delete=models.PROTECT,
        related_name="penalties",
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.member_id} - "
            f"{self.status}"
        )

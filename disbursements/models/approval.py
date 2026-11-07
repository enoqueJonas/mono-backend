import uuid

from django.conf import settings
from django.db import models


class DisbursementApproval(models.Model):
    """An authenticated application approval; not a private-key signature."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    disbursement = models.ForeignKey(
        "disbursements.Disbursement",
        on_delete=models.PROTECT,
        related_name="approvals",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="disbursement_approvals",
    )
    approved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["disbursement", "approved_by"],
                name="unique_disbursement_approval_user",
            ),
        ]
        ordering = ["approved_at"]

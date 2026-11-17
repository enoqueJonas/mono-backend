import uuid

from django.db import models


def new_payout_reference():
    """Stable idempotency reference reused for every provider reconciliation."""
    return "MONO-" + uuid.uuid4().hex[:26].upper()


class DisbursementExecution(models.Model):
    class Status(models.TextChoices):
        READY = "READY", "Ready"
        INTENT_ANCHORING = "INTENT_ANCHORING", "Anchoring approved intent"
        INTENT_ANCHORED = "INTENT_ANCHORED", "Intent anchored"
        SENDING = "SENDING", "Provider request in flight"
        PENDING = "PENDING", "Provider pending"
        UNKNOWN = "UNKNOWN", "Provider status unknown; reconcile only"
        PROVIDER_CONFIRMED = "PROVIDER_CONFIRMED", "Verified by provider"
        PROVIDER_FAILED = "PROVIDER_FAILED", "Rejected by provider"
        SETTLEMENT_ANCHORING = "SETTLEMENT_ANCHORING", "Anchoring settlement"
        SETTLEMENT_ANCHORED = "SETTLEMENT_ANCHORED", "Settlement anchored"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disbursement = models.OneToOneField(
        "disbursements.Disbursement",
        on_delete=models.PROTECT,
        related_name="execution",
    )
    reference = models.CharField(max_length=40, unique=True, default=new_payout_reference)
    provider = models.CharField(max_length=20, default="MPESA")
    recipient_msisdn = models.CharField(max_length=18)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.READY)
    intent_hash = models.CharField(max_length=64, blank=True, default="")
    intent_anchor_tx = models.CharField(max_length=66, blank=True, default="")
    settlement_hash = models.CharField(max_length=64, blank=True, default="")
    settlement_anchor_tx = models.CharField(max_length=66, blank=True, default="")
    provider_transaction_id = models.CharField(max_length=100, blank=True, default="")
    failure_reason = models.TextField(blank=True, default="")
    initiated_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference} ({self.status})"

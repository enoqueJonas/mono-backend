"""Durable intent for a contribution anchor; the SQL commit precedes RPC.

A contribution's CONFIRMED status describes the *simulated/manual ledger*,
not a verified financial-provider payment or successful blockchain anchoring.
"""
from django.db import models

class ContributionAnchorIntent(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Awaiting anchor or retry"
        PROCESSING = "PROCESSING", "Worker has claimed the attempt"
        CONFIRMED = "CONFIRMED", "Reconciled on chain and in SQL"
        REVIEW_REQUIRED = "REVIEW_REQUIRED", "Hash or ledger mismatch"

    contribution = models.OneToOneField(
        "contributions.Contribution",
        on_delete=models.PROTECT,
        related_name="anchor_intent",
    )
    # Frozen signed representation of the contribution at insertion time.
    content_hash = models.CharField(max_length=64)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    attempt_count = models.PositiveIntegerField(default=0)
    claimed_at = models.DateTimeField(null=True, blank=True)
    next_attempt_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Earliest time that a bounded retry worker may claim this intent.",
    )
    claim_token = models.UUIDField(null=True, blank=True)
    last_error_code = models.CharField(max_length=120, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "contribution_anchor_intents"
        indexes = [models.Index(fields=["status", "created_at"], name="contr_anchor_status_idx")]

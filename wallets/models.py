"""Isolated virtual-money accounts and double-entry records. Never real funds."""
import uuid
from django.db import models


class SandboxAccount(models.Model):
    class Role(models.TextChoices):
        ISSUER = "ISSUER", "Test-money issuer"
        GROUP = "GROUP", "Xitique test account"
        MEMBER = "MEMBER", "Member test account"

    key = models.CharField(max_length=110, unique=True)
    role = models.CharField(max_length=12, choices=Role.choices)
    currency = models.CharField(max_length=3, default="MZN")
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        db_table = "sandbox_accounts"

    def __str__(self):
        return self.key


class SandboxTransfer(models.Model):
    class Purpose(models.TextChoices):
        CONTRIBUTION = "CONTRIBUTION", "Simulated contribution receipt"
        PAYOUT = "PAYOUT", "Simulated disbursement"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idempotency_key = models.CharField(max_length=130, unique=True)
    purpose = models.CharField(max_length=16, choices=Purpose.choices)
    source = models.ForeignKey(
        SandboxAccount, on_delete=models.PROTECT, related_name="sandbox_debits"
    )
    destination = models.ForeignKey(
        SandboxAccount, on_delete=models.PROTECT, related_name="sandbox_credits"
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3)
    reference = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sandbox_transfers"

    def __str__(self):
        return f"{self.purpose}:{self.reference}"


class SandboxEntry(models.Model):
    """Two entries, debit and credit, must be written in the same SQL transaction."""
    transfer = models.ForeignKey(
        SandboxTransfer, on_delete=models.PROTECT, related_name="entries"
    )
    account = models.ForeignKey(
        SandboxAccount, on_delete=models.PROTECT, related_name="sandbox_entries"
    )
    signed_amount = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = "sandbox_entries"
        constraints = [
            models.UniqueConstraint(
                fields=["transfer", "account"], name="unique_sandbox_transfer_account"
            )
        ]

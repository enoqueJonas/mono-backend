"""Explicit wallet custody and statements about externally performed transfers.

These models never custody money and do not prove provider-side settlement.
"""
from django.db import models


class ExternalWalletCustody(models.Model):
    """A group designates the member who controls its external payment account."""
    group = models.OneToOneField(
        "groups.Group", on_delete=models.PROTECT, related_name="external_wallet_custody"
    )
    custodian = models.ForeignKey(
        "groups.GroupMember", on_delete=models.PROTECT,
        related_name="external_wallet_custodies"
    )
    provider = models.CharField(max_length=20)
    wallet_number = models.CharField(max_length=32)
    designated_by = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT,
        related_name="designated_external_wallets"
    )
    designated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "external_wallet_custody"


class ExternalPaymentReport(models.Model):
    """Transfer reported by custodian and independently attested by beneficiary.

    An account-holder statement is NOT a payment-provider receipt.
    """
    class Status(models.TextChoices):
        REPORTED = "REPORTED", "Reported by custodian"
        CONFIRMED = "CONFIRMED", "Confirmed by beneficiary"
        DISPUTED = "DISPUTED", "Disputed by beneficiary"

    disbursement = models.OneToOneField(
        "disbursements.Disbursement", on_delete=models.PROTECT,
        related_name="external_payment_report"
    )
    provider = models.CharField(max_length=20)
    reference = models.CharField(max_length=120)
    reported_by = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT,
        related_name="reported_external_payments"
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.REPORTED
    )
    reported_at = models.DateTimeField(auto_now_add=True)
    confirmed_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.PROTECT,
        related_name="confirmed_external_payment_receipts"
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    disputed_at = models.DateTimeField(null=True, blank=True)
    dispute_reason = models.TextField(blank=True, default="")

    class Meta:
        db_table = "external_payment_reports"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "reference"],
                name="unique_external_provider_reference",
            )
        ]

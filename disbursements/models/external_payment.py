"""Mandate for external custody, and self-reported evidence of payment.

No fund balances or provider tokens belong in these models. Wallet identifiers
are deliberately display aliases, not secrets or authorization credentials.
"""
from django.conf import settings
from django.db import models


class TreasuryMandate(models.Model):
    """One currently designated custodian of an external account per group."""

    class Provider(models.TextChoices):
        MPESA = "MPESA", "M-Pesa"
        EMOLA = "EMOLA", "e-Mola"
        OTHER = "OTHER", "Other external payment channel"

    group = models.OneToOneField(
        "groups.Group", on_delete=models.PROTECT, related_name="treasury_mandate"
    )
    custodian = models.ForeignKey(
        "groups.GroupMember", on_delete=models.PROTECT, related_name="custody_mandates"
    )
    provider = models.CharField(max_length=12, choices=Provider.choices)
    wallet_alias = models.CharField(
        max_length=64, help_text="Masked/display-only identifier; never a password or API key."
    )
    appointed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="appointed_treasury_mandates",
    )
    appointed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "external_treasury_mandates"


class ExternalPaymentReport(models.Model):
    """A custodian's claim and the beneficiary's response, not PSP settlement."""

    class Status(models.TextChoices):
        REPORTED = "REPORTED", "Reported by custodian"
        CONFIRMED = "CONFIRMED", "Beneficiary acknowledges receipt"
        DISPUTED = "DISPUTED", "Beneficiary disputes receipt"

    disbursement = models.OneToOneField(
        "disbursements.Disbursement", on_delete=models.PROTECT,
        related_name="external_payment",
    )
    mandate = models.ForeignKey(
        TreasuryMandate, on_delete=models.PROTECT,
        related_name="payment_reports",
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="external_payments_reported",
    )
    provider = models.CharField(max_length=12, choices=TreasuryMandate.Provider.choices)
    wallet_alias = models.CharField(max_length=64)
    transfer_reference = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3)
    beneficiary_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="external_payments_received",
    )
    reported_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.REPORTED,
    )
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name="external_payments_confirmed",
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    dispute_reason = models.TextField(blank=True, default="")

    class Meta:
        db_table = "external_payment_reports"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "transfer_reference"],
                name="unique_external_provider_reference",
            ),
        ]

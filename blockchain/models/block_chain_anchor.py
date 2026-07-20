from django.db import models


class BlockchainAnchorStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    FAILED = "FAILED", "Failed"
    REPLACED = "REPLACED", "Replaced"


class BlockchainAnchor(models.Model):

    credential = models.ForeignKey(
        "credentials.Credential",
        on_delete=models.CASCADE,
        related_name="anchors",
    )

    network = models.CharField(
        max_length=50,
    )

    contract_address = models.CharField(
        max_length=42,
    )

    transaction_hash = models.CharField(
        max_length=66,
        unique=True,
    )

    block_number = models.BigIntegerField()

    wallet_address = models.CharField(
        max_length=42,
    )

    anchored_at = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=BlockchainAnchorStatus.choices,
        default=BlockchainAnchorStatus.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        indexes = [

            models.Index(
                fields=[
                    "credential",
                ]
            ),

            models.Index(
                fields=[
                    "transaction_hash",
                ]
            ),

            models.Index(
                fields=[
                    "status",
                ]
            ),
        ]

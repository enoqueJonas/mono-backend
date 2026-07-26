from django.db import models

from credentials.models import VerifiableCredential
from credentials.enums.anchor_status import AnchorStatus


class BlockchainAnchor(models.Model):

    credential = models.ForeignKey(
        VerifiableCredential,
        related_name="anchors",
        on_delete=models.CASCADE,
    )

    credential_hash = models.BinaryField(
        max_length=32,
    )

    network = models.CharField(
        max_length=30,
    )

    contract_address = models.CharField(
        max_length=42,
    )

    transaction_hash = models.CharField(
        max_length=66,
        unique=True,
    )

    block_hash = models.CharField(
        max_length=66,
    )

    block_number = models.PositiveBigIntegerField()

    wallet_address = models.CharField(
        max_length=42,
    )

    gas_used = models.PositiveBigIntegerField()

    effective_gas_price = models.PositiveBigIntegerField()

    status = models.CharField(
        max_length=20,
        choices=AnchorStatus.choices,
        default=AnchorStatus.CONFIRMED,
    )

    anchored_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-anchored_at",
        ]

        indexes = [
            models.Index(
                fields=["credential"],
            ),
            models.Index(
                fields=["credential_hash"],
            ),
            models.Index(
                fields=["transaction_hash"],
            ),
            models.Index(
                fields=["status"],
            ),
        ]

    def __str__(self):
        return (
            # f"{self.credential_id} "
            f"{self.status}"
        )

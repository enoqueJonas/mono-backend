from django.db import models


class BlockchainAnchorStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    FAILED = "FAILED", "Failed"
    REPLACED = "REPLACED", "Replaced"


class BlockchainAnchorType(models.TextChoices):
    CREDENTIAL = "CREDENTIAL", "Credential"
    GROUP_SETTINGS = (
        "GROUP_SETTINGS",
        "Group Settings",
    )
    CONTRIBUTION = (
        "CONTRIBUTION",
        "Contribution",
    )
    DISBURSEMENT = (
        "DISBURSEMENT",
        "Disbursement",
    )


class BlockchainAnchor(models.Model):

    anchor_type = models.CharField(
        max_length=30,
        choices=BlockchainAnchorType.choices,
    )

    content_hash = models.CharField(
        max_length=64,
    )

    credential = models.ForeignKey(
        "credentials.VerifiableCredential",
        on_delete=models.PROTECT,
        related_name="anchors",
        null=True,
        blank=True,
    )

    group_settings = models.ForeignKey(
        "groups.GroupSettings",
        on_delete=models.PROTECT,
        related_name="anchors",
        null=True,
        blank=True,
    )

    contribution = models.ForeignKey(
        "contributions.Contribution",
        on_delete=models.PROTECT,
        related_name="anchors",
        null=True,
        blank=True,
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
                fields=["anchor_type"],
            ),
            models.Index(
                fields=["content_hash"],
            ),
            models.Index(
                fields=["credential"],
            ),
            models.Index(
                fields=["group_settings"],
            ),
            models.Index(
                fields=["contribution"],
            ),
            models.Index(
                fields=["transaction_hash"],
            ),
            models.Index(
                fields=["status"],
            ),
        ]

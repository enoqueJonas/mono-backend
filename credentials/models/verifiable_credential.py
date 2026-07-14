from django.db import models

from core.models import BaseModel


class VerifiableCredential(BaseModel):
    class CredentialType(models.TextChoices):
        CONTRIBUTION_HISTORY = (
            "CONTRIBUTION_HISTORY",
            "Contribution History",
        )

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        REVOKED = "REVOKED", "Revoked"

    group_member = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="verifiable_credentials",
    )

    issued_by = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="issued_credentials",
    )

    issuer_did = models.ForeignKey(
        "identity.GroupDID",
        on_delete=models.PROTECT,
        related_name="issued_credentials",
    )

    holder_did = models.ForeignKey(
        "identity.UserDID",
        on_delete=models.PROTECT,
        related_name="credentials",
    )

    credential_type = models.CharField(
        max_length=40,
        choices=CredentialType.choices,
        default=CredentialType.CONTRIBUTION_HISTORY,
    )

    period_start = models.DateField()
    period_end = models.DateField()

    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
    )

    credential_document = models.JSONField()

    credential_hash = models.CharField(
        max_length=64,
        unique=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    revocation_reason = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "verifiable_credentials"
        ordering = ["-valid_from"]
        indexes = [
            models.Index(
                fields=[
                    "group_member",
                    "credential_type",
                    "status",
                ],
                name="vc_member_type_status_idx",
            ),
            models.Index(
                fields=["credential_hash"],
                name="vc_hash_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(period_end__gte=models.F("period_start")),
                name="vc_period_end_after_start",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(valid_until__isnull=True)
                    | models.Q(valid_until__gt=models.F("valid_from"))
                ),
                name="vc_valid_until_after_valid_from",
            ),
            models.UniqueConstraint(
                fields=[
                    "group_member",
                    "credential_type",
                    "period_start",
                    "period_end",
                ],
                condition=models.Q(status="ACTIVE"),
                name="unique_active_vc_member_period",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.credential_type} - "
            f"{self.group_member} - "
            f"{self.period_start}/{self.period_end}"
        )

    @property
    def credential_id(self) -> str:
        return f"urn:uuid:{self.id}"

    @property
    def is_expired(self) -> bool:
        if self.valid_until is None:
            return False

        from django.utils import timezone

        return timezone.now() >= self.valid_until

    @property
    def effective_status(self) -> str:
        if self.status == self.Status.REVOKED:
            return "REVOKED"

        if self.is_expired:
            return "EXPIRED"

        return "ACTIVE"

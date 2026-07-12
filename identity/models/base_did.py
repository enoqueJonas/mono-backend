from django.db import models

from core.models import BaseModel


class BaseDID(BaseModel):
    class Method(models.TextChoices):
        KEY = "KEY", "did:key"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        REVOKED = "REVOKED", "Revoked"

    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.KEY,
    )

    did = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    public_key_multibase = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    encrypted_private_key = models.TextField(
        editable=False,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.did

    @property
    def verification_method_id(self) -> str:
        return f"{self.did}#{self.public_key_multibase}"

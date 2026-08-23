from django.db import models

from core.models import BaseModel


class Group(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CLOSED = "CLOSED", "Closed"
        ARCHIVED = "ARCHIVED", "Archived"

    name = models.CharField(
        max_length=120,
    )

    description = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        db_table = "groups"

    def __str__(self) -> str:
        return self.name

    @property
    def current_settings(self):
        return self.settings_versions.get(
            is_active=True,
        )

    @property
    def current_settings_version(self) -> int:
        return self.current_settings.version

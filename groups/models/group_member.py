from django.conf import settings
from django.db import models

from core.models import BaseModel


class GroupMember(BaseModel):
    class Role(models.TextChoices):
        MANAGER = "MANAGER", "Manager"
        TREASURER = "TREASURER", "Treasurer"
        MEMBER = "MEMBER", "Member"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"
        LEFT = "LEFT", "Left"

    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="group_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "group_members"
        constraints = [
            models.UniqueConstraint(
                fields=["group", "user"],
                name="unique_user_per_group",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.group} ({self.role})"

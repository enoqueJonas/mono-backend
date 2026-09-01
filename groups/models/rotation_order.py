from django.db import models

from core.models import BaseModel


class RotationOrder(BaseModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CURRENT = "CURRENT", "Current"
        COMPLETED = "COMPLETED", "Completed"
        SKIPPED = "SKIPPED", "Skipped"

    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.PROTECT,
        related_name="rotation_orders",
    )

    member = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="rotation_orders",
    )

    group_settings = models.ForeignKey(
        "groups.GroupSettings",
        on_delete=models.PROTECT,
        related_name="rotation_orders",
    )

    contribution_period = models.DateField()

    cycle_number = models.PositiveIntegerField()

    position = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        db_table = "rotation_orders"
        ordering = [
            "cycle_number",
            "position",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "group",
                    "cycle_number",
                    "position",
                ],
                name="unique_rotation_position_per_cycle",
            ),
            models.UniqueConstraint(
                fields=[
                    "group",
                    "cycle_number",
                    "member",
                ],
                name="unique_member_per_rotation_cycle",
            ),
            models.UniqueConstraint(
                fields=[
                    "group",
                    "cycle_number",
                ],
                condition=models.Q(
                    status="CURRENT",
                ),
                name="unique_current_rotation",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "group",
                    "cycle_number",
                    "status",
                ],
                name="rot_grp_cycle_stat_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.group.name} - "
            f"Cycle {self.cycle_number} - "
            f"Position {self.position}"
        )

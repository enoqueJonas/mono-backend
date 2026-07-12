from django.db import models

from .base_did import BaseDID


class GroupDID(BaseDID):
    group = models.OneToOneField(
        "groups.Group",
        on_delete=models.PROTECT,
        related_name="decentralized_identity",
    )

    class Meta:
        db_table = "group_dids"

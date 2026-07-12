from django.conf import settings
from django.db import models

from .base_did import BaseDID


class UserDID(BaseDID):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="decentralized_identity",
    )

    class Meta:
        db_table = "user_dids"

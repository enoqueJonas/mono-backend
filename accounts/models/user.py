from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from accounts.utils.phone import normalize_mz_phone
from ..managers import UserManager
from ...core.models.base import BaseModel


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=16, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if self.phone_number:
            try:
                self.phone_number = normalize_mz_phone(self.phone_number)
            except ValueError:
                pass
        super().save(*args, **kwargs)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.phone_number

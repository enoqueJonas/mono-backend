from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models.user import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    ordering = ("phone_number",)

    list_display = (
        "phone_number",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "phone_number",
        "first_name",
        "last_name",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "phone_number",
                    "password",
                )
            },
        ),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

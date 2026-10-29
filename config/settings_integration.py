"""Integration-test settings: PostgreSQL and a separate ephemeral Ganache RPC node.

These credentials belong exclusively to the disposable GitHub Actions service.
No production database or blockchain keys are accessed.
"""
from .settings_test import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mono_integration",
        "USER": "mono_test",
        "PASSWORD": "mono_test_password",
        "HOST": "127.0.0.1",
        "PORT": "5432",
        "TEST": {"NAME": "test_mono_integration"},
    }
}

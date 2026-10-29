"""Safe test-only defaults: never import production secrets to run the suite."""
import os
from base64 import urlsafe_b64encode

# The production settings import reads these values at module import time.
# Supply safe dummy values only if no local developer test config was provided.
_TEST_ENV = {
    "SECRET_KEY": "test-only-key-not-for-production",
    "DB_NAME": "mono_test",
    "DB_USER": "mono_test",
    "DB_PASSWORD": "mono_test",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "BLOCKCHAIN_PRIVATE_KEY": "0x" + "0" * 63 + "1",
    "BLOCKCHAIN_ACCOUNT_ADDRESS": "0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf",
    "DID_KEY_ENCRYPTION_KEY": urlsafe_b64encode(bytes(range(32))).decode("ascii"),
}
for name, value in _TEST_ENV.items():
    os.environ.setdefault(name, value)

from .settings import *  # noqa: E402,F401,F403

# Isolated default database for Django unit/integration-style tests.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

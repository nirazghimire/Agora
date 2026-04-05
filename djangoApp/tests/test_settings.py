"""
Test-specific Django settings.
Inherits everything from the main config and overrides the database
to use an in-memory SQLite backend so tests don't touch PostgreSQL.
"""
import os

# Base settings currently read PostgreSQL env vars at import time.
# Seed harmless placeholders so tests can import config.settings reliably.
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")

from config.settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Speed up password hashing during tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

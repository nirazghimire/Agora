"""
Test-specific Django settings.
Inherits everything from the main config and overrides the database
to use an in-memory SQLite backend so tests don't touch PostgreSQL.
"""
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

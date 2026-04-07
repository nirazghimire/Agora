"""
Test-specific Django settings.
Inherits everything from the main config and overrides the database
to use an in-memory SQLite backend so tests don't touch PostgreSQL.
"""
import os

os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")

"""
the import below was causing problem in the CI workflow as the runner tried to use posgres configurations ; so the base settings of setting env variables using os above overrides the config.settings configurations for postgres ; 
there were 2 options here, I could have either imported all of the other except for postgres configurations but that would just create a lot of import lines which would not be suitable ; instead just override the env varialbes first and then import all and hence this would not create the conflict ; 
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

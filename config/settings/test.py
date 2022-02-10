"""With these settings, tests run faster."""
import os

os.environ["DJANGO_READ_DOT_ENV_FILE"] = "true"  # noqa

from .base import *  # noqa
from .base import env  # noqa

# GENERAL
# ------------------------------------------------------------------------------
ENV = "test"

# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = TEMPLATE_DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="ZCpca087MiMmGi9zgkGyQG01G7GjNTakVXOAvcusVFDxedMVTy77LzRqz5Smhwfa",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Turn off whitenoise for test runs
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
    "postcodes": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "postcodecache",
        "TIMEOUT": 2620800,  # cache postcodes for ~ a month
        "OPTIONS": {
            "MAX_ENTRIES": 10000,
        },
    },
}

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # noqa F405
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = "localhost"
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025

# Fake URLs to avoid real API calls
# ------------------------------------------------------------------------------
AUTH0_DOMAIN = "example.auth.carbon.coop"
AUTH0_API_DOMAIN = "example.api.auth.carbon.coop"
SLACK_POST_SMART_METERS_URL = ""
SLACK_POST_MEMBERSHIP_URL = ""

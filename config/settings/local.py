import os

import coloredlogs

os.environ["DJANGO_READ_DOT_ENV_FILE"] = "true"  # noqa

from .base import *  # noqa
from .base import env  # noqa


# GENERAL
# ------------------------------------------------------------------------------
ENV = "local"

# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = TEMPLATE_DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="IpL8UcVq7UwgCB714NVbW7B7UqAGrLmTDbwTWNOYftQlqgHQAIMS95fZUK41b2Ek",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "*"]

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

# LOGGING
# ------------------------------------------------------------------------------
coloredlogs.install()
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "coloredlogs": {
            "()": "coloredlogs.ColoredFormatter",
            "fmt": "[%(asctime)s] %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "coloredlogs",
        },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "DEBUG"},
        "faker": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "rq_scheduler": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "rq.worker": {"handlers": ["console"], "level": "INFO"},
    },
}

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # noqa F405

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = "localhost"
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025


# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ["debug_toolbar"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]


# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions"]  # noqa F405

import base64
import json
import os
from urllib.parse import urlparse

from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# Platform.sh allows us to set variables, but they are set in a single
# environment variable which is a JSON dict.  To make this stable across
# environments expand those variables into environment variables:

platform_variables = os.getenv("PLATFORM_VARIABLES")
if platform_variables:
    platform_variables = json.loads(
        base64.b64decode(platform_variables).decode("utf-8")
    )
    for (key, value) in platform_variables.items():
        os.environ[key] = value


# Import prefixed settings from the platform environemnt.
PSH_ENV_PREFIX = "PROSPECTOR"


def psh_env(name, default=None, prefix=PSH_ENV_PREFIX):
    return os.getenv("%s_%s" % (prefix, name), default)


if psh_env("DEBUG", False):
    DEBUG = True
    INSTALLED_APPS += ("django_extensions",)  # noqa F405

if psh_env("LOCALHOST", False):
    ALLOWED_HOSTS.append("localhost")
    ALLOWED_HOSTS.append("127.0.0.1")

# Logging
# ------------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "": {"handlers": ["console", "mail_admins"], "level": "DEBUG"},
    },
}

log_file = psh_env("LOG_FILE")
if log_file:
    LOGGING["handlers"]["file"] = {  # noqa F405
        "level": psh_env("LOG_LEVEL", "INFO"),
        "class": "logging.FileHandler",
        "filename": log_file,
    }
    LOGGING["loggers"]["django"]["handlers"].append("file")  # noqa F405

#
# Import some PLATFORM_* Platform.sh settings from the environment.
#

app_dir = os.getenv("PLATFORM_APP_DIR")
if app_dir:
    STATIC_ROOT = os.path.join(app_dir, "static")

entropy = os.getenv("PLATFORM_PROJECT_ENTROPY")
if entropy:
    SECRET_KEY = entropy

routes = os.getenv("PLATFORM_ROUTES")
if routes:
    routes = json.loads(base64.b64decode(routes).decode("utf-8"))
    app_name = os.getenv("PLATFORM_APPLICATION_NAME")
    for url, route in routes.items():
        host = urlparse(url).netloc
        if (
            host not in ALLOWED_HOSTS
            and route["type"] == "upstream"
            and route["upstream"] == app_name
        ):
            ALLOWED_HOSTS.append(host)

relationships = os.getenv("PLATFORM_RELATIONSHIPS")
if relationships:
    relationships = json.loads(base64.b64decode(relationships).decode("utf-8"))
    db_settings = relationships["database"][0]
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": db_settings["path"],
            "USER": db_settings["username"],
            "PASSWORD": db_settings["password"],
            "HOST": db_settings["host"],
            "PORT": db_settings["port"],
        },
    }

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

# environment = os.getenv('PLATFORM_BRANCH')

smtp_host = os.getenv("PLATFORM_SMTP_HOST")
if smtp_host:
    EMAIL_HOST = smtp_host

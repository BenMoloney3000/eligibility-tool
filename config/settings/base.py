"""Base settings to build other settings files upon."""
import logging

import environ
#import sentry_sdk
#from sentry_sdk.integrations.django import DjangoIntegration
#from sentry_sdk.integrations.logging import LoggingIntegration
#from sentry_sdk.integrations.redis import RedisIntegration
#from sentry_sdk.integrations.rq import RqIntegration
#from ssm_parameter_store import EC2ParameterStore

ROOT_DIR = (
    environ.Path(__file__) - 3
)  # (prospector/config/settings/base.py - 3 = prospector/)
SRC_DIR = ROOT_DIR.path("prospector")

env = environ.Env()

# AWS setup
# ------------------------------------------------------------------------------

# Get parameters and populate os.environ, if desired
AWS_PARAM_STORE = env("AWS_PARAM_STORE", default="")
if AWS_PARAM_STORE != "":
    store = EC2ParameterStore()
    params = store.get_parameters_by_path(f"/{AWS_PARAM_STORE}/", strip_path=True)
    EC2ParameterStore.set_env(params)

# Load entries from the .env file, if desired
READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))


# GENERAL
# ------------------------------------------------------------------------------
ENV = env("ENV", default="production")  # can also be 'staging'

# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = TEMPLATE_DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Europe/London"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-gb"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# The externally-accessible URL of the site.
SITE_URL = env.str("SITE_URL", "")

# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Sentry
## ------------------------------------------------------------------------------
#SENTRY_DSN = env("SENTRY_DSN", default="")
#SENTRY_RELEASE = ""
#if SENTRY_DSN:
#    SENTRY_LOG_LEVEL = env.int("DJANGO_SENTRY_LOG_LEVEL", logging.INFO)
#    RQ_SENTRY_DSN = env("SENTRY_DSN")
#
#    sentry_logging = LoggingIntegration(
#        level=SENTRY_LOG_LEVEL,  # Capture info and above as breadcrumbs
#        event_level=logging.ERROR,  # Send events from Error messages
#    )

    # This commit ID is substituted in during the Docker build process
#    COMMIT_ID = "@@__COMMIT_ID__@@"
#    if COMMIT_ID != ("@@" + "__COMMIT_ID__" + "@@"):
#        SENTRY_RELEASE = f"prospector@{COMMIT_ID}"
 #   else:
 #       SENTRY_RELEASE = None
#
 #   sentry_sdk.init(
 #       dsn=SENTRY_DSN,
 #       integrations=[
#         #   sentry_logging,
        #    DjangoIntegration(),
       #     RqIntegration(),
     ##       RedisIntegration(),
    #    ],
   #     environment=ENV,
  #      release=SENTRY_RELEASE,
 #   )
#
#    # DisallowedHost errors are basically spam
 #   from sentry_sdk.integrations.logging import ignore_logger
#
#    ignore_logger("django.security.DisallowedHost")


# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

if ENV != "offline":
    DATABASES = {"default": env.db("DATABASE_URL", "")}
    DATABASES["default"]["ATOMIC_REQUESTS"] = True
    DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.humanize",  # Handy template tags
    "django.contrib.admin",
    "django.contrib.admindocs",
]
THIRD_PARTY_APPS = [
    "django_rq",
    "waffle",
    "sass_processor",
    "crispy_forms",
    "crispy_forms_gds",
    "import_export",
    "django_celery_results",
    "django_celery_beat",
]
LOCAL_APPS = [
    "prospector",
    "prospector.apps.questionnaire",
    "prospector.apps.users",
    "prospector.apps.crm",
    "prospector.dataformats",
    "prospector.apps.parity",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "/login"
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "/"
# https://docs.djangoproject.com/en/dev/ref/settings/#logout-redirect-url
LOGOUT_REDIRECT_URL = "/"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "prospector.middleware.healthcheck.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "waffle.middleware.WaffleMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR("staticfiles"))
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(SRC_DIR.path("static"))]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "sass_processor.finders.CssFinder",
]

# We're using whitenoise for STATICFILES_STORAGE in production, so configure
# a file based storage backend for the output of sass_processor:
SASS_PROCESSOR_STORAGE = "django.contrib.staticfiles.storage.FileSystemStorage"
SASS_PROCESSOR_STORAGE_OPTIONS = {
    "location": STATIC_ROOT,
    "base_url": STATIC_URL,
}

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(ROOT_DIR("media"))
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(SRC_DIR.path("templates"))],
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            "debug": DEBUG,
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"


if ENV == "offline":
    RQ_QUEUES = {}
else:
    RQ_QUEUES = {
        "default": {
            "HOST": env.str("REDIS_HOST"),
            "PORT": env.int("REDIS_PORT", default=6379),
            "PASSWORD": env.str("REDIS_PASSWORD", default=""),
            "SSL": env.bool("REDIS_SSL", default=False),
            "DB": env.int("REDIS_DB", default=0),
            "DEFAULT_TIMEOUT": 360,
        }
    }
    RQ_SHOW_ADMIN_LINK = True

EPC_API_KEY = env.str("EPC_API_KEY", default="")
POSTCODER = env.str("POSTCODER", default="DATA8")
IDEAL_POSTCODES_API_KEY = env.str("IDEAL_POSTCODES_API_KEY", default="")
DATA8_API_KEY = env.str("DATA8_API_KEY", default="")
DATA8_LICENSE = env.str("DATA8_LICENSE", default="FreeTrial")
MAIL_FROM = env.str("EMAIL_FROM", default="futurefit@plymouthenergycommunity.com")
DEFAULT_FROM_EMAIL = MAIL_FROM
SERVER_EMAIL = DEFAULT_FROM_EMAIL

CRM_API = {
    "TENANT": env.str("CRM_API_TENANT", default=""),
    "RESOURCE": env.str("CRM_API_RESOURCE", default=""),
    "CLIENT_ID": env.str("CRM_API_CLIENT_ID", default=""),
    "CLIENT_SECRET": env.str("CRM_API_CLIENT_SECRET", default=""),
}

CRISPY_ALLOWED_TEMPLATE_PACKS = ["gds"]
CRISPY_TEMPLATE_PACK = "gds"

# CELERY SETTINGS
# https://docs.celeryproject.org/en/stable/userguide/configuration.html
# loaded in main/celery.py with namespace='CELERY'
CELERY_ALWAYS_EAGER = (
    False  # set True for debug/testing (tasks will block and run synchronously).
)


CELERY_BROKER_URL = "redis://{0}:{1}/0".format(
    env.str("REDIS_HOST"), env.int("REDIS_PORT", default=6379)
)
CELERY_BROKER_USE_SSL = env.bool("REDIS_SSL", default=False)
CELERY_RESULT_BACKEND = "django-db"
CELERY_SINGLETON_BACKEND_URL = CELERY_BROKER_URL
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}  # 1 hour.

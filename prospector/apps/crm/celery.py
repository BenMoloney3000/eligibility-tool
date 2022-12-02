import os

from celery import Celery
from celery.signals import worker_ready
from celery.utils.log import get_task_logger
from celery_singleton import clear_locks

# from celery.schedules import crontab

logger = get_task_logger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")


# TODO:
# https://github.com/celery/django-celery-results/issues/20
# import django; django.setup()

app = Celery("proj")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
app.conf.beat_schedule = {}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@worker_ready.connect
def unlock_all(**kwargs):
    clear_locks(app)


@app.task(bind=True)
def debug_task(self):
    msg = f"Request: {self.request!r}"
    print(msg)
    logger.info(msg)
    return msg

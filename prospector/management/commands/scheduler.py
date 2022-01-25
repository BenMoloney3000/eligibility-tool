import logging
from importlib import import_module

import django_rq
from django.conf import settings
from django_rq.management.commands import rqscheduler

scheduler = django_rq.get_scheduler()
logger = logging.getLogger(__name__)


def clear_jobs():
    """
    Clear all jobs in the scheduler.

    We do this because otherwise they stick around, and when we deploy a new version
    we generally want to 'forget' the old jobs.
    """
    for job in scheduler.get_jobs():
        logger.debug("Deleting scheduled job %s", job)
        job.delete()


def register_jobs():
    """Run through all tasks files, execute the 'schedule' function."""

    for app_name in settings.LOCAL_APPS:
        try:
            module_ = import_module(".tasks", app_name)
        except ImportError:
            continue

        if hasattr(module_, "schedule"):
            logger.debug(f"Scheduling jobs for {module_.__package__}")
            module_.schedule(scheduler)


class Command(rqscheduler.Command):
    def handle(self, *args, **kwargs):
        clear_jobs()
        register_jobs()
        super(Command, self).handle(*args, **kwargs)

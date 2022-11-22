from django_rq import job

from . import models


def schedule(scheduler):
    # Run the cleanup every hour)
    scheduler.cron("30 * * * *", func=cleanup)


@job
def cleanup():
    """Clean up abandoned and incomplete responses."""

    # Anything that didn't accept the terms can go straight away with no ill effects
    models.Answers.objects.filter(terms_accepted_at__isnull=True).delete()

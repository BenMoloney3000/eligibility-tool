from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # See https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/

    help = "Does nothing; a placeholder and template for later"

    def handle(self, *args, **options):
        pass

from django.utils import timezone
from factory import Faker
from factory.django import DjangoModelFactory

from prospector.apps.questionnaire import models


class AnswersFactory(DjangoModelFactory):
    class Meta:
        model = models.Answers

    terms_accepted_at = timezone.now()
    email = Faker("email")
    property_postcode = Faker("postcode", locale="en-GB")

import datetime

from django.utils import timezone
from factory import Faker
from factory.django import DjangoModelFactory

from prospector.apis import epc
from prospector.apps.questionnaire import models


class AnswersFactory(DjangoModelFactory):
    class Meta:
        model = models.Answers

    terms_accepted_at = timezone.now()
    email = Faker("email")
    postcode = Faker("postcode", locale="en-GB")


FAKE_EPC = epc.EPCData(
    "19747490192737",
    datetime.date(2020, 10, 10),
    "20 Testington Pastures",
    "Eggborough",
    "Royal Leamington Spa",
    "1234",
    "Bungalow",
    "Semi-Detached",
    "England and Wales: 1976-1982",
    "Cavity wall, filled cavity",
    "To unheated space, limited insulation (assumed)",
    "Flat, no insulation (assumed)",
    "Boiler and radiators, electric",
    "From main system",
    2302,  # DHS_FLAT_RATE_PROGRAMMER
    66,
)

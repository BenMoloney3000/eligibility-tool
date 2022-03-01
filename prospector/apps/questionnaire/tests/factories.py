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
    property_postcode = Faker("postcode", locale="en-GB")


FAKE_EPC = epc.EPCData(
    "19747490192737",  # id
    datetime.date(2020, 10, 10),  # date
    "20 Testington Pastures",  # address_1
    "Eggborough",  # address_2
    "Royal Leamington Spa",  # address_3
    "1234",  # uprn
    "Bungalow",  # property_type
    "Semi-Detached",  # built_form
    "England and Wales: 1976-1982",  # construction_age_band
    "Cavity wall, filled cavity",  # walls_description
    4,  # walls_rating
    "To unheated space, limited insulation (assumed)",  # floor_description
    3,  # floor rating
    "Flat, no insulation (assumed)",  # roof_description
    2,  # roof rating
    "Boiler and radiators, electric",  # mainheat_description
    "From main system",  # hotwater_description
    2302,  # main_heating_controls  (DHS_FLAT_RATE_PROGRAMMER)
    66,  # current_energy_rating
)

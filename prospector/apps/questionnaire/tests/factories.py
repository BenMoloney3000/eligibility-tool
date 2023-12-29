from django.utils import timezone
from factory import Faker
from factory.django import DjangoModelFactory

from prospector.apis import parity
from prospector.apps.questionnaire import models


class AnswersFactory(DjangoModelFactory):
    class Meta:
        model = models.Answers

    terms_accepted_at = timezone.now()
    email = Faker("email")
    property_postcode = Faker("postcode", locale="en-GB")


FAKE_PARITY = parity.ParityData(
    "19747490192737",  # id
    "39771676",  # org_ref
    "https://crohm.parityprojects.com/Address/Details/12345678",  # address_link
    "https://maps.google.com/maps?q=9 LYNX LANE PL9 8FF",  # googlemaps
    "20 Testington Pastures",  # address_1
    "Eggborough",  # address_2
    "Royal Leamington Spa",  # address_3
    "PL9 8FF",  # postcode
    81.20,  # sap_score
    "B",  # sap_band
    84,  # lodged_epc_score
    "B",  # lodged_epc_band
    2.5,  # tco2_current
    "£622",  # realistic_fuel_bill
    "House",  # type
    "Detached",  # attachement
    "2012 onwards",  # construction_years
    6,  # heated_rooms
    "Cavity",  # wall_construction
    "As built",  # wall_insulation
    "Solid",  # floor_construction
    "As built",  # floor_insulation
    "Pitched - loft access",  # roof_construction
    "Unknown",  # roof_insulation
    "Triple",  # glazing
    "Boilers",  # heating
    "C",  # boiler_efficiency
    "Mains gas - not community",  # main_fuel
    "Top spec",  # control_adequacy
    "Plymouth",  # local_authority
    "Plymstock Dunstone",  # ward
    "E14000950",  # parliamentary_constituency
    "South West",  # region_name
    "Unknown",  # tenure
    "10093900740",  # uprn
    50.36647797,  # lat_coordinate
    -4.05325174,  # long_coordinate
    "E01015131",  # lower_super_output_area_code
    10,  # multiple_deprivation_index
)

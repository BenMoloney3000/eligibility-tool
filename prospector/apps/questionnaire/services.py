import json
import logging

from django.conf import settings
from django.utils import timezone

from . import models
from prospector.apps.crm.tasks import crm_create
from prospector.apps.parity.models import ParityData
from ...apis.crm import crm
from ...apis.parity import parity_api_fetch

logger = logging.getLogger(__name__)


def prepopulate_from_parity(answers: models.Answers) -> models.Answers:
    parity_object = None
    if answers.uprn:
        parity_object = parity_api_fetch.get_for_uprn(answers.uprn)
    if parity_object is None:
        parity_object = ParityData.objects.filter(
            address_1=answers.property_address_1,
            address_2=answers.property_address_2,
            postcode=answers.property_postcode,
        ).first()

    if parity_object:
        """Parse Parity contents to populate initial values for property energy data."""
        po = parity_object

        answers.property_type = po.type
        answers.property_attachment = po.attachment
        answers.property_construction_years = po.construction_years
        answers.wall_construction = po.wall_construction
        answers.walls_insulation = po.wall_insulation
        answers.roof_construction = po.roof_construction
        answers.roof_insulation = po.roof_insulation
        answers.floor_construction = po.floor_construction
        answers.floor_insulation = po.floor_insulation
        answers.heating = po.heating
        answers.main_fuel = po.main_fuel
        answers.sap_score = int(po.sap_score)
        answers.sap_band = po.sap_band
        answers.lodged_epc_score = po.lodged_epc_score
        answers.lodged_epc_band = po.lodged_epc_band
        answers.glazing = po.glazing
        answers.boiler_efficiency = po.boiler_efficiency
        answers.heating_controls_detail = po.heating_controls_detail
        answers.heated_rooms = po.heated_rooms
        answers.t_co2_current = po.tco2_current
        answers.realistic_fuel_bill = po.realistic_fuel_bill
        answers.multiple_deprivation_index = po.multiple_deprivation_index
        answers.income_decile = po.income_decile
        answers.parity_object_id = str(po.id)

        return answers

    else:
        return answers


def close_questionnaire(answers: models.Answers):
    """Set the questionnaire as completed.

    Prevents any part of it being edited through the questionnaire views.
    """

    answers.completed_at = timezone.now()
    answers.save()

    try:
        if settings.ENV in ["local", "stage"]:
            logger.warning('Local/stage environment - will not push data to CRM. Logging payload instead.')
            logger.info(json.dumps(crm.map_crm(answers)))
        else:
            crm_create.delay(str(answers.uuid))
    except Exception as e:
        logger.error("close_questionnaire_func exception %s", str(e))

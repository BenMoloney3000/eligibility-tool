import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from . import models
from prospector.apps.crm.tasks import crm_create
from prospector.apps.parity.models import ParityData

logger = logging.getLogger(__name__)


def prepopulate_from_parity(answers: models.Answers) -> models.Answers:
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
        answers.wall_insulation = po.wall_insulation
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
        answers.controls_adequacy = po.controls_adequacy
        answers.heated_rooms = po.heated_rooms
        answers.t_co2_current = po.tco2_current
        answers.realistic_fuel_bill = po.realistic_fuel_bill
        answers.uprn = po.uprn
        answers.multiple_deprivation_index = po.multiple_deprivation_index
        answers.council_tax_band = po.tax_band

        return answers

    else:
        return answers


def close_questionnaire(answers: models.Answers):
    """Set the questionnaire as completed.

    Prevents any part of it being edited through the questionnaire views. Also
    sends an acknowledment email.
    """

    answers.completed_at = timezone.now()
    answers.save()

    try:
        crm_create.delay(str(answers.uuid))

        context = {
            "full_name": f"{answers.first_name} {answers.last_name}",
            "postcode": answers.property_postcode,
            "consented_callback": answers.consented_callback,
            "consented_future_schemes": answers.consented_future_schemes,
            "short_uid": answers.short_uid,
        }
        message_body_txt = render_to_string("emails/acknowledgement.txt", context)
        message_body_html = render_to_string("emails/acknowledgement.html", context)

        message = EmailMultiAlternatives(
            subject="Thanks for completing the PEC Funding Eligibility Checker",
            body=message_body_txt,
            from_email=settings.MAIL_FROM,
            to=[answers.email],
        )
        message.attach_alternative(message_body_html, "text/html")
        message.send()
    except Exception as e:
        logger.error("close_questionnaire_func exception %s", str(e))

import logging
import re
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from . import enums
from . import models
from prospector.apis.epc import EPCData


logger = logging.getLogger(__name__)


def prepopulate_from_epc(
    answers: models.Answers, selected_epc: EPCData
) -> models.Answers:
    """Parse EPC contents to populate initial values for property energy data."""

    answers.property_type_orig = _detect_property_type(selected_epc) or ""
    answers.property_form_orig = _detect_property_form(selected_epc) or ""
    answers.property_age_band_orig = _detect_property_age(selected_epc) or None
    answers.wall_type_orig = _detect_wall_type(selected_epc) or ""
    answers.walls_insulated_orig = _detect_walls_insulated(selected_epc)
    answers.suspended_floor_orig = _detect_suspended_floor(selected_epc)
    answers.suspended_floor_insulated_orig = _detect_suspended_floor_insulation(
        selected_epc
    )
    answers.unheated_loft_orig = _detect_unheated_loft(selected_epc)
    answers.room_in_roof_orig = _detect_room_in_roof(selected_epc)
    answers.rir_insulated_orig = _detect_rir_insulated(selected_epc)
    answers.roof_space_insulated_orig = _detect_roof_insulated(selected_epc)
    answers.flat_roof_orig = _detect_flat_roof(selected_epc)
    answers.gas_boiler_present_orig = _detect_gas_boiler(selected_epc)
    answers.other_heating_present_orig = _detect_other_ch(selected_epc)
    answers.on_mains_gas_orig = _detect_mains_gas(selected_epc)
    answers.heat_pump_present_orig = _detect_heat_pump(selected_epc)
    answers.other_heating_fuel_orig = _detect_other_ch_fuel(selected_epc) or ""
    answers.storage_heaters_present_orig = _detect_storage_heaters(selected_epc)
    answers.hhrshs_present_orig = _detect_hhrshs(selected_epc)
    answers.electric_radiators_present_orig = _detect_electric_radiators(selected_epc)
    answers.trvs_present_orig = _detect_trvs(selected_epc)
    answers.room_thermostat_orig = _detect_room_thermostat(selected_epc)
    answers.ch_timer_orig = _detect_timer(selected_epc)
    answers.programmable_thermostat_orig = _detect_programmable_thermostat(selected_epc)
    answers.sap_rating = int(selected_epc.current_energy_rating)
    answers.has_solar_pv_orig = (
        bool(int(selected_epc.photo_supply))
        if isinstance(selected_epc.photo_supply, int)
        else None
    )

    return answers


def depopulate_orig_fields(answers: models.Answers) -> models.Answers:
    """Clear all the inferred data fields."""

    answers.property_type_orig = ""
    answers.property_form_orig = ""
    answers.property_age_band_orig = None
    answers.wall_type_orig = ""
    answers.walls_insulated_orig = None
    answers.suspended_floor_orig = None
    answers.suspended_floor_insulated_orig = None
    answers.unheated_loft_orig = None
    answers.room_in_roof_orig = None
    answers.rir_insulated_orig = None
    answers.roof_space_insulated_orig = None
    answers.flat_roof_orig = None
    answers.gas_boiler_present_orig = None
    answers.other_heating_present_orig = None
    answers.on_mains_gas_orig = None
    answers.heat_pump_present_orig = None
    answers.other_heating_fuel_orig = ""
    answers.storage_heaters_present_orig = None
    answers.hhrshs_present_orig = None
    answers.electric_radiators_present_orig = None
    answers.trvs_present_orig = None
    answers.room_thermostat_orig = None
    answers.ch_timer_orig = None
    answers.programmable_thermostat_orig = None
    answers.sap_rating = None
    answers.has_solar_pv_orig = None

    return answers


"""
The following functions all attempt to interrogate the contents of the EPC to
provide "best guess" answers to the various questions that the user is
invited to agree with or correct. Where we really can't tell it's fine to
return None which means that the user is just asked with no "we think it's this"
prompt.
"""


def _detect_property_type(epc: EPCData) -> Optional[enums.PropertyType]:
    p_type = epc.property_type.upper()

    if p_type in ["FLAT", "HOUSE", "BUNGALOW", "PARK HOME"]:
        return enums.PropertyType(p_type.replace(" ", "_"))
    elif p_type == "MAISONNETTE":
        return enums.PropertyType.FLAT


def _detect_property_form(epc: EPCData) -> Optional[enums.PropertyForm]:
    p_form = epc.built_form.upper().replace("-", " ")

    # Catch "Enclosed End/Mid-Terrace"
    p_form = p_form.replace("ENCLOSED ", "")

    if p_form in ["MID TERRACE", "END TERRACE", "SEMI DETACHED", "DETACHED"]:
        return enums.PropertyForm(p_form.replace(" ", "_"))

    if epc.property_type.upper() == "MAISONNETTE":
        return enums.PropertyForm.MAISONNETTE


def _detect_property_age(epc: EPCData) -> Optional[enums.PropertyAgeBand]:
    age_band = epc.construction_age_band.upper()

    # Standard bands:
    if age_band == "ENGLAND AND WALES: BEFORE 1900":
        return enums.PropertyAgeBand.BEFORE_1900
    elif age_band == "ENGLAND AND WALES: 1900-1929":
        return enums.PropertyAgeBand.FROM_1900
    elif age_band == "ENGLAND AND WALES: 1930-1949":
        return enums.PropertyAgeBand.FROM_1930
    elif age_band == "ENGLAND AND WALES: 1950-1966":
        return enums.PropertyAgeBand.FROM_1950
    elif age_band == "ENGLAND AND WALES: 1967-1975":
        return enums.PropertyAgeBand.FROM_1967
    elif age_band in ["ENGLAND AND WALES: 1976-1982", "ENGLAND AND WALES: 1983-1990"]:
        return enums.PropertyAgeBand.FROM_1976
    elif age_band in ["ENGLAND AND WALES: 1991-1995", "ENGLAND AND WALES: 1996-2002"]:
        return enums.PropertyAgeBand.FROM_1991
    elif age_band in [
        "ENGLAND AND WALES: 2003-2006",
        "ENGLAND AND WALES: 2007 ONWARDS",
        "ENGLAND AND WALES: 2007-2011",
        "ENGLAND AND WALES: 2012 ONWARDS",
    ]:
        # Seems to get less 'standard' as it gets more recent!
        return enums.PropertyAgeBand.SINCE_2003
    elif age_band.isdecimal():
        # Purely numerical value, compare with age bands
        for threshold in reversed(enums.PropertyAgeBand):
            if int(age_band) >= threshold:
                return enums.PropertyAgeBand(threshold)


def _detect_wall_type(epc: EPCData) -> Optional[enums.WallType]:
    wall_desc = epc.walls_description.upper()

    if "CAVITY" in wall_desc:
        return enums.WallType.CAVITY
    elif "SOLID" in wall_desc:
        return enums.WallType.SOLID

    # Other solid wall indicators:
    more_solid_wall_types = ["GRANITE", "LIMESTONE", "SANDSTONE", "COB"]
    if any([sw_type in wall_desc for sw_type in more_solid_wall_types]):
        return enums.WallType.SOLID


def _detect_walls_insulated(epc: EPCData) -> Optional[bool]:
    wall_desc = epc.walls_description.upper()

    if "NO INSULATION" in wall_desc or "PARTIAL INSULATION" in wall_desc:
        return False
    elif "FILLED CAVITY" in wall_desc:
        return True

    more_insulation_indicators = [
        "WITH INTERNAL INSULATION",
        "WITH EXTERNAL INSULATION",
        "WITH ADDITIONAL INSULATION",
        " INSULATED",
    ]
    if any([indicator in wall_desc for indicator in more_insulation_indicators]):
        return True

    if wall_desc == "COB, AS BUILT":
        return False

    # Finally, try to decide it by the energy-eff rating
    if epc.walls_rating:
        return epc.walls_rating > 2


def _detect_suspended_floor(epc: EPCData) -> Optional[bool]:
    floor_desc = epc.floor_description.upper()

    return "SUSPENDED" in floor_desc


def _detect_suspended_floor_insulation(epc: EPCData) -> Optional[bool]:
    floor_desc = epc.floor_description.upper()

    things_that_are_uninsulated_floors = [
        "UNINSULATED",
        "NO INSULATION",
        "LIMITED INSULATION",
    ]
    if any([indic in floor_desc for indic in things_that_are_uninsulated_floors]):
        return False

    if "INSULATED" in floor_desc:
        return True

    # Finally, try to decide it by the energy-eff rating
    if epc.floor_rating:
        return epc.floor_rating > 2


def _detect_unheated_loft(epc: EPCData) -> Optional[bool]:
    roof_desc = epc.roof_description.upper()

    things_that_arent_unheated_lofts = [
        "(ANOTHER DWELLING ABOVE)",
        "(OTHER PREMISES ABOVE)",
        "FLAT",
        "ROOF ROOM",
    ]
    if any([indic in roof_desc for indic in things_that_arent_unheated_lofts]):
        return False
    elif "PITCHED" or "TO UNHEATED SPACE" in roof_desc:
        return True


def _detect_room_in_roof(epc: EPCData) -> Optional[bool]:
    roof_desc = epc.roof_description.upper()

    if "ROOF ROOM" in epc.roof_description.upper():
        return True

    things_that_arent_room_in_roofs = [
        "(ANOTHER DWELLING ABOVE)",
        "(OTHER PREMISES ABOVE)",
        "FLAT",
        "PITCHED",
    ]
    if any([indic in roof_desc for indic in things_that_arent_room_in_roofs]):
        return False


def _detect_rir_insulated(epc: EPCData) -> Optional[bool]:
    roof_desc = epc.roof_description.upper()

    if "ROOF ROOM" not in roof_desc:
        return False
    elif " INSULATED" in roof_desc:
        return True
    elif "NO INSULATED" in roof_desc or "LIMITED INSULATION" in roof_desc:
        return False


def _detect_roof_insulated(epc: EPCData) -> Optional[bool]:
    # This is question is only asked for unheated lofts; if the loft isn't
    # pitched then the roof_insulated field shouldn't be set from
    # roof_insulated_orig.
    roof_desc = epc.roof_description.upper()

    things_that_arent_insulated = ["NO INSULATION", "LIMITED INSULATION", "UNINSULATED"]

    if any([indic in roof_desc for indic in things_that_arent_insulated]):
        return False
    elif " INSULATED" in roof_desc:
        return True

    # Check for insulation depth pattern
    parsed = re.search(
        r"Pitched, ([\d]+)(.*)mm loft insulation", roof_desc, re.IGNORECASE
    )
    if parsed:
        try:
            if parsed.group(1).isdecimal():
                depth = int(parsed.group(1))
                return depth >= 250
        except IndexError:
            pass

    # Try to decide it by the roof-energy-eff rating
    if epc.roof_rating:
        return epc.roof_rating > 2


def _detect_flat_roof(epc: EPCData) -> Optional[bool]:
    roof_desc = epc.roof_description.upper()

    if "FLAT" in roof_desc:
        return True

    things_that_arent_flat_roofs = [
        "(ANOTHER DWELLING ABOVE)",
        "(OTHER PREMISES ABOVE)",
        "PITCHED",
        "ROOF ROOM",
        "THATCHED",
    ]
    if any([indic in roof_desc for indic in things_that_arent_flat_roofs]):
        return False


def _detect_gas_boiler(epc: EPCData) -> Optional[bool]:
    mainheat_desc = epc.mainheat_description.upper()

    if "BOILER" in mainheat_desc:
        if "MAINS GAS" in mainheat_desc:
            return True
        # Exclude boiler systems that specify a different fuel
        other_fules = [
            "OIL",
            "WOOD",
            "ANTHRACITE",
            "ELECTRIC",
            "COAL",
            "SMOKELESS FUEL",
            "LPG",
        ]
        for fule in other_fules:
            # Don't match words in other words (e.g. "oil" in "boiler")
            if re.search(rf"\b{fule}\b", mainheat_desc):
                return False
    else:
        # If the EPC specifies another heating system then we can be reasonably
        # sure that there isn't a boiler.
        things_that_arent_gas_boilers = [
            "COMMUNITY SCHEME",
            "NO SYSTEM PRESENT",
            "HEAT PUMP",
            "ROOM HEATERS",
            "ELECTRIC STORAGE HEATERS",
            "PORTABLE ELECTRIC",
            "ELECTRIC UNDERFLOOR",
            "WARM AIR",
            "ELECTRIC CEILING HEATING",
        ]
        if any([indic in mainheat_desc for indic in things_that_arent_gas_boilers]):
            return False

    # If the EPC doesn't mention a boiler but also doesn't specify another
    # heating system, it may be that the information is missing (or in Welsh)

    # One last check: the heating controls may rule out
    heating_controls = epc.main_heating_controls
    if heating_controls:
        if heating_controls > 2200 and heating_controls < 2700:
            # Heat pumps, DHS, electric storage heaters, warm air or room heaters
            return False
        elif heating_controls < 2102:
            # No heating system present or system is DHW only
            return False


def _detect_mains_gas(epc: EPCData) -> Optional[bool]:
    mainheat_desc = epc.mainheat_description.upper()

    if "MAINS GAS" in mainheat_desc:
        return True


def _detect_other_ch(epc: EPCData) -> Optional[bool]:
    mainheat_desc = epc.mainheat_description.upper()

    # Any non-gas boiler
    if "BOILER" in mainheat_desc and not _detect_gas_boiler(epc):
        return True

    things_that_are_central_heating = ["HEAT_PUMP", "COMMUNITY"]
    # HPs or community schemes will be central heating
    if any([indic in mainheat_desc for indic in things_that_are_central_heating]):
        return True

    things_that_definitely_arent_central_heating = [
        "ROOM_HEATERS",
        "WARM AIR",  # For now - this may need to be refined
        "ELECTRIC UNDERFLOOR HEATING",
        "STORAGE HEATERS",
        "CEILING HEATING",
        "PORTABLE ELECTRIC",
        "ELECTRIC HEATERS",
    ]
    if any(
        [
            indic in mainheat_desc
            for indic in things_that_definitely_arent_central_heating
        ]
    ):
        return False


def _detect_heat_pump(epc: EPCData) -> Optional[bool]:
    mainheat_desc = epc.mainheat_description.upper()

    if "HEAT PUMP" in mainheat_desc:
        return True

    # Check the controls
    heating_controls = epc.main_heating_controls
    if heating_controls:
        return heating_controls > 2200 and heating_controls < 2300

    # Safe to assume not then
    return False


def _detect_other_ch_fuel(epc: EPCData) -> Optional[enums.NonGasFuel]:
    mainheat_desc = epc.mainheat_description.upper()

    # Only works if there is a non-gas CH system
    if _detect_other_ch(epc):
        # Some special cases
        if "COMMUNITY" in mainheat_desc:
            return enums.NonGasFuel.DISTRICT
        if "ELECTRICITY" in mainheat_desc:
            return enums.NonGasFuel.ELECTRICITY
        if "ANTHRACITE" in mainheat_desc or "SMOKELESS FUEL" in mainheat_desc:
            return enums.NonGasFuel.COAL

        for fuel in enums.NonGasFuel:
            # Don't match words in other words (e.g. "oil" in "boiler")
            if re.search(rf"\b{fuel.value}\b", mainheat_desc):
                return fuel


def _detect_storage_heaters(epc: EPCData) -> bool:
    mainheat_desc = epc.mainheat_description.upper()

    return "STORAGE HEATER" in mainheat_desc


def _detect_hhrshs(epc: EPCData) -> bool:
    if epc.main_heating_controls == 2404:
        return True
    # Otherwise, wouldn't like to speculate!


def _detect_electric_radiators(epc: EPCData) -> bool:
    mainheat_desc = epc.mainheat_description.upper()

    things_that_are_electric_heaters = [
        "ROOM HEATERS, ELECTRIC",
        "ELECTRIC HEATERS",
        "PORTABLE ELECTRIC HEATING",
        "ELECTRIC CEILING HEATING",
        "RADIATORS, ELECTRIC",
    ]

    return any([indic in mainheat_desc for indic in things_that_are_electric_heaters])


def _detect_trvs(epc: EPCData) -> Optional[bool]:
    if epc.main_heating_controls:
        try:
            controls = enums.HeatingSystemControls(epc.main_heating_controls)
            if "TRVS" in controls.name:
                return enums.TRVsPresent("ALL")
        except ValueError:
            return None

        return enums.TRVsPresent("NONE")


def _detect_room_thermostat(epc: EPCData) -> Optional[bool]:
    if epc.main_heating_controls:
        try:
            controls = enums.HeatingSystemControls(epc.main_heating_controls)
            return "ROOM" in controls.name
        except ValueError:
            return None

        return False


def _detect_timer(epc: EPCData) -> Optional[bool]:
    # Three different kinds of systems that constitute a heating timer

    if epc.main_heating_controls:
        try:
            controls = enums.HeatingSystemControls(epc.main_heating_controls)

            # One value is positively undetermined
            if controls == enums.HeatingSystemControls.ROOM_APPLIANCE:
                return None

            # Others can be positively determined
            things_that_are_timed_systems = ["PROGRAMMER", "TIME_AND_TEMP", "STORAGE"]
            return any(
                [indic in controls.name for indic in things_that_are_timed_systems]
            )
        except ValueError:
            return None


def _detect_programmable_thermostat(epc: EPCData) -> Optional[bool]:
    if epc.main_heating_controls:
        try:
            controls = enums.HeatingSystemControls(epc.main_heating_controls)
            if "TIME_AND_TEMP" in controls.name:
                return True
        except ValueError:
            return None

        things_that_definitely_arent_timed = [
            "NO_CONTROL",
            "BOILER_TRVS_BYPASS",
            "DHS_FLAT_RATE_TRVS",
            "DHS_USE_CHARGE_TRVS",
        ]
        if any(
            [indic in controls.name for indic in things_that_definitely_arent_timed]
        ):
            return False


"""
# The below functions populate data from external data if the user declines to
# correct them. They should only be called if we have a complete set of answers
# for a section from external data.
"""


def set_type_from_orig(answers: models.Answers) -> models.Answers:
    answers.property_type = answers.property_type_orig
    answers.property_form = answers.property_form_orig
    answers.property_age_band = answers.property_age_band_orig

    return answers


def set_walls_from_orig(answers: models.Answers) -> models.Answers:
    answers.wall_type = answers.wall_type_orig
    answers.walls_insulated = answers.walls_insulated_orig

    return answers


def set_floor_from_orig(answers: models.Answers) -> models.Answers:
    answers.suspended_floor = answers.suspended_floor_orig

    if answers.suspended_floor:
        answers.suspended_floor_insulated = answers.suspended_floor_insulated_orig
    else:
        # We need to wipe any answers that may have been previously entered
        answers.suspended_floor_insulated = None

    return answers


def set_roof_from_orig(answers: models.Answers) -> models.Answers:
    answers.unheated_loft = answers.unheated_loft_orig

    # Uninferable fields can be wiped because they can't be relevant -
    # this function can only be called if we have a complete set
    # of answers.
    answers.flat_roof_insulated = ""

    if answers.unheated_loft:
        answers.roof_space_insulated = answers.roof_space_insulated_orig
        answers.flat_roof = None
        answers.room_in_roof = None
        answers.rir_insulated = None

    else:
        answers.room_in_roof = answers.room_in_roof_orig
        answers.roof_space_insulated = None

        if answers.room_in_roof:
            answers.rir_insulated = answers.rir_insulated_orig
            answers.flat_roof = None
        else:
            answers.flat_roof = answers.flat_roof_orig
            answers.rir_insulated = None

    return answers


def set_heating_from_orig(answers: models.Answers) -> models.Answers:
    answers.gas_boiler_present = answers.gas_boiler_present_orig
    # Can't populate HWT present, boiler age or broken down state
    # (and therefore no point in populating the heating controls data
    # or 'other CH fuel' data)

    # Uninferable fields
    answers.hwt_present = None
    answers.smart_thermostat = None
    answers.gas_boiler_age = ""
    answers.gas_boiler_broken = None

    # Because we can't infer the presence of the HWT, we the only possible
    # scenario to complete from inferences is that there is no CH system at all.
    answers.on_mains_gas = answers.on_mains_gas_orig
    answers.other_heating_present = answers.other_heating_present_orig
    answers.trvs_present = None
    answers.room_thermostat = None
    answers.ch_timer = None
    answers.programmable_thermostat = None

    answers.heat_pump_present = None
    answers.other_heating_fuel = ""

    answers.storage_heaters_present = answers.storage_heaters_present_orig

    if answers.storage_heaters_present is False:
        answers.hhrshs_present = None
        answers.electric_radiators_present = answers.electric_radiators_present_orig
    else:
        answers.electric_radiators_present = None
        answers.hhrshs_present = answers.hhrshs_present_orig

    return answers


def close_questionnaire(answers: models.Answers):
    """Set the questionnaire as completed.

    Prevents any part of it being edited through the questionnaire views. Also
    sends an acknowledment email.
    """

    answers.completed_at = timezone.now()
    answers.save()

    context = {
        "full_name": f"{answers.first_name} {answers.last_name}",
        "postcode": answers.property_postcode,
        "consented_callback": answers.consented_callback,
        "consented_future_schemes": answers.consented_future_schemes,
        "uuid": answers.uuid,
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


def sync_household_adults(answers: models.Answers):
    """Ensure we have the correct number of HouseholdAdults.

    Normally will just have to create them, but we may need to delete them in
    the situation where the user has gone back and reduced the number in the
    household!
    """

    # Sanity check.
    if answers.adults < 1:
        # A fatal error but let's pretend it didn't happen (which it won't)
        answers.adults = 1
        answers.save()
        logging.error("Household of zero adults somehow created")

    # Delete any excess first
    models.HouseholdAdult.objects.filter(adult_number__gt=answers.adults).delete()
    # nb will cascade to related WelfareBenefits

    # Now make sure we have the ones we need
    for adult_number in range(1, answers.adults + 1):
        models.HouseholdAdult.objects.get_or_create(
            answers=answers, adult_number=adult_number
        )


def sync_benefits(adult: models.HouseholdAdult) -> bool:
    """Ensure we have the correct benefit models associated with this adult.

    Normally will just have to create them, but we may need to delete them in
    the situation where the user has gone back and changed their options.

    The view logic will have temporarily stored the form cleaned_data onto the
    HouseholdAdult object, but it won't persist there.

    (Note that this means that we need to be alert to any naming collision
    between benefits and fields on HouseholdAdult!)

    Returns whether any benefits were saved to the HouseholdAdult (and therefore
    whether we need to show the amounts inputs.
    """

    for_deletion = []
    any_benefits = False

    for benefit in enums.BenefitType:
        if getattr(adult, benefit.value.lower(), False):
            any_benefits = True
            models.WelfareBenefit.objects.get_or_create(
                recipient=adult, benefit_type=benefit.value
            )
        else:
            for_deletion.append(benefit.value)

    models.WelfareBenefit.objects.filter(
        recipient=adult, benefit_type__in=for_deletion
    ).delete()

    return any_benefits


def save_benefit_amounts(adult: models.HouseholdAdult):
    """Save the relevant benefit amounts & frequencies.

    The view logic will have temporarily stored the form cleaned_data onto the
    WelfareBenefit object, but it won't persist there.
    """
    for benefit in adult.welfarebenefit_set.all():
        # All fields are required so there will be data for each (pinky promise?)
        benefit.amount = getattr(adult, benefit.benefit_type.lower() + "_amount")
        benefit.frequency = getattr(adult, benefit.benefit_type.lower() + "_frequency")
        benefit.save()

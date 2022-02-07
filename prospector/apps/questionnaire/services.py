import re
from typing import Optional

from . import enums
from . import models
from prospector.apis.epc.dataclass import EPCData


def prepopulate_from_epc(answers: models.Answers, selected_epc: EPCData):
    """Parse EPC contents to populate initial values for property energy data."""

    answers.property_type_orig = _detect_property_type(selected_epc)
    answers.property_form_orig = _detect_property_form(selected_epc)
    answers.property_age_band_orig = _detect_property_age(selected_epc)
    answers.wall_type_orig = _detect_wall_type(selected_epc)
    answers.walls_insulated_orig = _detect_walls_insulated(selected_epc)
    answers.suspended_floor_orig = _detect_suspended_floor(selected_epc)
    answers.unheated_loft_orig = _detect_unheated_loft(selected_epc)
    answers.room_in_roof_orig = _detect_room_in_roof(selected_epc)
    answers.rir_insulated_orig = _detect_rir_insulated(selected_epc)
    answers.roof_space_insulated_orig = _detect_roof_insulated(selected_epc)
    answers.flat_roof_orig = _detect_flat_roof(selected_epc)
    answers.gas_boiler_present_orig = _detect_gas_boiler(selected_epc)
    answers.trvs_present_orig = _detect_trvs(selected_epc)
    answers.room_thermostat_orig = _detect_room_thermostat(selected_epc)
    answers.ch_timer_orig = _detect_timer(selected_epc)
    answers.programmable_thermostat_orig = _detect_programmable_thermostat(selected_epc)

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

    if "NO INSULATION" in wall_desc:
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


def _detect_suspended_floor(epc: EPCData) -> Optional[bool]:
    floor_desc = epc.floor_description.upper()

    if "SUSPENDED" in floor_desc:
        return True
    elif "SOLID" in floor_desc:
        return False

    things_that_arent_suspended_floors = [
        "(ANOTHER DWELLING BELOW)",
        "(OTHER PREMISES BELOW)",
        "CONSERVATORY" "To unheated space",
        "To external air",
    ]
    if any([indic in floor_desc for indic in things_that_arent_suspended_floors]):
        return False


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
    # This is question is only asked for unheated lofts, so explicitly exclude
    # flat roofs and RiRs
    roof_desc = epc.roof_description.upper()

    things_that_arent_insulated = ["NO INSULATION", "LIMITED INSULATION", "UNINSULATED"]

    if "PITCHED" not in roof_desc:
        return None
    elif any([indic in roof_desc for indic in things_that_arent_insulated]):
        return False
    elif " INSULATED" in roof_desc:
        return True

    # Check for insulation depth pattern
    parsed = re.search(r"Pitched, ([\d]+)(.*)mm loft insulation", roof_desc)
    if parsed:
        try:
            if parsed.group(1).isdecimal():
                depth = int(parsed.group(1))
                return depth >= 250
        except IndexError:
            pass


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


def _detect_gas_boiler(epc: EPCData) -> bool:
    mainheat_desc = epc.mainheat_description.upper()

    if "BOILER" in mainheat_desc:
        if "GAS" in mainheat_desc or "LPG" in mainheat_desc:
            return True
        # Exclude boiler systems that specify a different fuel
        other_fules = [
            "oil",
            "wood",
            "anthracite",
            "electric",
            "coal",
            "smokeless fuel",
        ]
        if any([indic in mainheat_desc for indic in other_fules]):
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

    # There may be a gas boiler for DHW
    if "GAS BOILER" in epc.hotwater_description.upper():
        return True

    # One last check: the heating controls may tell us the technology:
    heating_controls = epc.main_heating_controls
    if heating_controls > 2200 and heating_controls < 2700:
        return False


def _detect_trvs(epc: EPCData) -> Optional[bool]:
    if epc.main_heating_controls:
        try:
            controls = enums.HeatingSystemControls(epc.main_heating_controls)
            return "TRVS" in controls.name
        except ValueError:
            return None

        return False


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

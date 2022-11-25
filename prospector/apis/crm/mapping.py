import logging
from functools import wraps
from typing import Literal
from typing import Optional
from typing import Union

from prospector.apis.crm import crm
from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import models


logger = logging.getLogger(__name__)


class UnmappedValueError(Exception):
    pass


def map_pcc_values(pcc_fieldname):
    def _map_pcc_values(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            option_name = func(*args, **kwargs)

            if option_name is None:
                logger.error(UnmappedValueError((option_name, kwargs)))
                return (option_name, None)

            option_value = crm.option_value(pcc_fieldname, option_name)
            return (option_name, option_value)

        return wrapper

    return _map_pcc_values


@map_pcc_values("pcc_primaryheatingfuel")
def infer_pcc_primaryheatingfuel(
    on_mains_gas: Optional[bool] = None,
    storage_heaters_present: Optional[bool] = None,
    other_heating_fuel: Union[
        enums.NonGasFuel, Literal[""]
    ] = "",  # non-nullable, but blank=True
) -> int:
    """Map between answers and pcc_primaryheatingfuel.

    Unmapped answers field values:
        'other_heating_fuel': DISTRICT  # see pcc_heatingdeliverymethod

    pcc_primaryheatingfuel:
        No Heating System Present
    """
    if on_mains_gas:
        return "Mains Gas"
    elif other_heating_fuel == enums.NonGasFuel.ELECTRICITY:
        if storage_heaters_present:
            return "Electricity - off peak"
        else:
            return "Electricity - standard"
    else:
        return {
            enums.NonGasFuel.WOOD: "Biomass",
            enums.NonGasFuel.COAL: "Coal",
            enums.NonGasFuel.LPG: "LPG",
            enums.NonGasFuel.OIL: "Oil",
        }.get(other_heating_fuel, "Unknown")


@map_pcc_values("pcc_primaryheatingdeliverymethod")
def infer_pcc_primaryheatingdeliverymethod(
    gas_boiler_present: Optional[bool] = None,
    heat_pump_present: Optional[bool] = None,
    storage_heaters_present: Optional[bool] = None,
    hhrshs_present: Optional[bool] = None,
    electric_radiators_present: Optional[bool] = None,
) -> int:
    if gas_boiler_present:
        return "Central Heating"
    elif heat_pump_present:
        return "Heat Pump"
    elif storage_heaters_present:
        if hhrshs_present:
            return "Night Storage Heaters - electronic control"
        else:
            return "Night Storage Heaters - manual control"
    elif electric_radiators_present:
        return "Room Heaters Fixed"
    else:
        return "Unknown"


@map_pcc_values("pcc_boilertype")
def infer_pcc_boilertype(
    gas_boiler_present: Optional[bool] = None,
    gas_boiler_age: Union[enums.BoilerAgeBand, Literal[""]] = "",
) -> int:
    if gas_boiler_present is False:
        return "No Boiler"
    elif gas_boiler_present:
        if gas_boiler_age == enums.BoilerAgeBand.BEFORE_2004:
            return "Standard"
        elif gas_boiler_age == "":  # (blank)
            return "Unknown"
        else:  # Bolier is newer than 2004
            return "Condensing"
    else:
        return "Unknown"


@map_pcc_values("pcc_heatingcontrols")
def infer_pcc_heatingcontrols(
    gas_boiler_present: Optional[bool] = None,
    smart_thermostat: Optional[bool] = None,
    room_thermostat: Optional[bool] = None,
    programmable_thermostat: Optional[bool] = None,
    heat_pump_present: Optional[bool] = None,
    ch_timer: Optional[bool] = None,
) -> int:
    if gas_boiler_present is False and heat_pump_present is False:
        return "Not applicable"
    elif gas_boiler_present or heat_pump_present:
        if smart_thermostat:
            return "Smart Thermostat"
        elif room_thermostat:
            if ch_timer:
                return "Programmer and thermostat"
            else:
                return "Thermostat Only"
        elif room_thermostat is False:
            if ch_timer:
                return "Programmer only"
            elif (
                ch_timer is False
                and smart_thermostat is False
                and programmable_thermostat is False
            ):
                return "No Heating Control"
        else:
            return "Unknown"
    else:
        return "Unknown"


@map_pcc_values("pcc_propertytype")
def infer_pcc_propertytype(
    property_type: Union[enums.PropertyType, Literal[""]] = "",
    property_form: Union[enums.PropertyForm, Literal[""]] = "",
) -> int:
    if property_type == enums.PropertyType.BUNGALOW:
        if property_form == enums.PropertyForm.DETACHED:
            return "Bungalow - Detatched"
        elif property_form == enums.PropertyForm.SEMI_DETACHED:
            return "Bungalow - Semi Deatched"
        else:
            return "Bungalow - Not Specified"
    elif property_type == enums.PropertyType.FLAT:
        if property_form == enums.PropertyForm.FLAT_BLOCK:
            return "Flat - in block/mixed use building"
        elif property_form == enums.PropertyForm.FLAT_SMALL:
            return "Flat - in small block/converted dwelling"
        elif property_form == enums.PropertyForm.MAISONNETTE:
            return "Maisonette"
        else:
            return "Flat - Type not specified"
    elif property_type == enums.PropertyType.HOUSE:
        if property_form == enums.PropertyForm.DETACHED:
            return "House - Detached"
        elif property_form == enums.PropertyForm.SEMI_DETACHED:
            return "House - Semi Detatched"
        elif property_form == enums.PropertyForm.END_TERRACE:
            return "Terraced - End"
        elif property_form == enums.PropertyForm.MID_TERRACE:
            return "Terraced - Mid"
        elif property_form == enums.PropertyForm.MAISONNETTE:
            return "Maisonette"
        else:
            return "House - Not Specified"
    elif property_type == enums.PropertyType.PARK_HOME:
        return "Park home"
    else:
        return "Not yet specified"


@map_pcc_values("pcc_rooftype")
def infer_pcc_rooftype(
    unheated_loft: Optional[bool] = None,
    room_in_roof: Optional[bool] = None,
    flat_roof: Optional[bool] = None,
) -> int:
    if unheated_loft:
        return "Pitched - loft space"
    elif room_in_roof:
        return "Pitched - converted loft"
    elif flat_roof:
        return "Flat roof"
    else:
        return "Unknown"


@map_pcc_values("pcc_walltype")
def infer_pcc_walltype(
    wall_type: Union[enums.WallType, Literal[""]] = "",
    walls_insulated: Optional[bool] = None,
) -> int:
    if wall_type == enums.WallType.CAVITY:
        if walls_insulated:
            return "Brick cavity - insulated"
        else:
            return "Brick cavity - not insulated"
    else:
        return "Unknown"

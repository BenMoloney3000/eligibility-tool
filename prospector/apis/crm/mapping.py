from typing import Optional
from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import models


def infer_pcc_primaryheatingfuel(
    on_mains_gas: Optional[bool] = None,
    storage_heaters_present: Optional[bool] = None,
    other_heating_fuel: enums.NonGasFuel = "",  # non-nullable, but blank=True
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

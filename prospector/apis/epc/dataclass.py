import datetime
from dataclasses import dataclass


@dataclass
class EPCData:
    id: str
    date: datetime.date
    address_1: str
    address_2: str
    address_3: str
    uprn: str
    property_type: str
    built_form: str
    construction_age_band: str
    walls_description: str
    walls_rating: int
    floor_description: str
    floor_rating: int
    roof_description: str
    roof_rating: int
    mainheat_description: str
    hotwater_description: str
    main_heating_controls: int
    current_energy_rating: int

    def __repr__(self):
        return (f"{self.address_1}, {self.address_2}".strip(", ")) + (
            f", inspected on {self.date:%d/%m/%Y}" if self.date else ""
        )

from dataclasses import dataclass


@dataclass
class ParityData:
    id: str
    org_ref: str
    address_link: str
    googlemaps: str
    address_1: str
    address_2: str
    address_3: str
    postcode: str
    sap_score: float
    sap_band: str
    lodged_epc_score: int
    lodged_epc_band: str
    tco2_current: float
    realistic_fuel_bill: str
    type: str
    attachment: str
    construction_years: str
    heated_rooms: int
    wall_construction: str
    wall_insulation: str
    floor_construction: str
    floor_insulation: str
    roof_construction: str
    roof_insulation: str
    glazing: str
    heating: str
    boiler_efficiency: str
    main_fuel: str
    controls_adequacy: str
    local_authority: str
    ward: str
    parliamentary_constituency: str
    region_name: str
    tenure: str
    uprn: str
    lat_coordinate: float
    long_coordinate: float
    lower_super_output_area_code: str
    multiple_deprivation_index: int

    def __repr__(self):
        return (f"{self.address_1}, {self.address_2}".strip(", ")) + (
            f", inspected on {self.date:%d/%m/%Y}" if self.date else ""
        )

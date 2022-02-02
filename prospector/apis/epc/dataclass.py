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

    def __repr__(self):
        return (f"{self.address_1}, {self.address_2}".strip(", ")) + (
            f", inspected on {self.date:%d/%m/%Y}" if self.date else ""
        )

from dataclasses import dataclass
from enum import Enum


# TODO: Handle this differently
class CarEmissionType(Enum):

    ELECTRIC = 1
    HYBRID = 2
    DIESEL = 3
    PETROL = 4

    def has_engine_size(self) -> bool:
        return self in [CarEmissionType.HYBRID, CarEmissionType.DIESEL, CarEmissionType.PETROL]


@dataclass
class Car:

    _type = "Car" # TODO: Improve this
    nickname: str | None = None
    emission_type: CarEmissionType | None = None
    engine_size: float | None = None # Can be None for electric cars


@dataclass
class Coach:

    _type = "Coach"


@dataclass
class Train:

    _type = "Train"

from dataclasses import dataclass
from enum import Enum


class EmissionType(Enum):

    ELECTRIC: float = 1
    HYBRID: float = 2
    DIESEL: float = 3
    GASOLINE: float = 4


@dataclass
class Journey:

    origin: str
    destination: str
    distance: int


@dataclass
class CarJourney(Journey):

    engine_size: float
    emission_type: str

    @property
    def green_score(self) -> float:
        return 1 / (self.distance * self.engine_size * self.emission_type.value) 


@dataclass
class CoachJourney(Journey):

    @property
    def green_score(self) -> float:
        return 10 / (self.distance)


@dataclass
class TrainJourney(Journey):

    @property
    def green_score(self) -> float:
        return 100 / (self.distance)
    
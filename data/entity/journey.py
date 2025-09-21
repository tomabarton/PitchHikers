from dataclasses import dataclass
from data.entity.transport import Car, CarEmissionType, Coach, Train
from data.google.places import Place

@dataclass
class Journey:

    fixture_id: int  # Don't need full fixture object 
    origin: Place
    destination: Place
    distance: int  
    transport: Car | Coach | Train # One of these three


@dataclass
class CarJourney(Journey):

    num_passengers: int
    id: int | None = None

    @property
    def green_score(self) -> float:
        if not self.transport.engine_size:  # Handle electric cars
            engine_size = 1 
        else:
            engine_size = self.transport.engine_size
        return self.num_passengers / (self.distance * engine_size * self.transport.emission_type.value) 

    @classmethod
    def from_db(
            cls, 
            fixture_id: int, 
            origin: Place, 
            destination: Place, 
            distance: int, 
            num_passengers: int, 
            car: Car, 
            id: int, 
            *args, 
            **kwargs
        ) -> 'CarJourney':
        return cls(
            fixture_id,
            origin,
            destination,
            distance,
            num_passengers,
            car,
            id
        )

    # TODO: Handle this in parent class an extend?
    def params(self) -> list[str|CarEmissionType|float|int|None]:  # Handle string with ENUM/_type instead
        return [self.fixture_id, self.origin.id, self.origin.address, self.destination.id, self.destination.address, 
                self.distance, self.transport._type.upper(), self.green_score, self.transport.emission_type.name, self.transport.engine_size, self.num_passengers]


@dataclass
class CoachJourney(Journey):

    id: int | None = None

    @property
    def green_score(self) -> float:
        return 50 / (self.distance)

    @classmethod
    def from_db(
            cls, 
            fixture_id: int, 
            origin: Place, 
            destination: Place, 
            distance: int, 
            id: int, 
            *args, 
            **kwargs
            ) -> 'CoachJourney':
        return cls(
            fixture_id,
            origin,
            destination,
            distance,
            Coach(),  # TODO: make singleton to prevent overhead of recreation? 
            id
        )

    def params(self) -> list[str|float|None]:  # Handle string with ENUM/_type instead
        return [self.fixture_id, self.origin.id, self.origin.address, self.destination.id, self.destination.address, self.distance, self.transport._type.upper(), self.green_score, None, None, None]  # TODO: change to .name for class?


@dataclass
class TrainJourney(Journey):

    id: int | None = None

    @property
    def green_score(self) -> float:
        return 250 / (self.distance)
    
    def params(self) -> list[str|float|None]:  # Handle string with ENUM/_type instead
        return [self.fixture_id, self.origin.id, self.origin.address, self.destination.id, self.destination.address, self.distance, self.transport._type.upper(), self.green_score, None, None, None]  # TODO: handle better

    @classmethod
    def from_db(
            cls, 
            fixture_id: int,
            origin: Place,
            destination: Place, 
            distance: int, 
            id: int,
            *args,
            **kwargs
        ) -> 'TrainJourney':
        return cls(
            fixture_id,
            origin,
            destination,
            distance,
            Train(),  # TODO: make singleton to prevent overhead of recreation? 
            id
        )


def build_journey(
    fixture_id: int,
    origin: Place,
    destination: Place,
    distance: int,
    transport: Car | Coach | Train,
    num_passengers: int = 0,
    id: int | None = None
) -> CarJourney | CoachJourney | TrainJourney:
    """
    Helper function to create the relevant journey subtype based on parameters passed.
    """
    if isinstance (transport, Car):
        return CarJourney(fixture_id, origin, destination, distance, transport, num_passengers, id=id)
    if isinstance (transport, Coach):
        return CoachJourney(fixture_id, origin, destination, distance, transport, id=id)
    return TrainJourney(fixture_id, origin, destination, distance, transport, id=id)
    

from dataclasses import dataclass
from data.access.singleton import Singleton
from google.maps.places_v1.services.places import PlacesClient
from google.maps.places_v1.types import AutocompletePlacesRequest #, Place
from  google.maps.places_v1.types.places_service import AutocompletePlacesResponse


# https://googleapis.dev/python/places/latest/places_v1/types_.html#google.maps.places_v1.types.AutocompletePlacesRequest
# May need a location bias when deployed


@dataclass
class Place:

    address: str
    id: str

    @classmethod
    def from_autocomplete(cls, place_prediction: AutocompletePlacesResponse.Suggestion.PlacePrediction) -> 'Place':
        return cls(
            address=place_prediction.text.text,
            id=place_prediction.place_id
        )
    
    def __repr__(self) -> str:
        return self.address


class GooglePlacesClient(metaclass=Singleton):

    def __init__(self):
        self.client = PlacesClient()

    def get_place_predictions(self, query_str: str) -> list[Place]:
        request = AutocompletePlacesRequest(
            input=query_str,
            language_code="en-GB"
        )
        response: AutocompletePlacesResponse = self.client.autocomplete_places(request)
        return [Place.from_autocomplete(suggestion.place_prediction) for suggestion in response.suggestions]

from data.access.http_requests import HTTPRequests
from data.access.api import gmap_api_key

# https://developers.google.com/maps/documentation/routes/client-libraries#python
# https://developers.google.com/maps/documentation/places/web-service/text-search#includedtype

class GMaps:
    
    def __init__(self, api_key: str=gmap_api_key) -> None:
        self.api_key = api_key
        self.base_url = "https://places.googleapis.com/v1/places:searchText"
        self.req = HTTPRequests(self.base_url)

    def get_places_id(
            self,
            search_string: str
    ):
        """
        Get google specific place ID (for origin/destination)
        """
        params = {
            "textQuery": search_string,
            "key": self.api_key ,
            'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.id'
        }
        self.req.post(params=params)



    # TODO: Defunct now
    def get_route(
            self, 
            origin: str, 
            destination: str, 
            travel_mode: str,
            emission_type: str="",
        ) -> dict[str,str]:
        """
        Get route information from origin to destination using specified mode of transport.
        """
        params={
            "travelMode": travel_mode,
            "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
            "requestedReferenceRoutes": ["FUEL_EFFICIENT"]
        }
        if emission_type:
            params["routeModifiers"]["vehicleInfo"]["emissionType"] = emission_type


        return self.gmap.get("directions/json", params=params)
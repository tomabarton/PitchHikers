import requests
from requests.exceptions import RequestException

class HTTPRequests:

    def __init__(self, base_url: str, timeout: int=30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, 
            endpoint: str="", 
            params: dict[str,str]={}, 
            headers: dict[str,str]={}
        ) -> dict[str,str]:
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise HTTPRequestError(f"GET request failed: {str(e)}")

    def post(
            self, 
            endpoint: str, 
            data: dict[str,str]={}, 
            json: dict[str,str]={},
            headers: dict[str,str]={}
        ) -> dict[str,str]:
        """
        Perform POST request
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.post(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise HTTPRequestError(f"POST request failed: {str(e)}")


class HTTPRequestError(Exception):
    """Custom exception for HTTP request errors"""
    pass

if __name__ == "__main__":
    url = "https://football-web-pages1.p.rapidapi.com/fixtures-results.json"

    payload={}
    headers = {
        'x-rapidapi-key': 'e21451adaamshae4395b372e434dp1f99c5jsn26153a4eaec6',
        'x-rapidapi-host': 'football-web-pages1.p.rapidapi.com'
    }
    params = {
        'comp': '1',
        'round': '1',
        'team': '1'

    }
    try:
        http_client = HTTPRequests(base_url=url)
        response = http_client.get(headers=headers, params=params)
        print(response)
    except HTTPRequestError as e:
        print(f"An error occurred: {e}")

    from data.access.data_access import DataAccess
    from data.entity.club import Club

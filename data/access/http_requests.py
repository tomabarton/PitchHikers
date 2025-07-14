import requests
from requests.exceptions import RequestException

class HTTPRequests:
    def __init__(self, base_url: str, timeout: int = 30):
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
            endpoint: str, data: dict[str,str]={}, 
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
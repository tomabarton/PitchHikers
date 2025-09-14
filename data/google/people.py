from datetime import date
import os
from data.access.singleton import Singleton
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

class GooglePeopleClient:

    def __init__(self) -> None:
        self._SCOPES = [ 
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/user.birthday.read", 
            "openid"
        ]
        self._redirect_uri = "http://localhost:8502/oauth2callback" # TODO: fetch from config
        self._credentials = self._get_credentials()
        self.client = build("people", "v1", credentials=self._credentials).people()
      
    def _get_credentials(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self._SCOPES)

        if not creds or not creds.valid:
            refresh_success = False
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    refresh_success = True
                except RefreshError as e:
                    print(f"Error refreshing credentials: {e}")
            elif not refresh_success:
                flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
                    "/Users/tbart/Projects/PitchHikers/data/google/credentials.json", self._SCOPES, redirect_uri="http://localhost:8502/oauth2callback"
                )
                creds = flow.run_local_server(port=0, redirect_uri_trailing_slash=False)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds
    
    def get_user_details(self, resource_name: str='people/me', person_fields: str="birthdays") -> date:
        """
        Fetches user details from Google People API.
        Example format:
        {'resourceName': 'people/101135359444256237088', 'etag': '%EgcBAgcILjc9GgQBAgUHIgxxM080RXdCMHFBdz0=', 'names': [{'metadata': {'primary': True, 'source': {'type': 'PROFILE', 'id': '101135359444256237088'}, 'sourcePrimary': True}, 'displayName': 'Thomas Barton', 'familyName': 'Barton', 'givenName': 'Thomas', 'displayNameLastFirst': 'Barton, Thomas', 'unstructuredName': 'Thomas Barton'}], 'birthdays': [{'metadata': {'primary': True, 'source': {'type': 'PROFILE', 'id': '101135359444256237088'}}, 'date': {'month': 9, 'day': 30}}, {'metadata': {'source': {'type': 'ACCOUNT', 'id': '101135359444256237088'}}, 'date': {'year': 1995, 'month': 9, 'day': 30}}]}
        """
        reponse = self.client.get(resourceName=resource_name, personFields=person_fields).execute()
        birthday_dict = reponse['birthdays'][-1]['date']
        return date(year=birthday_dict['year'], month=birthday_dict['month'], day=birthday_dict['day'])

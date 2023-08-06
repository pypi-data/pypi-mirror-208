import base64
import json
import os
from typing import Union

from requests_oauthlib import OAuth2Session


class PolarTeamproAPI:
    BASE_URL = "https://teampro.api.polar.com"
    AUTH_URL = "https://auth.polar.com/"
    AUTH_ENDPOINT = "oauth/authorize?"
    TOKEN_ENDPOINT = "oauth/token?"

    def __init__(
        self, client_id: str, client_secret: str, redirect_uri: str, version: str = "v1"
    ) -> None:
        self.VERSION = version
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = redirect_uri
        self.REFRESH_TOKEN = None
        self.SESSION = None
        self.SCOPE = "team_read"
        self.HEADERS = {
            "Authorization": f"Basic {self._get_auth_header()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Token init
        self.HOME_DIR = (
            os.getenv("HOME") or os.getenv("HOMEPATH") or os.getenv("USERPROFILE")
        )
        self.TOKEN_CACHE_DIR = os.getenv("SSI_TOKEN_CACHE") or "."

    # Helpers

    def _get_auth_header(self):
        auth_string = f"{self.CLIENT_ID}:{self.CLIENT_SECRET}"
        auth_string_encoded = auth_string.encode("ascii")
        auth_string_decoded = base64.b64encode(auth_string_encoded).decode("ascii")
        return auth_string_decoded

    # Request helpers

    def _url(self, *route) -> str:
        return "{base}/{version}/{route}".format(
            base=self.BASE_URL,
            version=self.VERSION,
            route="/".join(str(r) for r in route),
        )

    def _get_route_json(self, *route, **params) -> dict:
        if self.session is None:
            raise Exception("Please authenticate first.")

        for param, val in params.items():
            if isinstance(param, bool):
                params[param] = json.dumps(val)  # So that True -> 'true'

        # r = requests.get(self._url(*route), headers=self.HEADERS, params=params)
        r = self.session.request("get", url=self._url(*route), headers=self.HEADERS)

        return r.json()

    def authenticate(self) -> None:
        oauth = OAuth2Session(
            client_id=self.CLIENT_ID, redirect_uri=self.REDIRECT_URI, scope=self.SCOPE
        )
        authorization_url, _ = oauth.authorization_url(
            self.AUTH_URL + self.AUTH_ENDPOINT
        )
        print("Please visit the following URL to authorize the application:")
        print(authorization_url)

        authorization_response = input("Enter the full callback URL: ")
        token = oauth.fetch_token(
            token_url=self.AUTH_URL + self.TOKEN_ENDPOINT,
            authorization_response=authorization_response,
            client_secret=self.CLIENT_SECRET,
            headers=self.HEADERS,
        )
        self.TOKEN = token
        self.session = oauth

    # Team

    def get_team(self, page: int = None, per_page: int = None) -> dict:
        return self._get_route_json("teams", page=page, per_page=per_page)

    def get_team_details(self, team_id: str) -> dict:
        return self._get_route_json("teams", team_id)

    # Team training sessions

    def get_team_training_session(
        self,
        team_id: str,
        since: str = None,
        until: str = None,
        page: int = None,
        per_page: int = None,
    ) -> dict:
        return self._get_route_json(
            "teams",
            team_id,
            "training_sessions",
            since=since,
            until=until,
            page=page,
            per_page=per_page,
        )

    def get_team_training_session_detail(self, training_session_id: str) -> dict:
        return self._get_route_json("teams", "training_sessions", training_session_id)

    # Player training sessions

    def get_player_training_session(
        self,
        player_id: str,
        since: str = None,
        until: str = None,
        type: str = None,
        page: int = None,
        per_page: int = None,
    ) -> dict:
        return self._get_route_json(
            "players",
            player_id,
            "training_sessions",
            since=since,
            until=until,
            type=type,
            page=page,
            per_page=per_page,
        )

    def get_player_training_session_detail(
        self, player_session_id: str, samples: Union[str, list[str]] = "all"
    ) -> dict:
        """_summary_

        Args:
            player_session_id (str): _description_
            samples (str | list[str]): Include requested samples in response.
                                       Possible values are "all" or comma-separated list from
                                       "distance", "location", "hr", "speed", "cadence", "altitude", "forward_acceleration", "rr".

        Returns:
            dict: _description_
        """
        return self._get_route_json(
            "training_sessions", player_session_id, samples=samples
        )

    def get_player_training_session_trimmed(self, player_session_id: str) -> dict:
        return self._get_route_json(
            "training_sessions", player_session_id, "session_summary"
        )

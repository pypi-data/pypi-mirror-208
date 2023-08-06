import base64
import webbrowser

import requests

# POLAR API DOCUMENTATION
# https://www.polar.com/teampro-api/?python#teampro-api

# -------- AUTHORIZATION AND ACCESS TOKENS --------- #


class POLAR_API:
    def __init__(self, client_id, client_secret, team):
        self.client_id = client_id
        self.client_secret = client_secret
        self.team = team
        self.authorize_url = "https://auth.polar.com/oauth/authorize"
        self.access_token_url = "https://auth.polar.com/oauth/token"
        self.authorize_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "team_read",
        }

    # Authorization

    def _get_authorization_code(self):
        r = requests.get(self.authorize_url, params=self.authorize_params)

        webbrowser.open(r.history[0].url, new=2)
        authorization_code = input("Authorization Code: ")

        return authorization_code

    def get_tokens(self):
        encoding = self.client_id + ":" + self.client_secret
        message_bytes = encoding.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        base64_encoding = base64_bytes.decode("ascii")
        headers = {"Authorization": "Basic " + base64_encoding}

        authorization_code = self._get_authorization_code()

        # POST request to get access token
        access_token_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
        }
        r_post = requests.post(
            self.access_token_url, data=access_token_data, headers=headers
        )
        tokens = r_post.json()

        return tokens

    # Team

    def get_teams_info(self, tokens):
        access_token = tokens["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + access_token,
        }
        r = requests.get(
            "https://teampro.api.polar.com/v1/teams", params={}, headers=headers
        )
        teams_info = r.json()

        return teams_info

    def get_team_players(self, tokens, team_id):
        access_token = tokens["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + access_token,
        }
        r = requests.get(
            f"https://teampro.api.polar.com/v1/teams/{team_id}",
            params={},
            headers=headers,
        )
        players_and_staff = r.json()

        return players_and_staff

    # Session

    def get_session(self, tokens, team_id, date):
        access_token = tokens["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + access_token,
        }

        day, month, year = date.split("-")
        r = requests.get(
            f"https://teampro.api.polar.com/v1/teams/{team_id}/training_sessions",
            params={
                "since": f"{year}-{month}-{day}T00:00:00",
                "until": f"{year}-{month}-{day}T23:59:59",
                "per_page": "100",
            },
            headers=headers,
        )
        sessions_metadata = r.json()

        return sessions_metadata

    def get_sessions(self, tokens, team_id, dates):
        access_token = tokens["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + access_token,
        }

        day1, month1, year1 = dates[0].split("-")
        day2, month2, year2 = dates[1].split("-")
        r = requests.get(
            f"https://teampro.api.polar.com/v1/teams/{team_id}/training_sessions",
            params={
                "since": f"{year1}-{month1}-{day1}T00:00:00",
                "until": f"{year2}-{month2}-{day2}T23:59:59",
                "per_page": "100",
            },
            headers=headers,
        )

        sessions_metadata = r.json()

        total_pages = sessions_metadata["page"]["total_pages"]

        if total_pages > 0:
            all_sessions = []
            for i in range(total_pages):
                r_new = requests.get(
                    f"https://teampro.api.polar.com/v1/teams/{team_id}/training_sessions?page={i}",
                    params={
                        "since": f"{year1}-{month1}-{day1}T00:00:00",
                        "until": f"{year2}-{month2}-{day2}T23:59:59",
                    },
                    headers=headers,
                )

                page_data = r_new.json()
                session_data = page_data["data"]
                all_sessions.append(session_data)

            # concatenate list of sessions
            flatten_list = lambda l: [item for sublist in l for item in sublist]
            all_sessions = flatten_list(all_sessions)
            sessions_metadata = all_sessions

            # df_sessions = pd.json_normalize(all_sessions)

        return sessions_metadata

    # Players

    def get_players_session_data(self, tokens, session_id):
        access_token = tokens["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + access_token,
        }
        r = requests.get(
            f"https://teampro.api.polar.com/v1/teams/training_sessions/{session_id}",
            params={},
            headers=headers,
        )
        session_data = r.json()

        return session_data

    def get_player_session_details(self, tokens, player_session_id):
        access_token = tokens["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + access_token,
        }
        r = requests.get(
            f"https://teampro.api.polar.com/v1/training_sessions/{player_session_id}",
            params={"samples": "all"},
            headers=headers,
        )
        player_session_details = r.json()

        return player_session_details

    def get_trimmed_player_session_details(self, tokens, player_session_id):
        access_token = tokens["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + access_token,
        }
        r = requests.get(
            f"https://teampro.api.polar.com/v1/training_sessions/{player_session_id}/session_summary",
            params={},
            headers=headers,
        )
        session_details = r.json()

        return session_details

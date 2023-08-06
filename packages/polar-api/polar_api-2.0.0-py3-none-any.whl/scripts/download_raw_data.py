import os
import json
import isodate
import pandas as pd


from ..api.polar_api import POLAR_API
from ..utilities.metadata import client_id, client_secret

# set variables
team_polar = 'Superliga'
date = input('Enter date (DD-MM-YYYY): ')

# Setup API
api = POLAR_API(client_id, client_secret, team=team_polar)
tokens = api.retrieve_tokens()
team_id = api.get_teams_info(tokens, get_team_id=True)

# Get players from the team
players = api.get_team_players(tokens, team_id)
df_players = pd.DataFrame(players['data']['players'])

# Extract metadata from sessions at specific date
sessions_metadata = api.get_sessions(tokens,
                                     team_id=team_id,
                                     date=date)
# Extract session ids
session_ids = []
for session_data in sessions_metadata['data']:
    session_id = session_data['id']
    session_ids.append(session_id)

# Extract and save session metadata
for session_id in session_ids:
    ## METADATA ##
    # get and save session metadata
    session_metadata = api.get_players_session_data(tokens, session_id)
    # add player names to metadata (only if exists in team players)
    participants = session_metadata['data']['participants']
    for i, player_data in enumerate(participants):
        player_id = player_data['player_id']
        # add player name if exists in polar else add NaN name
        if df_players['player_id'].str.contains(player_id).any():
            player_row = df_players[df_players['player_id'] == player_id]
            player_name = (player_row['first_name'] +
                           ' ' + player_row['last_name'])
            session_metadata['data']['participants'][i]['player_name'] = (player_name
                                                                          .item())
        else:
            session_metadata['data']['participants'][i]['player_name'] = 'NaN'

    # extract date and create folder if not exists
    session_date = isodate.parse_datetime(
        session_metadata['data']['record_start_time'])
    year, month, day, time = (session_date.year,
                              session_date.month,
                              session_date.day,
                              str(session_date.time()).replace(':', '-'))
    directory = f'data/{year}/{month}/{day}/{time}'
    if not os.path.exists(directory):
        os.makedirs(directory)
    # save metadata
    save_path_metadata = f'{directory}/{session_id}_metadata.json'

    ## RAW DATA ##
    # Extract and save player session raw data for all players in each session
    num_players = len(session_metadata['data']['participants'])
    for i in range(num_players-1):
        player_session_id = session_metadata['data']['participants'][i]['player_session_id']
        player_session_data = api.get_player_session_details(
            tokens, player_session_id)
        # save player raw data
        save_path_player_data = f'{directory}/{player_session_id}.json'
        with open(save_path_player_data, 'w') as outfile:
            json.dump(player_session_data, outfile)

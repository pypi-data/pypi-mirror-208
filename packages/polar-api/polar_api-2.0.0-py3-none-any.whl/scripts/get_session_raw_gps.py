# %%
import requests
import webbrowser
import base64
import json
import os
from datetime import datetime, timedelta
import pandas as pd

import api.polar_api_old as polar_api

# %%
## SCRIPT TO GET RAW GPS DATA FROM A TRAINING SESSION ##
tokens = polar_api.retrieve_tokens()
# Select team to get data from
team_id = polar_api.get_team_ids(tokens, 'U19')

# %%
# Choose training date or dates
session_date = input(
    'Choose session date or dates\n(e.g. "DD-MM-YYYY" or "DD-MM-YYYY to DD-MM-YYYY"):')

# If you want data from multiple dates
if 'to' in session_date:
    session_date = session_date.split(' to ')
    sessions = polar_api.get_sessions(tokens, team_id, date=session_date)

    # Convert first session date to datetime
    session_start_date = datetime.strptime(session_date[0], '%d-%m-%Y').date()
    session_end_date = datetime.strptime(session_date[1], '%d-%m-%Y').date()
    #delta_time = timedelta(days=1)

    # Get session ids from two dates
    session_ids = sessions['id']
    session_times = list(set([session['start_time'].split(
        'T')[0] for idx, session in sessions.iterrows()]))

    # Create list of dataframes for specific date
    session_dataframes = []
    for session_time in session_times:
        session_df = sessions[sessions['start_time'].str.contains(
            f'{session_time}')]
        session_dataframes.append(session_df)

    # Create dictionary of session time and session id
    session_id_dict = {}
    for idx in range(len(session_dataframes)):
        session_id_dict[session_times[idx]] = list(
            session_dataframes[idx]['id'].values)

    # Go through all sessions and get session gps data
    for idx, session_date in enumerate(polar_api.daterange(session_start_date, session_end_date)):
        session_date_clean = session_date.strftime('%Y-%m-%d')
        session_date_save_path = session_date.strftime('%d-%m-%Y')
        for session_id in session_id_dict[session_date_clean]:
            # Get all session ids from all dates
            player_session_ids = polar_api.get_player_session_ids(
                tokens, session_id)

            # Create empty folder of the session
            save_path = f'data/{session_date_save_path}_{session_id}'
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # Save raw GPS in folder created above - separate file for each player
            polar_api.get_all_player_session_details(tokens, player_session_ids, session_id,
                                                     save_as_csv=True, path=save_path)

# If you want data from a single date
else:
    try:
        sessions = polar_api.get_sessions(tokens, team_id, date=session_date)
        # Get session start so user can specify which session is requested
        session_start_times = list(sessions['start_time'].values)
        print('Choose training session from start time (1 or 2 or 3 etc.)')
        for idx, session_time in enumerate(session_start_times):
            print(f'{idx+1}: {session_time}')
        idx = input()  # get session number

        # Get session id
        session_id = sessions['id'][int(idx)-1]
        # Get individual session for each player in the session
        player_session_ids = polar_api.get_player_session_ids(
            tokens, session_id)

        # Create empty folder of session
        save_path = f'data/{session_date}_{session_id}'
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Save raw GPS in folder created above - separate file for each player
        polar_api.get_all_player_session_details(tokens, player_session_ids, session_id,
                                                 save_as_csv=True, path=save_path)

    except KeyError:
        print('Session date does not exists')

    except ValueError:
        print('Date is wrong format\nShould be e.g. "12-08-2020" or "08-08-2021 to 12-08-2021"')

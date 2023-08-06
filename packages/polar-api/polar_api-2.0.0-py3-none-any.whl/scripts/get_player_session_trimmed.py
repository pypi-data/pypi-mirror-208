#%%
import requests
import webbrowser
import base64
import json
import pandas as pd
import time

import polar_api

# Authorize and get access tokens from Polar API
tokens = polar_api.retrieve_tokens()
# Select team to get data from
team_id = polar_api.get_team_ids(tokens, 'Superliga')
sessions = polar_api.get_sessions(tokens, team_id, date="03-12-2021")
#%%
all_data = []
for session_id, start_time in zip(sessions['id'],sessions['start_time']):
    #get sessions ids for all players
    player_session_ids = polar_api.get_player_session_ids(tokens, session_id)
    
    #extract sessions data
    session_details = polar_api.get_all_player_session_details_trimmed(tokens, player_session_ids, team_id)
    #insert session start time
    session_details['start_date_time'] = start_time
    
    #add to list of training data
    all_data.append(session_details)
#%%
df = pd.concat(all_data)
save_name = 'u19_2021_midseason'
df.to_csv(f'../player_weekly_summary/data/2122_midseason/{save_name}.csv')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob


#path for the training data output folder containing all the CSVs
path = r'INSERTPATH'
all_files = glob.glob(path + "/*.csv")

df_from_each_file = (pd.read_csv(f) for f in all_files) #read each CSV into a df
df_training = pd.concat(df_from_each_file, ignore_index=True) #concat all the CSV data into one df

def time_to_sec(t): 
    """function to convert the duration xx:xx:xx to seconds"""
    h, m, s = map(float, t.split(':'))
    return h * 3600 + m * 60 + s

df_training["time_s"] = df_training['time'].apply(time_to_sec) #create a column with the duration in seconds
df_training = df_training.drop(columns=['session_type', 'name', 'time'])
df_training.set_index("time_s", inplace = True) #time in seconds column as an index


# Data exploration functions

def list_players():
    """returns the players' ID"""
    return list(df_training["player_id"].unique())

def count_players():
    """returns the number of players that took part in the session"""
    return len(list_players())

def session_len():
    """returns the session length in seconds"""
    return max(df_training.index)

def session_time():
    """returns the tuple (session start_time, session_end_time)"""
    return min(df_training['time_expanded']), max(df_training['time_expanded'])

def above_hr():
    """returns the anomalies in data - HR values above 205"""
    if len(df_training.loc[df_training['hr'] > 205]) == 0:
        return False
    else: 
        return df_training.loc[df_training['hr'] > 205]

def above_speed():
    """returns the anomalies in data - speed values above 10.5 m/s (37.8 km/h)"""
    if len(df_training.loc[df_training['speed'] > 37.8]) == 0:
        return False
    else:
        return df_training.loc[df_training['speed'] > 37.8]

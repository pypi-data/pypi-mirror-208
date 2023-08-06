#%%
# from polar_api import POLAR_API
import pandas as pd
import isodate


def hms_to_m(s):
    t = 0
    for u in s.split(":"):
        t = 60 * t + int(float(u))
    return int(t / 60)


def extract_team_id(teams_info, team):
    """
    teams_info -> json output from get_teams_info(tokens)
    """
    teams_data = teams_info["data"]
    for data in teams_data:
        if data["name"] == team:
            team_id = data["id"]

    return team_id


def extract_players(players_and_staff):
    # extract only players
    players = players_and_staff["data"]["players"]
    # convert to dataframe
    df_players = pd.json_normalize(players)
    # remove staff
    df_players = df_players[df_players["player_number"] < 100]
    map_positions = {
        "Målmand": "Goal Keeper",
        "Forsvar": "Centre Back",
        "Forsvarer": "Centre Back",
        "Midtbane": "Midfielder",
        "Angriber": "Attacker",
        "Goalkeeper": "Goal Keeper",
        "Defender": "Centre Back",
        "Midfielder": "Midfielder",
        "Striker or Forward": "Attacker",
        "Full Back": "Full Back",
        "Back": "Full Back",
        "Central Defender": "Centre Back",
        "Number 8": "Midfielder",
        "Number 6": "Midfielder",
        "Number 10": "Midfielder",
        "Number 9": "Attacker",
        "Winger": "Attacker",
        "None": "Goal Keeper",
    }
    df_players["role"] = df_players["role"].map(map_positions)
    df_players = df_players.dropna(subset=["role"])
    # df_players = df_players.dropna(inplace=True)

    return df_players


def get_day_sessions_name_id_dict(session_data):
    sessions_dict = {}
    for i in session_data["data"]:
        name = i["name"]
        date = str(i["record_start_time"].split("T")[0])
        start_time = str(i["record_start_time"].split("T")[1][:5])
        end_time = str(i["record_end_time"].split("T")[1][:5])
        session = name + " (" + date + ", " + start_time + "-" + end_time + ")"
        id = i["id"]
        sessions_dict[id] = session
    return sessions_dict


def get_interval_sessions_name_id_dict(sessions_data):
    df = pd.json_normalize(sessions_data)
    df["record_start_time"] = df.record_start_time.apply(
        lambda x: ", ".join(x.split("T"))[:-3]
    )
    df["record_end_time"] = df.record_end_time.apply(lambda x: x.split("T")[1][:-3])
    df["name"] = (
        df["name"] + " (" + df["record_start_time"] + "-" + df["record_end_time"] + ")"
    )
    sessions_dict = dict(zip(df["id"], df["name"]))
    return sessions_dict


def get_multiple_sessions_df_metadata(sessions_data):
    return pd.json_normalize(sessions_data)


def get_player_session_ids(session_data):
    participants = session_data["data"]["participants"]
    df_participants = pd.json_normalize(participants)
    # create dictionary of session ids and player ids
    player_ids = list(df_participants["player_id"])
    player_session_ids = list(df_participants["player_session_id"])

    zip_iterator = zip(player_ids, player_session_ids)
    session_ids_dict = dict(zip_iterator)
    return session_ids_dict


def clean_zone_df(df, zone):
    """Clean columns that are divided into zones (e.g. heart rate, acceleration, running distance)

    Args:
        df (DataFrame): DataFrame with Polar data to be cleaned
        zone (str): which zone to be cleaned, "hr", "speed" or "acceleration"

    Returns:
        DataFrame: clean dataframe
    """
    cols_to_drop = [
        "lower_limit_1",
        "lower_limit_2",
        "lower_limit_3",
        "lower_limit_4",
        "lower_limit_5",
        "higher_limit_1",
        "higher_limit_2",
        "higher_limit_3",
        "higher_limit_4",
        "higher_limit_5",
    ]
    hr_cols_to_keep = ["in_zone_1", "in_zone_2", "in_zone_3", "in_zone_4", "in_zone_5"]
    speed_cols_to_keep = [
        "in_zone_meters_1",
        "in_zone_meters_2",
        "in_zone_meters_3",
        "in_zone_meters_4",
        "in_zone_meters_5",
    ]
    if zone == "hr":
        cols_to_keep = hr_cols_to_keep
    elif zone == "speed":
        cols_to_keep = speed_cols_to_keep
    elif zone == "acceleration":
        # Convert row into columns
        df = df.pivot(index="player_session_id", columns="limit").reset_index()
        # Collapse columns
        df.columns = df.columns.to_flat_index()
        df.rename(columns=lambda x: "_".join(map(str, x)), inplace=True)
        return df
    else:
        print("Not a valid zone")
        return None
    # Convert row into columns
    df = df.pivot(index="player_session_id", columns="index").reset_index()
    # Collapse columns
    df.columns = df.columns.to_flat_index()
    df.rename(columns=lambda x: "_".join(map(str, x)), inplace=True)
    df.drop(cols_to_drop, axis=1, inplace=True)  # drop higher and lower limits
    # Parse times and rename columns
    if zone == "hr":
        for col in cols_to_keep:
            df[col] = df[col].apply(isodate.parse_duration)
            # Remove days from time zones
            df[col] = df[col].astype(str).str.split("0 days ").str[-1]
            # entries with 0 minutes show 0 days, thus replace with 00:00:00
            df[col].replace("0 days", "00:00:00", inplace=True)
    return df


def get_player_session_details_trimmed(trimmed_player_session_details):

    session_details = trimmed_player_session_details

    # Split columns with zones into multiple dataframe and merge them in get_all function
    # ------ Heart Rate Zones ------- #
    # heart_rate_zones	speed_zones_kmh	acceleration_zones_ms2
    df_hr_zones = pd.json_normalize(
        session_details["data"],
        record_path="heart_rate_zones",
        meta="player_session_id",
    )
    df_hr_zones = clean_zone_df(df_hr_zones, zone="hr")
    hr_cols = [
        "player_session_id",
        "Time in HR zone 1 (50 - 59 %)",
        "Time in HR zone 2 (60 - 69 %)",
        "Time in HR zone 3 (70 - 79 %)",
        "Time in HR zone 4 (80 - 89 %)",
        "Time in HR zone 5 (90 - 100 %)",
    ]
    df_hr_zones.columns = hr_cols
    # ------ Speed Zones ------- #
    df_speed_zones = pd.json_normalize(
        session_details["data"], record_path="speed_zones_kmh", meta="player_session_id"
    )
    df_speed_zones = clean_zone_df(df_speed_zones, zone="speed")
    speed_cols = [
        "player_session_id",
        "Distance in Speed zone 1 [m] (12.00 - 20.99 km/h)",
        "Distance in Speed zone 2 [m] (21.00 - 23.99 km/h)",
        "Distance in Speed zone 3 [m] (24.00 - 25.19 km/h)",
        "Distance in Speed zone 4 [m] (25.20 - 29.99 km/h)",
        "Distance in Speed zone 5 [m] (30.00- km/h)",
    ]
    df_speed_zones.columns = speed_cols
    # ------ Acceleration Zones ------- #
    df_acceleration_zones = pd.json_normalize(
        session_details["data"],
        record_path="acceleration_zones_ms2",
        meta="player_session_id",
    )
    df_acceleration_zones = clean_zone_df(df_acceleration_zones, zone="acceleration")
    acceleration_cols = [
        "player_session_id",
        "Number of accelerations (-50.00 - -9.00 m/s²)",
        "Number of accelerations (-8.99 - -6.00 m/s²)",
        "Number of accelerations (-5.99 - -3.00 m/s²)",
        "Number of accelerations (-2.99 - -0.50 m/s²)",
        "Number of accelerations (0.50 - 2.99 m/s²)",
        "Number of accelerations (3.00 - 5.99 m/s²)",
        "Number of accelerations (6.00 - 8.99 m/s²)",
        "Number of accelerations (9.00 - 50.00 m/s²)",
    ]
    df_acceleration_zones.columns = acceleration_cols

    # ---- Merge zones dataframes with original dataframe ----- #
    df_all_details = pd.json_normalize(session_details["data"])

    # Modify time columns (duration, start_time, end_time)
    df_all_details["trimmed_start_time"] = isodate.parse_datetime(
        df_all_details["trimmed_start_time"][0]
    )
    df_all_details["trimmed_start_time"] = df_all_details["trimmed_start_time"].dt.time
    df_all_details["duration_ms"] = pd.to_datetime(
        df_all_details["duration_ms"], unit="ms"
    ).dt.time
    # Calculate distance per min.
    df_all_details["distance_per_min"] = df_all_details[
        "distance_meters"
    ] / df_all_details["duration_ms"].astype(str).str.split(":").apply(
        lambda x: int(x[0]) * 60 + int(x[1])
    )
    # Calculate end time
    df_all_details["end_time"] = pd.to_timedelta(
        df_all_details["trimmed_start_time"].astype(str)
    ) + pd.to_timedelta(df_all_details["duration_ms"].astype(str))
    df_all_details["end_time"] = (
        df_all_details["end_time"].astype(str).str.split("0 days ").str[-1]
    )

    # Remove and rename columns
    df_all_details.drop(
        ["heart_rate_zones", "speed_zones_kmh", "acceleration_zones_ms2"],
        axis=1,
        inplace=True,
    )
    df_all = [
        df_all_details.set_index("player_session_id"),
        df_hr_zones.set_index("player_session_id"),
        df_speed_zones.set_index("player_session_id"),
        df_acceleration_zones.set_index("player_session_id"),
    ]

    df_final = pd.concat(df_all, axis=1).reset_index()
    # Drop and rename columns
    cols_to_drop = [
        "created",
        "modified",
        "player_session_id",
        "cadence_avg",
        "cadence_max",
    ]
    cols_to_rename = {
        "duration_ms": "Duration",
        "trimmed_start_time": "Start time",
        "end_time": "End time",
        "heart_rate_min": "HR min [bpm]",
        "heart_rate_avg": "HR avg [bpm]",
        "heart_rate_max": "HR max [bpm]",
        "heart_rate_min_percent": "HR min [%]",
        "heart_rate_avg_percent": "HR avg [%]",
        "heart_rate_max_percent": "HR max [%]",
        "distance_meters": "Total distance [m]",
        "distance_per_min": "Distance / min [m/min]",
        "speed_max_kmh": "Maximum speed [km/h]",
        "speed_avg_kmh": "Average speed [km/h]",
        "sprint_counter": "Sprints",
        "kilo_calories": "Calories [kcal]",
        "training_load": "Training load score",
    }
    df_final.drop(cols_to_drop, axis=1, inplace=True)
    df_final.rename(columns=cols_to_rename, inplace=True)

    # ------ Clean top speeds ------- #
    # df_top_speed = pd.read_csv('utils/top_speeds.csv')
    top_speed = 37
    df_final["Maximum speed [km/h]"] = df_final["Maximum speed [km/h]"].apply(
        lambda x: x if x <= top_speed else top_speed
    )

    # Calculate times in minutes
    # cols_to_convert = ['Duration', 'Time in HR zone 1 (50 - 59 %)', 'Time in HR zone 2 (60 - 79 %)',
    #                   'Time in HR zone 3 (80 - 84 %)', 'Time in HR zone 4 (85 - 94 %)', 'Time in HR zone 5 (95 - 100 %)']

    # df_final = pd.concat([df_final, df_converted])

    return df_final


def get_all_player_session_details_trimmed(player_session_ids):
    player_data_id_dct = {}
    for player_id, player_session_id in player_session_ids.items():
        player_data = api.get_trimmed_player_session_details(tokens, player_session_id)
        df_session_player = get_player_session_details_trimmed(player_data)
        df_session_player.insert(loc=0, column="player_id", value=player_id)
        player_data_id_dct[player_id] = df_session_player

    df_all_players = pd.concat(list(player_data_id_dct.values())).reset_index(drop=True)
    return df_all_players


def preprocess(data, set_date, team_players, session_name, account):

    data["Start time"] = set_date
    # data['Start time'] = data['Start time'].astype(str)
    # data['Start time'] = set_date + " " + data['Start time']
    # data['End time'] = set_date + " " + data['End time']

    id_df = team_players
    id_df["full_name"] = id_df["first_name"] + " " + id_df["last_name"]
    id_name = dict(zip(list(id_df["player_id"]), list(id_df["full_name"])))

    data["Player name"] = data["player_id"]
    data.replace({"Player name": id_name}, inplace=True)
    id_df = id_df[["player_id", "player_number"]]

    data = pd.merge(data, id_df, how="inner", on="player_id")
    data.rename(
        columns={"player_number": "Player number", "cardio_load": "Cardio load"},
        inplace=True,
    )
    data["Recovery time [h]"] = 0

    data["Session name"] = session_name
    data["Type"] = "Training"
    data["Phase name"] = "Whole session"

    if account == "M":
        data.rename(
            columns={
                "Time in HR zone 1 (50 - 69 %)": "Time in HR zone 1 (50 - 59 %)",
                "Time in HR zone 2 (60 - 69 %)": "Time in HR zone 2 (60 - 79 %)",
                "Time in HR zone 3 (70 - 79 %)": "Time in HR zone 3 (80 - 84 %)",
                "Time in HR zone 4 (80 - 89 %)": "Time in HR zone 4 (85 - 94 %)",
                "Time in HR zone 5 (90 - 100 %)": "Time in HR zone 5 (95 - 100 %)",
            },
            inplace=True,
        )

        # final_columns = list(template.columns.values)
        final_columns = [
            "Player number",
            "Player name",
            "Session name",
            "Type",
            "Phase name",
            "Duration",
            "Start time",
            "End time",
            "HR min [bpm]",
            "HR avg [bpm]",
            "HR max [bpm]",
            "HR min [%]",
            "HR avg [%]",
            "HR max [%]",
            "Time in HR zone 1 (50 - 59 %)",
            "Time in HR zone 2 (60 - 79 %)",
            "Time in HR zone 3 (80 - 84 %)",
            "Time in HR zone 4 (85 - 94 %)",
            "Time in HR zone 5 (95 - 100 %)",
            "Total distance [m]",
            "Distance / min [m/min]",
            "Maximum speed [km/h]",
            "Average speed [km/h]",
            "Sprints",
            "Distance in Speed zone 1 [m] (12.00 - 20.99 km/h)",
            "Distance in Speed zone 2 [m] (21.00 - 23.99 km/h)",
            "Distance in Speed zone 3 [m] (24.00 - 25.19 km/h)",
            "Distance in Speed zone 4 [m] (25.20 - 29.99 km/h)",
            "Distance in Speed zone 5 [m] (30.00- km/h)",
            "Number of accelerations (-50.00 - -9.00 m/s²)",
            "Number of accelerations (-8.99 - -6.00 m/s²)",
            "Number of accelerations (-5.99 - -3.00 m/s²)",
            "Number of accelerations (-2.99 - -0.50 m/s²)",
            "Number of accelerations (0.50 - 2.99 m/s²)",
            "Number of accelerations (3.00 - 5.99 m/s²)",
            "Number of accelerations (6.00 - 8.99 m/s²)",
            "Number of accelerations (9.00 - 50.00 m/s²)",
            "Calories [kcal]",
            "Training load score",
            "Cardio load",
            "Recovery time [h]",
            "Duration_min",
            "Time in HR zone 1 (50 - 59 %)",
            "Time in HR zone 2 (60 - 69 %)",
            "Time in HR zone 3 (70 - 79 %)",
            "Time in HR zone 4 (80 - 89 %)",
            "Time in HR zone 5 (90 - 100 %)",
        ]

        columns_before_calc = final_columns[:-6]
        data = data[columns_before_calc]

        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Duration"].astype(str).apply(hms_to_m), name="Duration_min"
                ),
            ],
            axis=1,
        )
        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Time in HR zone 1 (50 - 59 %)"].apply(hms_to_m),
                    name="Time in HR zone 1 (50 - 59 %)",
                ),
            ],
            axis=1,
        )
        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Time in HR zone 2 (60 - 79 %)"].apply(hms_to_m),
                    name="Time in HR zone 2 (60 - 69 %)",
                ),
            ],
            axis=1,
        )
        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Time in HR zone 3 (80 - 84 %)"].apply(hms_to_m),
                    name="Time in HR zone 3 (70 - 79 %)",
                ),
            ],
            axis=1,
        )
        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Time in HR zone 4 (85 - 94 %)"].apply(hms_to_m),
                    name="Time in HR zone 4 (80 - 89 %)",
                ),
            ],
            axis=1,
        )
        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Time in HR zone 5 (95 - 100 %)"].apply(hms_to_m),
                    name="Time in HR zone 5 (90 - 100 %)",
                ),
            ],
            axis=1,
        )
        data["Maximum speed [km/h]"] = data["Maximum speed [km/h]"].round(decimals=1)
        data["Average speed [km/h]"] = data["Average speed [km/h]"].round(decimals=1)

        columns_dec_0 = [
            "Total distance [m]",
            "Distance / min [m/min]",
            "Distance in Speed zone 1 [m] (12.00 - 20.99 km/h)",
            "Distance in Speed zone 2 [m] (21.00 - 23.99 km/h)",
            "Distance in Speed zone 3 [m] (24.00 - 25.19 km/h)",
            "Distance in Speed zone 4 [m] (25.20 - 29.99 km/h)",
            "Distance in Speed zone 5 [m] (30.00- km/h)",
        ]
        data[columns_dec_0] = data[columns_dec_0].round(decimals=0)
        data[columns_dec_0] = data[columns_dec_0].astype(int)

        data = data[
            [
                "Session name",
                "Start time",
                "Player name",
                "Duration",
                "Total distance [m]",
                "Distance in Speed zone 4 [m] (25.20 - 29.99 km/h)",
                "Distance in Speed zone 5 [m] (30.00- km/h)",
                "Sprints",
                "Number of accelerations (-50.00 - -9.00 m/s²)",
                "Number of accelerations (9.00 - 50.00 m/s²)",
                "Time in HR zone 4 (80 - 89 %)",
                "Time in HR zone 5 (90 - 100 %)",
                "Maximum speed [km/h]",
                "Duration_min",
            ]
        ]

        data = pd.merge(
            data,
            team_players[["full_name", "role"]],
            left_on="Player name",
            right_on="full_name",
        )
        data = data.drop(["full_name"], axis=1)
        data = data.rename(
            columns={
                "role": "position_name",
                "Player name": "athlete_name",
                "Duration_min": "Minutes",
                "Total distance [m]": "Total Distance",
            }
        )
        sum_hr = (
            data["Time in HR zone 4 (80 - 89 %)"]
            + data["Time in HR zone 5 (90 - 100 %)"]
        )
        data["HR (>85%)"] = sum_hr
        data = data.drop(
            ["Time in HR zone 4 (80 - 89 %)", "Time in HR zone 5 (90 - 100 %)"], axis=1
        )
        data = data[
            [
                "Session name",
                "Start time",
                "athlete_name",
                "position_name",
                "Minutes",
                "Total Distance",
                "Distance in Speed zone 4 [m] (25.20 - 29.99 km/h)",
                "Distance in Speed zone 5 [m] (30.00- km/h)",
                "Sprints",
                "Number of accelerations (-50.00 - -9.00 m/s²)",
                "Number of accelerations (9.00 - 50.00 m/s²)",
                "HR (>85%)",
                "Maximum speed [km/h]",
            ]
        ]

        data = data.set_index(["position_name", "athlete_name"])

    elif account == "W":

        data.rename(
            columns={
                "Time in HR zone 1 (50 - 59 %)": "Time in HR zone 1 (50 - 59 %).1",
                "Time in HR zone 2 (60 - 69 %)": "Time in HR zone 2 (60 - 69 %).1",
                "Time in HR zone 3 (70 - 79 %)": "Time in HR zone 3 (70 - 79 %).1",
                "Time in HR zone 4 (80 - 89 %)": "Time in HR zone 4 (80 - 89 %).1",
                "Time in HR zone 5 (90 - 100 %)": "Time in HR zone 5 (90 - 100 %).1",
            },
            inplace=True,
        )

        data.rename(
            columns={
                "Distance in Speed zone 1 [m] (12.00 - 20.99 km/h)": "Distance in Speed zone 1 [m] (10.00 - 17.99 km/h)",
                "Distance in Speed zone 2 [m] (21.00 - 23.99 km/h)": "Distance in Speed zone 2 [m] (18.00 - 20.99 km/h)",
                "Distance in Speed zone 3 [m] (24.00 - 25.19 km/h)": "Distance in Speed zone 3 [m] (21.00 - 23.99 km/h)",
                "Distance in Speed zone 4 [m] (25.20 - 29.99 km/h)": "Distance in Speed zone 4 [m] (24.00 - 26.99 km/h)",
                "Distance in Speed zone 5 [m] (30.00- km/h)": "Distance in Speed zone 5 [m] (27.00- km/h)",
            },
            inplace=True,
        )

        data.rename(
            columns={
                "Number of accelerations (-50.00 - -9.00 m/s²)": "Number of accelerations (-50.00 - -2.70 m/s²)",
                "Number of accelerations (-8.99 - -6.00 m/s²)": "Number of accelerations (-2.69 - -2.00 m/s²)",
                "Number of accelerations (-5.99 - -3.00 m/s²)": "Number of accelerations (-1.99 - -1.00 m/s²)",
                "Number of accelerations (-2.99 - -0.50 m/s²)": "Number of accelerations (-0.99 - -0.50 m/s²)",
                "Number of accelerations (0.50 - 2.99 m/s²)": "Number of accelerations (0.50 - 0.99 m/s²)",
                "Number of accelerations (3.00 - 5.99 m/s²)": "Number of accelerations (1.00 - 1.99 m/s²)",
                "Number of accelerations (6.00 - 8.99 m/s²)": "Number of accelerations (2.00 - 2.69 m/s²)",
                "Number of accelerations (9.00 - 50.00 m/s²)": "Number of accelerations (2.70 - 50.00 m/s²)",
            },
            inplace=True,
        )

        # final_columns = list(girls_template.columns.values)
        final_columns = [
            "Player number",
            "Player name",
            "Session name",
            "Type",
            "Phase name",
            "Duration",
            "Start time",
            "End time",
            "HR min [bpm]",
            "HR avg [bpm]",
            "HR max [bpm]",
            "HR min [%]",
            "HR avg [%]",
            "HR max [%]",
            "Time in HR zone 1 (50 - 59 %)",
            "Time in HR zone 2 (60 - 69 %)",
            "Time in HR zone 3 (70 - 79 %)",
            "Time in HR zone 4 (80 - 89 %)",
            "Time in HR zone 5 (90 - 100 %)",
            "Total distance [m]",
            "Distance / min [m/min]",
            "Maximum speed [km/h]",
            "Average speed [km/h]",
            "Sprints",
            "Distance in Speed zone 1 [m] (10.00 - 17.99 km/h)",
            "Distance in Speed zone 2 [m] (18.00 - 20.99 km/h)",
            "Distance in Speed zone 3 [m] (21.00 - 23.99 km/h)",
            "Distance in Speed zone 4 [m] (24.00 - 26.99 km/h)",
            "Distance in Speed zone 5 [m] (27.00- km/h)",
            "Training load score",
            "Cardio load",
            "Recovery time [h]",
            "Calories [kcal]",
            "Number of accelerations (-50.00 - -2.70 m/s²)",
            "Number of accelerations (-2.69 - -2.00 m/s²)",
            "Number of accelerations (-1.99 - -1.00 m/s²)",
            "Number of accelerations (-0.99 - -0.50 m/s²)",
            "Number of accelerations (0.50 - 0.99 m/s²)",
            "Number of accelerations (1.00 - 1.99 m/s²)",
            "Number of accelerations (2.00 - 2.69 m/s²)",
            "Number of accelerations (2.70 - 50.00 m/s²)",
            "Duration_min",
        ]
        # 'Time in HR zone 1 (50 - 59 %)',
        # 'Time in HR zone 2 (60 - 69 %)',
        # 'Time in HR zone 3 (70 - 79 %)',
        # 'Time in HR zone 4 (80 - 89 %)',
        # 'Time in HR zone 5 (90 - 100 %)']

        # columns_before_calc = final_columns[:-6]
        # data = data[columns_before_calc]

        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Duration"].astype(str).apply(hms_to_m), name="Duration_min"
                ),
            ],
            axis=1,
        )
        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Time in HR zone 1 (50 - 59 %).1"].apply(hms_to_m),
                    name="Time in HR zone 1 (50 - 59 %)",
                ),
            ],
            axis=1,
        )
        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Time in HR zone 2 (60 - 69 %).1"].apply(hms_to_m),
                    name="Time in HR zone 2 (60 - 69 %)",
                ),
            ],
            axis=1,
        )
        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Time in HR zone 3 (70 - 79 %).1"].apply(hms_to_m),
                    name="Time in HR zone 3 (70 - 79 %)",
                ),
            ],
            axis=1,
        )
        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Time in HR zone 4 (80 - 89 %).1"].apply(hms_to_m),
                    name="Time in HR zone 4 (80 - 89 %)",
                ),
            ],
            axis=1,
        )
        data = pd.concat(
            [
                data,
                pd.Series(
                    data["Time in HR zone 5 (90 - 100 %).1"].apply(hms_to_m),
                    name="Time in HR zone 5 (90 - 100 %)",
                ),
            ],
            axis=1,
        )
        data["Maximum speed [km/h]"] = data["Maximum speed [km/h]"].round(decimals=1)
        data["Average speed [km/h]"] = data["Average speed [km/h]"].round(decimals=1)
        columns_dec_0 = [
            "Total distance [m]",
            "Distance / min [m/min]",
            "Distance in Speed zone 1 [m] (10.00 - 17.99 km/h)",
            "Distance in Speed zone 2 [m] (18.00 - 20.99 km/h)",
            "Distance in Speed zone 3 [m] (21.00 - 23.99 km/h)",
            "Distance in Speed zone 4 [m] (24.00 - 26.99 km/h)",
            "Distance in Speed zone 5 [m] (27.00- km/h)",
        ]
        data[columns_dec_0] = data[columns_dec_0].round(decimals=0)
        data[columns_dec_0] = data[columns_dec_0].astype(int)

        data = data[
            [
                "Session name",
                "Start time",
                "Player name",
                "Duration",
                "Total distance [m]",
                "Distance in Speed zone 4 [m] (24.00 - 26.99 km/h)",
                "Distance in Speed zone 5 [m] (27.00- km/h)",
                "Sprints",
                "Number of accelerations (-50.00 - -2.70 m/s²)",
                "Number of accelerations (2.70 - 50.00 m/s²)",
                "Time in HR zone 4 (80 - 89 %)",
                "Time in HR zone 5 (90 - 100 %)",
                "Maximum speed [km/h]",
                "Duration_min",
            ]
        ]

        data = pd.merge(
            data,
            team_players[["full_name", "role"]],
            left_on="Player name",
            right_on="full_name",
        )
        data = data.drop(["full_name"], axis=1)
        data = data.rename(
            columns={
                "role": "position_name",
                "Player name": "athlete_name",
                "Duration_min": "Minutes",
                "Total distance [m]": "Total Distance",
            }
        )

        sum_hr = (
            data["Time in HR zone 4 (80 - 89 %)"]
            + data["Time in HR zone 5 (90 - 100 %)"]
        )
        data["HR (>85%)"] = sum_hr
        data = data.drop(
            ["Time in HR zone 4 (80 - 89 %)", "Time in HR zone 5 (90 - 100 %)"], axis=1
        )

        data = data[
            [
                "Session name",
                "Start time",
                "athlete_name",
                "position_name",
                "Minutes",
                "Total Distance",
                "Distance in Speed zone 4 [m] (24.00 - 26.99 km/h)",
                "Distance in Speed zone 5 [m] (27.00- km/h)",
                "Sprints",
                "Number of accelerations (-50.00 - -2.70 m/s²)",
                "Number of accelerations (2.70 - 50.00 m/s²)",
                "HR (>85%)",
                "Maximum speed [km/h]",
            ]
        ]

        data = data.set_index(["position_name", "athlete_name"])

    return data


def clean_df(df, volume=False, intensity=False):
    try:
        # remove goalkeepers
        df.drop("Goal Keeper", level=0, axis=0, inplace=True)
    except KeyError:
        df = df

    positions = df.index.get_level_values("position_name").unique()

    # calculate total distance in km
    # df["Total Distance"] = df["Total Distance"] / 1000

    # add average for team
    df.loc[("Avg. Team", "Avg. Team"), :] = df.mean(axis=0)

    # add average for groups
    df_group = df.groupby("position_name").mean().reset_index()
    df_group["athlete_name"] = "Åvg. Position"
    df_group = df_group.set_index(["position_name", "athlete_name"])
    for pos in positions:
        df.loc[(f"{pos}", f"Åvg. {pos}"), :] = df_group.loc[
            (f"{pos}", "Åvg. Position"), :
        ]

    # convert duration to minutes
    #     df["Minutes"] = df["Minutes"] / 60

    # format decimals
    if volume:
        df.iloc[:, :-1] = df.iloc[:, :-1].round(0)
        df.iloc[:, -1] = df.iloc[:, -1].round(1)
    if intensity:
        df.iloc[:, 0] = df.iloc[:, 0].round(0)
        df.iloc[:, 1:] = df.iloc[:, 1:].round(1)
    # df = df.round(1)

    # sort position
    position_order = ["Avg. Team", "Centre Back", "Full Back", "Midfielder", "Attacker"]
    df = df.reindex(position_order, axis=0, level=0)
    return df


# %%
# api = POLAR_API(client_id, client_secret, "U17")
# tokens = api.retrieve_tokens()
# team_info = api.get_teams_info(tokens)
# team_id = extract_team_id(team_info, "U17")
# session_data = api.get_session(tokens, team_id=team_id, date="04-10-2022")
# sessions_data = api.get_sessions(tokens, team_id=team_id, dates=['30-09-2022', '04-10-2022'])
# get_interval_sessions_name_id_dict(sessions_data)
# session = api.get_players_session_data(tokens, "lpxQW6pl")
# player_session_ids = get_player_session_ids(session)
# dt = api.get_trimmed_player_session_details(tokens,"xNNz4an5")
# x = get_all_player_session_details_trimmed(player_session_ids)

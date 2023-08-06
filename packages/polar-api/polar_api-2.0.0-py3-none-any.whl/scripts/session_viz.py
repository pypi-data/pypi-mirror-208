import os
import pandas as pd
import matplotlib.pyplot as plt
from scripts.load_s3 import load_from_s3
from datetime import datetime
from datetime import timedelta

def time_to_sec(t): #function to convert the duration from a xx:xx:xx format to seconds
    h, m, s = map(int, t.split(':'))
    return h * 3600 + m * 60 + s

def available_dates():
    """
    returns a list of all the recorded trainings uploaded to AWS S3
    """
    dates = []
    for i in df_all['Start time'].unique():
        dates.append(i[0:10])
    
    dates = sorted(list(set(dates)))
    print("Available dates:")
    for i in dates:
        print(i)

def timing_phases_dict():
    time_phases = {} #dictionary with the date, time as key and phase name as a value
    for i in (df_all['Start time'].unique()):
        time_phases.setdefault(i, set(df_all[df_all['Start time'] == i]["Phase name"]))
    return time_phases

def total_dst_phases_pie(date):
    
    """
    Input: date fx 14-02
    Output: pie chart, percentage of running distance per phase (total running distance/particular phase distance)
    """
    
    try:
        date_df = df_all.loc[df_all['Start time'].str.startswith(date)]
        title = "Training session " + str(date_df["Start time"][0][0:10]) + " | Percentage of total distance [m] per phase"
        events_lst = [x for x in date_df["Phase name"].unique() if x not in ["Helt trÃ¦ningspas"]]
        comb_data = {}

        for x,y in enumerate(events_lst):
            comb_data.setdefault(y, date_df.loc[date_df["Phase name"] == y]["Total distance [m]"].sum())  

        fig = plt.figure(figsize = (10,8), facecolor = 'white')
        plt.pie(comb_data.values(), labels = events_lst, autopct='%1.1f%%',  wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
        textprops={'size': '14', 'color':"black"});
        plt.title(label = title, color = "black", fontsize = 20)
    except:
        print("Error, no such date\n")
        available_dates()


def total_dst_bar_phases(date):
    """
    Input: date fx 14-02
    Output: horizontal bar chart, total team running distance [m] per phases
    
    """
    try:
        date_df = df_all.loc[df_all['Start time'].str.startswith(date)]
        title = "Training session " + str(date_df["Start time"][0][0:10]) + " | Team's total distance [m] per phase"
        events_lst = [x for x in date_df["Phase name"].unique() if x not in ["Helt trÃ¦ningspas"]]
        comb_data = {}

        for x,y in enumerate(events_lst):
            comb_data.setdefault(y, date_df.loc[date_df["Phase name"] == y]["Total distance [m]"].sum())  

        comb_data = dict(sorted(comb_data.items(), key=lambda item: item[1]))
        fig = plt.figure(figsize = (12,8))
        ax = fig.add_axes([0,0,1,1])
        ax.grid(color='grey', linestyle='-.', linewidth=0.5, alpha=0.2)
        ax.barh(list(comb_data.keys()), list(comb_data.values()), color=['red', 'purple', 'blue', 'green', 'orange', 'brown'])
        plt.rcParams.update({'font.size': 12})
        ax.set_title(title, fontsize = 19)
        plt.xlabel('Total distance [m]', fontsize = 16) 
        plt.ylabel('Phases', fontsize = 16) 
        for index, value in enumerate(comb_data.values()):
            plt.text(value, index, str(value))
    except:
        print("Error, no such date\n")
        available_dates()


def sprints_bar_phases(date):
    #need to remove the 0% values
    date_df = df_all.loc[df_all['Start time'].str.startswith(date)]
    comb_data = {}
    events_lst = [x for x in date_df["Phase name"].unique() if x not in ["Helt trÃ¦ningspas"]]
    title = "Training session " + str(date_df["Start time"][0][0:10]) + " | Percentage of total sprints per phase"
    
    for x,y in enumerate(events_lst):
        comb_data.setdefault(y, date_df.loc[date_df["Phase name"] == y]["Sprints"].sum())  
    
    fig = plt.figure(figsize = (10,8))
    plt.pie(comb_data.values(), labels = events_lst, autopct='%1.1f%%',  wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
    textprops={'size': '12', 'color':"white"}); #autopct=lambda p: '{:.1f}%'.format(round(p)) if p > 0 else '' //for 0% values
    plt.title(label = title, color = "white", fontsize = 20)


def sprints_bar_phases(date):
    """
    Input: date fx 14-02
    Output: bar chart, total running distance [m] per phases
    
    """
    
    date_df = df_all.loc[df_all['Start time'].str.startswith(date)]
    title = "Training session " + str(date_df["Start time"][0][0:10]) + " | Sprints per phase"
    events_lst = [x for x in date_df["Phase name"].unique() if x not in ["Helt trÃ¦ningspas"]]
    comb_data = {}
    
    for x,y in enumerate(events_lst):
        comb_data.setdefault(y, date_df.loc[date_df["Phase name"] == y]["Sprints"].sum())  
    
    comb_data = dict(sorted(comb_data.items(), key=lambda item: item[1]))
    fig = plt.figure(figsize = (10,7))
    ax = fig.add_axes([0,0,1,1])
    ax.grid(color='grey', linestyle='-.', linewidth=0.5, alpha=0.2)
    ax.barh(list(comb_data.keys()), list(comb_data.values()), color=['red', 'purple', 'blue', 'green', 'orange', 'brown'])
    plt.rcParams.update({'font.size': 12})
    ax.set_title(title, fontsize = 19)
    plt.xlabel('Phases', fontsize = 16) 
    plt.ylabel('No. of sprints', fontsize = 16) 
    for index, value in enumerate(comb_data.values()):
        plt.text(value, index, str(value))
    plt.show()
    

def total_dst_phases_pie(date):
    
    """
    Input: date fx 14-02
    Output: pie chart, percentage of running distance per phase (total running distance/particular phase distance)
    """
    
    date_df = df_all.loc[df_all['Start time'].str.startswith(date)]
    title = "Training session " + str(date_df["Start time"][0][0:10]) + " | Percentage of total distance [m] per phase"
#     day = str(data["Start time"][0][0:10]) # for title
    events_lst = [x for x in date_df["Phase name"].unique() if x not in ["Helt trÃ¦ningspas"]]
    comb_data = {}
    
    for x,y in enumerate(events_lst):
        comb_data.setdefault(y, date_df.loc[date_df["Phase name"] == y]["Total distance [m]"].sum())  
        
    fig = plt.figure(figsize = (10,8), facecolor = 'white')
    plt.pie(comb_data.values(), labels = events_lst, autopct='%1.1f%%',  wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
    textprops={'size': '15', 'color':"black"});
    plt.title(label = title, color = "black", fontsize = 20)
    plt.show()


if __name__ == "__main__":

    print("AWS_ACCESS_KEY_ID:")
    os.environ['AWS_ACCESS_KEY_ID'] = input()

    print("AWS_SECRET_ACCESS_KEY:")
    os.environ['AWS_SECRET_ACCESS_KEY'] = input()

    aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
    bucket = 'training-data-fcn-s3'

    team_aws = input('Choose folder name: ')

    # Load data from AWS S3
    df_all = load_from_s3(aws_access_key, aws_secret_access_key,
                      bucket, team_aws)

    df_all.drop(columns=['Player number', 'Session name', 'Type']); #drop the unnecessary columns

    ## ----- CALCULATE METRICS ----- ##
    dist21_cols = ['Distance in Speed zone 3 [m] (21.00 - 23.99 km/h)',
               'Distance in Speed zone 4 [m] (24.00 - 26.99 km/h)',
               'Distance in Speed zone 5 [m] (27.00- km/h)']
    df_all['dist21'] = df_all[dist21_cols].sum(axis=1)

    # calculate sum of different phases
    cols = ['Total distance [m]', 'Sprints', 'dist21',
        'Number of accelerations (2.70 - 50.00 m/s²)']
    df_calc = df_all.groupby('Phase name')[cols].sum()
   

    df_all["Duration_s"] = df_all['Duration'].apply(time_to_sec) #create a new column, duration in seconds

    total_dst_phases_pie("31-01")

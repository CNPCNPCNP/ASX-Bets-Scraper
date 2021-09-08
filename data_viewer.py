"""
Created on Thu Sep  2 10:32:05 2021
@author: clayh
"""
import pandas as pd
import datetime as dt
import os

#Global variable for the data folder path as we re-use it a lot, and it should
#never change
PATH = os.path.dirname(__file__) + '\\data'

def plot_asx_summary_data(asx_df: pd.DataFrame) -> None:
    """Takes a summary dataframe and plots ticker mentions over time. Filters 
    out tickers that aren't mentioned at all"""
    new_df = collapse_full_df(asx_df)
    print(new_df)
    new_df.plot(kind = 'line')
    return None

def collapse_full_df(asx_df: pd.DataFrame) -> pd.DataFrame:
    """Takes a summary dataframe and deletes all the entries which have 0
    mentions over the time period"""
    for i in asx_df.columns:
        if asx_df[i].all() == 0:
            asx_df.drop(labels = i, axis = 1, inplace = True)
    return asx_df

def export_df_summary(asx_df_summary: pd.DataFrame, start_date, end_date) -> None:
    start_date = start_date.strftime('%d_%m_%y')
    end_date = end_date.strftime('%d_%m_%y')
    title = 'summary_'
    asx_df_summary.to_csv(os.path.join(PATH, title + start_date + '-' + 
                                       end_date + '.csv'))
    
def export_counter(asx_df_dict: dict) -> None:
    """Takes a pandas dataframe (ideally after the count of each ticker has 
    been updated) and exports this to a CSV file to be viewed/edited further"""
    for i in asx_df_dict.keys():
        date = i.strftime('%d_%m_%y')
        title = 'companies_counter_'
        asx_df_dict[i].to_csv(os.path.join(PATH, title + date + '.csv'))
    return None

def file_name_list_checker() -> list:
    """Checks the data folder for any asx summary files, returns a list giving
    all the names of these files"""
    summary_list = []
    for file in os.listdir(PATH):
        if file.startswith('summary'):
            summary_list.append(file)
    return summary_list

def df_reader(file_name: str) -> pd.DataFrame:
    """Takes a file_name specified and returns this dataframe from the data
    folder"""
    asx_df = pd.read_csv(PATH + '\\' + file_name, index_col = 0)
    return asx_df

def asx_summary_reader(files: list):
    """Takes a list of file names and returns a list of dataframes"""
    df_list = []
    for file in files:
        df_list.append(df_reader(file))
    return df_list

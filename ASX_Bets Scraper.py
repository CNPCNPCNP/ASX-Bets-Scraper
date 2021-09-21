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
    mentions over the time period
    for column in asx_df.columns:
        if asx_df[column].all() == 0:
            asx_df.drop(labels = column, axis = 1, inplace = True)
            """
    asx_df = asx_df.loc[:,~(asx_df == 0).all(axis = 0)]
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

def date_grabber(file_name: str) -> dt.datetime:
    """Subroutine for asx_summary_reader functionakes a file name for a summary 
    dataframe and grabs the start date of the summary"""
    date = file_name.strip('summary_')[:8]
    date = dt.datetime.strptime(date, '%d_%m_%y').date()
    return date

def asx_summary_reader(files: list) -> dict:
    """Takes a list of file names and returns a dictionary of start date and
    summary dataframes"""
    df_list = {}
    for file in files:
        df_list[date_grabber(file)] = df_reader(file)
    return df_list

def flat_summary(start_date = dt.date(2021, 8, 16), end_date = dt.date.today()) -> pd.DataFrame:
    """Takes two dates, and returns a dataframe which first concatenates then
    removes all extraneous rows from the dataset
    
    Keyword arguments default this function to get every single date, however
    can be specified by user if needed"""
    new_df_list = []
    
    #Create our list of dataframes to merge together, then merge them
    full_df_list = asx_summary_reader(file_name_list_checker())
    for df in full_df_list:
        print (start_date, df, end_date)
        if start_date <= df <= end_date:
            new_df_list.append(full_df_list[df])
    new_df = pd.concat(new_df_list)
    
    #Take merged dataframe, sort it by date and delete empty rows
    new_df = new_df.sort_index()
    #~(new_df == 0) creates a boolean dataframe when all values in column are 0
    new_df = collapse_full_df(new_df)
    #new_df = new_df.loc[:,~(new_df == 0).all(axis = 0)]
    
    return new_df

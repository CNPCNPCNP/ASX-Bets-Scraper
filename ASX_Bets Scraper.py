"""
Created on Thu Aug 19 10:12:25 2021
@author: clayh
"""

import praw
import matplotlib as plt
import pandas as pd
import datetime as dt
import string
from psaw import PushshiftAPI

def __init__() -> None:
    """Starts the program and will contain test code. """
    a = date_ticker_counter(dt.date(2021, 8, 23), dt.date(2021, 8, 27))
    export_counter(a)
    b = summary_asx_data(a)
    export_df_summary(b)
    #c = test_dataframe()
    plot_asx_summary_data(b)
    return None

def test_dataframe() -> pd.DataFrame:
    """Loads a pre defined dataframe to save time when testing"""
    return pd.read_csv(r'C:\Users\clayh\Documents\Projects\ASX Bets Scraper\companies_summary.csv', index_col = 0)

def asx_companies() -> pd.DataFrame:
    """Loads the CSV containing all the ASX listed companies and their share code/name. Returns a dataframe"""
    #asx_companies = pd.read_csv(r'C:\Users\clayh\Documents\Projects\ASX Bets Scraper\companies.csv', index_col = 0)
    #asx_companies = pd.read_csv(r'C:\Users\Clay\Documents\ASX Bets Scraper\companies.csv', index_col = 0)
    asx_companies = pd.read_csv('companies.csv', index_col = 0)
    return asx_companies

def reddit():
    """Contains the data from my reddit application that allows me to scrape data using
    reddit's inbuilt API. It returns my login details which can be accessed by other functions"""
    reddit = praw.Reddit(client_id='hRX-iBVQQJ02lMhEYRMEfA', client_secret='gfr8A7RqQ8ZSBr8mBkZIXkS9LePUnQ', 
                     user_agent='clay_scraper')
    return reddit

def submission_id_list(start_date: dt.date, end_date = dt.date.today()) -> list:
    """Takes a start date, returns all the needed post ids from the pre-market, daily discussion and weekend
    discussion from the reddit automoderator who posts them on ASX_bets after this date. First creates a
    generator object which we then convert into a list. Elements of the list can then be fed into comment_scrape
    as needed. Can take optional argument of end date to find submissions between certain dates, otherwise this
    defaults to today. Returns the list, as well as the start and end dates used. 
    
    Uses the pushshift wrapper psaw to accomplish this as the basic reddit API does not have these features"""
    submission_list = []
    day_s, month_s, year_s = start_date.day, start_date.month, start_date.year
    end_date += dt.timedelta(1) #This is done because the list is not inclusive of today's date, 
                                #ends on beginning of next day
    day_f, month_f, year_f = end_date.day, end_date.month, end_date.year #Dirty hack because I suck at datetime
    start_epoch = int(dt.datetime(year_s, month_s, day_s).timestamp())
    end_epoch = int(dt.datetime(year_f, month_f, day_f).timestamp())
    api = PushshiftAPI(reddit())
    submission_ids = api.search_submissions(after = start_epoch, 
                                 before = end_epoch,
                                 subreddit = 'asx_bets',
                                 #author = 'AutoModerator',
                                 limit=1000)
    for i in submission_ids:
        submission_list.append(i)
    print (submission_list)
    return(submission_list)
    
def comment_scrape(post_id: str) -> list:
    """Takes a post_id as a string and returns a full list of all the comments in a post"""
    comment_list = []
    submission = reddit().submission(id=post_id)
    submission.comments.replace_more(limit=0) #replace_more method means that all top level comments are accessed
    for comment in submission.comments.list(): #list method takes lower level comments as well
        comment_list.append(comment.body)
    return comment_list

def ticker_mention_counter(submission_ids: list) -> pd.DataFrame:
    """Takes a list of submission ids, creates a dataframe containing tickers and how many times they were mentioned"""
    asx_df = asx_companies()
    banned_list = ('ATH', 'ATM', 'BUY', 'ASX', 'ETF')
    for submission in submission_ids:
        cmts = comment_scrape(submission)
        for comment in cmts:
            fixed_cmt = comment.translate(str.maketrans('', '', string.punctuation)) #strips out all punctuation
            for i in fixed_cmt.split(): 
                if len(i) < 6 and i not in banned_list and asx_df['Code'].eq(i).any(): #checks not in banned list first 
                                                                                       #as that is a shorter list                                
                    asx_df.loc[i, 'Count'] += 1
    return asx_df

def date_ticker_counter(start_date: dt.date, end_date = dt.date.today()) -> dict:
    """Takes a start and end date, creates an iterable list of dates inclusive of start and end date. Uses this to 
    generate a dataframe of ticker mentions for each particular date in the list of dates. Returns this as a dict"""
    sd = start_date
    ed = end_date
    asx_df_dict = {}
    delta = dt.timedelta(days=1)
    while sd <= ed:
        submissions_on_date = submission_id_list(sd, sd) #By checking from start date to start date we check only on
                                                         #that particular date
        asx_df = ticker_mention_counter(submissions_on_date)
        asx_df_dict[sd] = asx_df
        sd += delta
    return asx_df_dict

def summary_asx_data(asx_df_dict: dict) -> pd.DataFrame:
    """Takes a dictionary of dates vs asx ticker count dataframes from that day. Returns a single
    dataframe that contains every ticker and the number of mentions on each date"""
    data_list = []
    dataframe_length = len(asx_companies().index)
    row_dates = asx_df_dict.keys()
    tickers = list(asx_companies().index)
    for asx_df in asx_df_dict.values():
        count = 0
        value_list = []
        while count < dataframe_length:
            value_list.append(asx_df.iat[count, 2])
            count+= 1
        data_list.append(value_list)
    summary_asx_df = pd.DataFrame(data_list, index = row_dates, columns = tickers)
    return summary_asx_df

def plot_asx_summary_data(asx_df: pd.DataFrame) -> None:
    """Takes a summary dataframe and plots ticker mentions over time. Filters out tickers that aren't mentioned at all"""
    new_df = asx_df
    for i in new_df.columns:
        if new_df[i].all() == 0:
            new_df.drop(labels = i, axis = 1, inplace = True)
    print(new_df)
    new_df.plot(kind = 'line')
    return None

def export_df_summary(asx_df_summary: pd.DataFrame) -> None:
    #path = r'C:\Users\clayh\Documents\Projects\ASX Bets Scraper\companies_summary' #on laptop
    #path = r'C:\Users\Clay\Documents\ASX Bets Scraper\companies_summary' #on desktop
    path = 'companies_summary'
    asx_df_summary.to_csv(path + '.csv')
    
def export_counter(asx_df_dict: dict) -> None:
    """Takes a pandas dataframe (ideally after the count of each ticker has been updated) and exports this to a CSV file
    to be viewed/edited further"""
    for i in asx_df_dict.keys():
        date = i.strftime('%d_%m_%y')
        #path = r'C:\Users\clayh\Documents\Projects\ASX Bets Scraper\companies_counter_' #on laptop
        #path = r'C:\Users\Clay\Documents\ASX Bets Scraper\companies_counter_' #on desktop
        path = 'companies_counter_'
        asx_df_dict[i].to_csv(path + date + '.csv')
    return None

__init__()
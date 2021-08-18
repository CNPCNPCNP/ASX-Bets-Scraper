# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 14:29:01 2021

@author: Clay
"""

import praw
import pandas as pd
import datetime as dt
import string
from psaw import PushshiftAPI

def __init__():
    """Starts the program and will contain test code. """
    a = submission_id_list(dt.date(2021, 8, 18))
    b = ticker_mention_counter(a)
    export_counter(b)

def asx_companies() -> pd.DataFrame:
    """Loads the CSV containing all the ASX listed companies and their share code/name. Returns a dataframe"""
    asx_companies = pd.read_csv(r'C:\Users\Clay\Documents\ASX Bets Scraper\companies.csv', index_col = 0)
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
                                 author = 'AutoModerator',
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
            print (fixed_cmt)
            for i in fixed_cmt.split(): 
                if len(i) < 6 and i not in banned_list and asx_df['Code'].eq(i).any(): #checks not in banned list first 
                                                                                       #as that is a shorter list                                
                    asx_df.loc[i, 'Count'] += 1
    return asx_df

def export_counter(asx_df: pd.DataFrame, date = dt.date.today()):
    """Takes a pandas dataframe (ideally after the count of each ticker has been updated) and exports this to a CSV file
    to be viewed/edited further"""
    sorted_df = asx_df.sort_values('Count', ascending = False)
    sorted_df.to_csv(r'C:\Users\Clay\Documents\ASX Bets Scraper\companies_counter.csv')

__init__()
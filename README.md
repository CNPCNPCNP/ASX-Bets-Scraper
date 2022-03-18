# ASX-Bets-Scraper
Scrapes ASX Bets for ticker mentions

User will need to have PRAW (Python reddit API wrapper, 
https://praw.readthedocs.io/en/stable/) and PSAW (Python pushshift.io API 
wrapper, https://psaw.readthedocs.io/en/latest/) installed in able to use this 
script. The user will also need pandas.

Can take quite a long time to scrape especially if the user decides to scrape 
all threads and not just the daily discussion. Once data is scraped, the data 
is saved in csv files on the user's computer for further data analysis if 
necessary. 
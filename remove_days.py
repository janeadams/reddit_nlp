import os
from os import walk
import pandas as pd
import progressbar
import numpy as np

from data import *

process_start_time = time.time()

def get_removal_list(datelist):
    remove_dates = []
    for date in datelist:
        date_time = datetime.datetime.strptime(date, '%Y-%m-%d')
        if start_time <= date_time <= end_time:
            remove_dates.append(date)
    return remove_dates

def remove_files():
    print()
    print(f'Removing r/{subreddit} post, token, and wordcounts from {start_date} to {end_date}...')
    
    for folder in ['posts','tokens','wordcounts']:
        datelist = get_dirs(f'subreddits/{subreddit}/data/{folder}')
        remove_dates = get_removal_list(datelist)
        for folder_date in datelist:
            try:
                os.rmdir(f'subreddits/{subreddit}/data/{folder}/{folder_date}')
            except:
                print(f'subreddits/{subreddit}/data/{folder}/{folder_date} does not exist' )
                #pass
            print(f'Removed {len(remove_dates)} days from {subreddit} {folder} folder')
                        
    wordcount_dates = get_files(f'subreddits/{subreddit}/data/wordcounts/')
    remove_dates = get_removal_list(wordcount_dates)
    try:
        os.remove(f'subreddits/{subreddit}/data/wordcounts/{post_date}.csv')
    except:
        pass
    print(f'Removed {len(remove_dates)} days from {subreddit} wordcount data')
    return remove_dates

def remove_aggregate_counts(aggnames):
    for agg in aggnames:
        print()
        print(f'Removing r/{subreddit} {agg} counts from {start_date} to {end_date}...')
        df = pd.read_csv(f'subreddits/{subreddit}/data/{agg}_counts.csv', names=['date', agg])
        remove_dates = get_removal_list(df['date'])
        filtered = df[~df['date'].isin(remove_dates)].sort_values(by='date').set_index('date')
        filtered.to_csv(f'subreddits/{subreddit}/data/{agg}_counts.csv', header=False)
    
    
def remove_ngram_entries():
    print()
    print(f'Removing r/{subreddit} ngram entries from {start_date} to {end_date}...')
    ngrams = get_files(f'subreddits/{subreddit}/data/ngrams')
    for ngram in progressbar.progressbar(ngrams, redirect_stdout=True):
        df = pd.read_csv(f'subreddits/{subreddit}/data/ngrams/{ngram}.csv', names=['date', 'count', 'freq'])
        remove_dates = get_removal_list(df['date'])
        filtered = df[~df['date'].isin(remove_dates)].sort_values(by='date')
        filtered.to_csv(f'subreddits/{subreddit}/data/ngrams/{ngram}.csv', header=False)
    
print("Which subreddit (case-sensitive) would you like to filter? (Don't include 'r/'):")
print(f'Subreddits available: {get_dirs("subreddits/")}')
subreddit = input()

print()
print('Enter start date in the format YYYY-MM-DD:')
start_date = input()
start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')

print()
print('Enter end date in the format YYYY-MM-DD:')
end_date = input()
end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    
remove_files()

remove_aggregate_counts(['post','token'])

remove_ngram_entries()

try:
    new_datelist = get_dirs(f'subreddits/{subreddit}/data/posts')
    summarize_wordcounts(new_datelist[0], new_datelist[-1], subreddit, process_start_time)
except:
    print(f'Error summarizing new wordcounts')

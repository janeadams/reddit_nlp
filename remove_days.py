import os
from os import walk
import pandas as pd
import progressbar
import numpy as np

from data import *

process_start_time = time.time()

def remove_files():
    print()
    print(f'Removing r/{subreddit} post, token, and wordcounts from {start_date} to {end_date}...')
    remove_dates = []
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    post_dates = get_dirs(f'subreddits/{subreddit}/data/posts')
    for post_date in progressbar.progressbar(post_dates, redirect_stdout=True):
        post_time = datetime.datetime.strptime(post_date, '%Y-%m-%d')
        if start_time <= post_time <= end_time:
            remove_dates.append(post_date)
            for folder in [f'subreddits/{subreddit}/data/posts/{post_date}',
                         f'subreddits/{subreddit}/data/tokens/{post_date}',
                         f'subreddits/{subreddit}/data/wordcounts/{post_date}'
                        ]:
                try:
                    os.rmdir(folder)
                except:
                    print(f'{folder} does not exist' )
                    #pass
            try:
                os.remove(f'subreddits/{subreddit}/data/wordcounts/{post_date}.csv')
            except:
                pass
    print(f'Removed {len(remove_dates)} days from {subreddit} post, token, and wordcount data')
    return remove_dates
    
def remove_ngram_entries():
    print()
    print(f'Removing r/{subreddit} ngram entries from {start_date} to {end_date}...')
    ngrams = get_files(f'subreddits/{subreddit}/data/ngrams')
    for ngram in progressbar.progressbar(ngrams, redirect_stdout=True):
        df = pd.read_csv(f'subreddits/{subreddit}/data/ngrams/{ngram}.csv', names=['date', 'count', 'freq'])
        filtered = df[~df['date'].isin(remove_dates)]
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
    
remove_dates = remove_files()

remove_ngram_entries()

new_datelist = get_dirs(f'subreddits/{subreddit}/data/posts')

summarize_wordcounts(new_datelist[0], new_datelist[-1], subreddit, process_start_time)

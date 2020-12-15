import json
import requests
import datetime
from psaw import PushshiftAPI
import time

from data import *

process_start_time = time.time()

try: os.mkdir(f'subreddits')
except: print(f'subreddits/ directory exists')

print('Setting up psaw API connection...')
print('Learn more about psaw here: https://github.com/dmarx/psaw')
api = PushshiftAPI()
print()
print("Which subreddit (case-sensitive) would you like to query? (Don't include 'r/'):")
subreddit = input()
print()
print(f"Great! We'll search the Pushshift API for posts to r/{subreddit}")
      
try: os.mkdir(f'subreddits/{subreddit}')
except: print(f'subreddits/{subreddit} directory exists')
try: os.mkdir(f'subreddits/{subreddit}/data')
except: print(f'subreddits/{subreddit}/data/ directory exists')
try: os.mkdir(f'subreddits/{subreddit}/data/posts')
except: print(f'subreddits/{subreddit}/data/posts directory exists')
    
with open(f'subreddits/{subreddit}/data/post_counts.csv', 'w') as csvfile:
    pass

with open(f'subreddits/{subreddit}/data/token_counts.csv', 'w') as csvfile:
    pass

print()
print('Enter start date in the format YYYY-MM-DD:')
start = input()

print()
print('Enter end date in the format YYYY-MM-DD:')
end = input()

print()
print("Only save ngrams that are used more than X times (recommended entry: 1-4; enter 0 to save all)")
threshold = int(input())

get_days(start, end, subreddit, api, process_start_time)
 
tokenize_files(start, end, subreddit, process_start_time)
  
count_words(start, end, subreddit, process_start_time)
    
summarize_wordcounts(start, end, subreddit, process_start_time)

get_ngrams(start, end, subreddit, process_start_time, threshold)

process_elapsed_time = time.time() - process_start_time
print()
print('--- Finished process! ---')
print(f'Elapsed time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')
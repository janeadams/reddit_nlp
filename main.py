import json
import requests
import datetime
from psaw import PushshiftAPI
import time

from data import *

process_start_time = time.time()

print('Setting up psaw API connection...')
print('Learn more about psaw here: https://github.com/dmarx/psaw')
api = PushshiftAPI()
print()
print("Which subreddit (case-sensitive) would you like to query? (Don't include 'r/'):")
subreddit = input()
print()
print(f"Great! We'll search the Pushshift API for posts to r/{subreddit}")
      
try: os.mkdir(f'{subreddit}')
except: print(f'{subreddit} directory exists')
try: os.mkdir(f'{subreddit}/data')
except: print(f'{subreddit}/data/ directory exists')
try: os.mkdir(f'{subreddit}/data/posts')
except: print(f'{subreddit}/data/posts directory exists')
    
with open(f'{subreddit}/data/post_counts.csv', 'w') as csvfile:
    pass

with open(f'{subreddit}/data/token_counts.csv', 'w') as csvfile:
    pass

print()
print('Enter start date in the format YYYY-MM-DD:')
start = input()

print()
print('Enter end date in the format YYYY-MM-DD:')
end = input()

get_days(start, end, subreddit, api, process_start_time)
 
tokenize_files(start, end, subreddit, process_start_time)
  
count_words(start, end, subreddit, process_start_time)

get_ngrams(start, end, subreddit, process_start_time)
    
summarize_wordcounts(start, end, subreddit, process_start_time)

process_elapsed_time = time.time() - process_start_time
print()
print('--- Finished process! ---')
print(f'Elapsed time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')

print()
print('Do you want to open the ngram visualizer? [Y/n]')
reply = input()

if reply.lower() == 'y':
    from dashboard import *
    visualize(subreddit)
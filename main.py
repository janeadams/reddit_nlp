import json
import requests
import datetime
import os
from os import walk
import pickle
import csv
import pandas as pd
import nltk
import time
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.probability import FreqDist

process_start_time = time.time()

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

print()
print('Enter start date in the format YYYY-MM-DD:')
start = input()

print()
print('Enter end date in the format YYYY-MM-DD:')
end = input()

all_data = {}
post_data = {}
not_recorded = {}

def get_files(path):
    files = []
    for (dirpath, dirnames, filenames) in walk(path):
        files.extend(filenames)
    str_files = [str(f) for f in files]
    return str_files

def get_dirs(path):
    directories = []
    for (dirpath, dirnames, filenames) in walk(path):
        directories.extend(dirnames)
    str_directories = [str(d) for d in directories]
    return str_directories

def get_days(start_date, end_date):
    function_start_time = time.time()
    # Convert dates to datetime format
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    # Advance one day at a time
    delta = datetime.timedelta(days=1)
    while start_time <= end_time:
        cached=False
        # Convert to integer epoch for querying Pushshift API
        after_epoch = int(start_time.timestamp())
        before_epoch = int((start_time + delta).timestamp())
        # Format current query date as string (for file naming, etc.)
        date = start_time.date().strftime("%Y-%m-%d")
        if date in get_dirs(f'{subreddit}/data/posts/'):
            cached=True
            print(f'{date} already in data folder; skipping API query')
        if not cached:
            URL = f'https://api.pushshift.io/reddit/search/submission/?subreddit={subreddit}&size=100&before={before_epoch}&after={after_epoch}&fields=selftext,id'
            print()
            print(f'Querying r/{subreddit} for posts on {date}...')
            try:
                # Query API, specifying subreddit and time epoch
                r = requests.get(URL).json()
                post_count = len(r["data"])
                print(f'Number of posts: {post_count}/100 on {date}')
                # Create a posts folder for each date
                try:
                    os.mkdir(f'{subreddit}/data/posts/{date}')
                except:
                    #print(f'{date} folder exists')
                    pass
                removed = 0
                for post_obj in r['data']: # For each post
                    n = post_obj['id']
                    try:
                        post_text = post_obj['selftext'] # Get the raw text of the post
                        if len(post_text)>1:
                            file = open(f'{subreddit}/data/posts/{date}/{n}.txt',"w") # Save it in a text file
                            file.write(post_text)
                            file.close()
                        else:
                            removed+=1
                    except:
                        print(f'Error saving post data from r/{subreddit} API response on {date} id {n}.')
                        print(f'Find detailed post data here: https://api.pushshift.io/reddit/search/submission/?ids={n}')
                if removed > 0:
                    print(f'{removed}/{post_count} posts from {date} have since been removed')
                try:
                    with open(f'{subreddit}/data/post_counts.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([date,post_count])
                except:
                    print(f'Error writing post count for {date} to file {f"{subreddit}/data/post_counts.csv"}')
            except:
                if requests.get(URL).text[0] == "<":
                    print('HTML ERR RESPONSE')
                    with open(f'{subreddit}/data/post_counts.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([date,'HTML_ERR'])
                    print(f'HTML Error querying r/{subreddit} on {date}.')
                    print(f"It's possible that the server is just temporarily down or timed out;")
                    print(f'If this is the case, the backfill() function should catch this missing date later and fill it in')
                else:
                    not_recorded[date]=URL
                    print(f'NON-html error querying r/{subreddit} on {date}. Check the URL for errors:')
                    print(f'{URL}')
                    print(f"It's possible that the JSON file is corrupted (e.g. double-quotes or emoticons are not escaped)")
        start_time += delta
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print()
    print(f'--- Finished querying r/{subreddit} API ---')
    print(f'Elapsed query function time: {np.around(function_elapsed_time, 1)}s ({np.around(function_elapsed_time/60, 2)} minutes)')
    print(f'Elapsed process time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')
        
get_days(start, end)
        
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))
nltk.download('punkt', quiet=True)
tokenizer = RegexpTokenizer(r'\w+')

def tokenize_files(start_date, end_date):
    print(f'Tokenizing post files for {start_date} to {end_date}...')
    function_start_time = time.time()
    try: os.mkdir(f'{subreddit}/data/tokens')
    except: print(f'{subreddit}/data/tokens directory exists')
    # Convert dates to datetime format
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    # Advance one day at a time
    delta = datetime.timedelta(days=1)
    while start_time <= end_time:
        # Format current query date as string (for file naming, etc.)
        date = start_time.date().strftime("%Y-%m-%d")
        # Create a tokens folder for each date
        try:
            os.mkdir(f'{subreddit}/data/tokens/{date}')
        except:
            #print(f'{date} folder exists')
            pass
        #print(f'Files in {date} posts folder: {get_files(f"data/posts/{date}")}')
        for post_id in get_files(f'{subreddit}/data/posts/{date}'):
            try:
                # Read the text data for each post
                path = f'{subreddit}/data/posts/{date}/{post_id}'
                file = open(path,"r")
                # Remove newlines and apostrophes; lowercase everything
                post_string = file.read().replace('\n', '').replace("'","").lower()
                # Tokenize string (creates an array of strings)
                word_tokens = tokenizer.tokenize(post_string) 
                tokenized_post = []
                for w in word_tokens:  
                    if w not in stop_words: # Remove stopwords
                        tokenized_post.append(w)
                #print(tokenized_post)
                # Save as pickle
                pickle.dump(tokenized_post, open(f'{subreddit}/data/tokens/{date}/{post_id[:-4]}.pkl', 'wb'))
            except: print(f"Couldn't read {date} post id {post_id[:-4]} at {path}")
        start_time += delta
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print()
    print('--- Finished tokenizing post files ---')
    print(f'Elapsed tokenize function time: {np.around(function_elapsed_time, 1)}s ({np.around(function_elapsed_time/60, 2)} minutes)')
    print(f'Elapsed process time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')
        
tokenize_files(start, end)

def count_words(start_date, end_date):
    print(f'Getting wordcounts for {start_date} to {end_date}...')
    function_start_time = time.time()
    try: os.mkdir(f'{subreddit}/data/wordcounts')
    except: print(f'{subreddit}/data/wordcounts directory exists')
    # Convert dates to datetime format
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    # Advance one day at a time
    delta = datetime.timedelta(days=1)
    while start_time <= end_time:
        # Format current query date as string (for file naming, etc.)
        date = start_time.date().strftime("%Y-%m-%d")
        # Create a dataframe for the whole day
        day_df = pd.DataFrame(columns=['post_number','count','word'])
        try:
            # Create a wordcounts folder for each date
            os.mkdir(f'{subreddit}/data/wordcounts/{date}')
        except: pass #print(f'{date} folder exists')
        #print(f'Files in {date} token folder: {get_files(f"data/tokens/{date}")}')
        for post_id in get_files(f'{subreddit}/data/tokens/{date}'):
            #try:
            path = f'{subreddit}/data/tokens/{date}/{post_id}'
            # Load pickled token file for each post
            tokenized_post = pickle.load(open(path, 'rb'))
            # Obtain the word counts for each token
            word_counts = FreqDist(tokenized_post)
            #print(dict(word_counts))
            # Save the word counts to a dataframe
            df = pd.DataFrame.from_dict(dict(word_counts), orient='index',
                       columns=['count']).sort_values(by='count', ascending=False).reset_index()
            # Save the dataframe of token counts to a csv in the date folder
            df.to_csv(f'{subreddit}/data/wordcounts/{date}/{post_id[:-4]}.csv',index=False)
            # Add additional post data to the dataframe and format for integration into full day dataframe
            df['post_number']=post_id[:-4]
            df.reset_index(inplace=True)
            df = df.rename(columns = {'index':'word'}).drop(columns=['level_0'])
            # Add this post's word count data to the whole day dataframe
            day_df = day_df.append(df, ignore_index=True)
            #except: print(f"Couldn't read {date} post #{post_id[:-4]} at path {path}")
        #print(day_df)
        # Save all the post wordcounts into a csv within the date folder
        day_df.to_csv(f'{subreddit}/data/wordcounts/{date}/_{date}.csv')
        # Aggregate all the wordcounts for the whole day
        agg_df = pd.DataFrame(day_df.groupby('word')['count'].sum()).reset_index()
        agg_df = agg_df.sort_values(by='count', ascending=False).dropna()
        # Save the aggregations for the whole day directly into the wordcount folder
        agg_df.to_csv(f'{subreddit}/data/wordcounts/_{date}.csv',index=False)
        start_time += delta
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print()
    print('--- Finished counting words ---')
    print(f'Elapsed wordcount function time: {np.around(function_elapsed_time, 1)}s ({np.around(function_elapsed_time/60, 2)} minutes)')
    print(f'Elapsed process time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')
        
count_words(start,end)

def get_ngrams(start_date, end_date):
    print()
    print(f'Processing r/{subreddit} ngrams for {start_date} to {end_date}')
    function_start_time = time.time()
    try: os.mkdir(f'{subreddit}/data/ngrams')
    except: print(f'{subreddit}/data/ngrams directory exists')
    # Convert dates to datetime format
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    # Advance one day at a time
    delta = datetime.timedelta(days=1)
    dates_list = get_dirs(f'{subreddit}/data/wordcounts/')
    num_dates = len(dates_list)
    i=0
    while start_time <= end_time:
        # Format current query date as string (for file naming, etc.)
        date = start_time.date().strftime("%Y-%m-%d")
        print(f'Processing ngrams for {date}... ({i}/{num_dates})')
        # Open the aggregations for this date
        agg_df = pd.read_csv(f'{subreddit}/data/wordcounts/_{date}.csv').set_index('word').dropna()
        for word in agg_df.index:
            word = str(word)
            if word[0].isdigit():
                #print(f'{word} begins with a digit; omitting from ngram data')
                pass
            else:
                try:
                    count = agg_df.loc[word]['count']
                    with open(f'{subreddit}/data/ngrams/{word}.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([date,count])
                except:
                    print(f'Error processing ngram {word}')
                    #pass
        start_time += delta
        i+=1
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print()
    print('--- Finished getting ngram timeseries ---')
    print(f'Elapsed ngram function time: {np.around(function_elapsed_time, 1)}s ({np.around(function_elapsed_time/60, 2)} minutes)')
    print(f'Elapsed process time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')

get_ngrams(start,end)

def backfill():
    function_start_time = time.time()
    post_counts = pd.read_csv(f'{subreddit}/data/post_counts.csv',names=['date','response'])
    missing = list(post_counts[post_counts['response'].astype(str)=="HTML_ERR"]['date'])
    
    for nr in not_recorded.keys():
        if nr not in missing:
            print()
            print(f'{nr} is not in the HTML Error list; the JSON response file may be corrupted for that day.')
            print(f'Check the link here: {not_recorded[nr]}')
            print()
    if len(missing)>0:
        print()
        print(f'Identified missing dates due to HTML ERR (API timeout): {missing}')
        i=0
        for m in missing:
            print(f'Backfilling {m}... ({i}/{len(missing)}')
            start_time = datetime.datetime.strptime(m, '%Y-%m-%d')
            delta = datetime.timedelta(days=1)
            end_time = start_time + delta
            start_date = start_time.date().strftime("%Y-%m-%d")
            end_date = end_time.date().strftime("%Y-%m-%d")
            try:
                get_days(start_date, end_date)
                tokenize_files(start, end)
                count_words(start,end)
                get_ngrams(start,end)
            except:
                print(f'Error backfilling {m}')
            i+=1
        function_elapsed_time = time.time() - function_start_time
        process_elapsed_time = time.time() - process_start_time
        print()
        print('--- Finished backfilling missing days ---')
        print('NOTE: If the API was down the second time around too, there may still be missing days')
        print(f'Elapsed backfilling function time: {np.around(function_elapsed_time, 1)}s ({np.around(function_elapsed_time/60, 2)} minutes)')
        print(f'Elapsed process time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')

backfill()

process_elapsed_time = time.time() - process_start_time
print()
print('--- Finished process! ---')
print(f'Elapsed time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')
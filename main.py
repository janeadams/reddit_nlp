import json
import requests
import datetime
import os
import pickle
import csv
import pandas as pd
import nltk
import time
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.probability import FreqDist

process_start_time = time.time()

print("Which subreddit (case-sensitive) would you like to query? (Don't include 'r/'):")
subreddit = input()
print(f'Querying Pushshift API for r/{subreddit}...')
      
try: os.mkdir(f'data')
except: print('data/ directory exists')
try: os.mkdir(f'data/all')
except: print('data/all directory exists')
try: os.mkdir(f'data/posts')
except: print('data/posts directory exists')
    
print('Enter start date in the format YYYY-MM-DD:')
start = input()
    
print('Enter end date in the format YYYY-MM-DD:')
end = input()

all_data = {}
post_data = {}

def get_days(start_date, end_date):
    function_start_time = time.time()
    # Convert dates to datetime format
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    # Advance one day at a time
    delta = datetime.timedelta(days=1)
    while start_time <= end_time:
        # Convert to integer epoch for querying Pushshift API
        after_epoch = int(start_time.timestamp())
        before_epoch = int((start_time + delta).timestamp())
        # Format current query date as string (for file naming, etc.)
        date = start_time.date().strftime("%Y-%m-%d")
        print(f'https://api.pushshift.io/reddit/search/submission/?subreddit={subreddit}&before={before_epoch}&after={after_epoch}')
        try:
            print(f'Querying {date} to {(start_time + delta).date().strftime("%Y-%m-%d")}')
            # Query API, specifying subreddit and time epoch
            r = requests.get(f'https://api.pushshift.io/reddit/search/submission/?subreddit={subreddit}&before={before_epoch}&after={after_epoch}').json()
            all_data[date] = r['data']
            print(f'{date} number of posts: {len(r["data"])}')
            # Save raw data (incl. metadata) in json files for each date
            with open(f'data/all/{date}.json', 'w') as outfile:
                json.dump(r['data'], outfile)
            # Create a posts folder for each date
            try:
                os.mkdir(f'data/posts/{date}')
            except:
                print(f'{date} folder exists')
            n=0 # Post number
            for post_obj in r['data']: # For each post
                try:
                    post_text = post_obj['selftext'] # Get the raw text of the post
                    file = open(f'data/posts/{date}/{n}.txt',"w") # Save it in a text file
                    file.write(post_text)
                    file.close()
                    n+=1 # Increase n by 1 for next post number
                except:
                    print(f'No selftext in {subreddit} API response on {date}')
        except:
            print(f'Error querying {date} to {(start_time + delta).date().strftime("%Y-%m-%d")}')
        start_time += delta
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print(f'Finished quering API!')
    print(f'Elapsed function time: {function_elapsed_time}')
    print(f'Elapsed process time: {process_elapsed_time}')
        
get_days(start, end)
        
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
nltk.download('punkt')
tokenizer = RegexpTokenizer(r'\w+')

def tokenize_files(start_date, end_date):
    function_start_time = time.time()
    try: os.mkdir(f'data/tokens')
    except: print('data/tokens directory exists')
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
            os.mkdir(f'data/tokens/{date}')
        except:
            print(f'{date} folder exists')
        n=0
        while n < 100: # The max number of posts returned by Pushshift for each date
            try:
                # Read the text data for each post
                file = open(f'data/posts/{date}/{n}.txt',"r")
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
                pickle.dump(tokenized_post, open(f'data/tokens/{date}/{n}.pkl', 'wb'))
            except Exception: pass #print(f"Couldn't read {date} post #{n}")
            n+=1
        start_time += delta
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print(f'Finished tokenizing post files!')
    print(f'Elapsed function time: {function_elapsed_time}')
    print(f'Elapsed process time: {process_elapsed_time}')
        
tokenize_files(start, end)

def count_words(start_date, end_date):
    function_start_time = time.time()
    try: os.mkdir(f'data/wordcounts')
    except: print('data/wordcounts directory exists')
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
            os.mkdir(f'data/wordcounts/{date}')
        except: pass #print(f'{date} folder exists')
        n=0
        while n < 100: # The max number of posts returned by Pushshift for each date
            try:
                # Load pickled token file for each post
                tokenized_post = pickle.load(open(f'data/tokens/{date}/{n}.pkl', 'rb'))
                # Obtain the word counts for each token
                word_counts = FreqDist(tokenized_post)
                #print(dict(word_counts))
                # Save the word counts to a dataframe
                df = pd.DataFrame.from_dict(dict(word_counts), orient='index',
                           columns=['count']).sort_values(by='count', ascending=False).reset_index()
                # Save the dataframe of token counts to a csv in the date folder
                df.to_csv(f'data/wordcounts/{date}/{n}.csv',index=False)
                # Add additional post data to the dataframe and format for integration into full day dataframe
                df['post_number']=n
                df.reset_index(inplace=True)
                df = df.rename(columns = {'index':'word'}).drop(columns=['level_0'])
                # Add this post's word count data to the whole day dataframe
                day_df = day_df.append(df, ignore_index=True)
            except Exception: pass #print(f"Couldn't read {date} post #{n}")
            n+=1
        #print(day_df)
        # Save all the post wordcounts into a csv within the date folder
        day_df.to_csv(f'data/wordcounts/{date}/_{date}.csv')
        # Aggregate all the wordcounts for the whole day
        agg_df = pd.DataFrame(day_df.groupby('word')['count'].sum()).reset_index()
        agg_df = agg_df.sort_values(by='count', ascending=False)
        # Save the aggregations for the whole day directly into the wordcount folder
        agg_df.to_csv(f'data/wordcounts/_{date}.csv',index=False)
        start_time += delta
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print(f'Finished counting words!')
    print(f'Elapsed function time: {function_elapsed_time}')
    print(f'Elapsed process time: {process_elapsed_time}')
        
count_words(start,end)

def get_ngrams(start_date, end_date):
    function_start_time = time.time()
    try: os.mkdir(f'data/ngrams')
    except: print('data/ngrams directory exists')
    # Convert dates to datetime format
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    # Advance one day at a time
    delta = datetime.timedelta(days=1)
    while start_time <= end_time:
        # Format current query date as string (for file naming, etc.)
        date = start_time.date().strftime("%Y-%m-%d")
        print(f'Processing ngrams for {date}')
        # Open the aggregations for this date
        agg_df = pd.read_csv(f'data/wordcounts/_{date}.csv').set_index('word')
        for word in agg_df.index:
            count = agg_df.loc[word]['count']
            try:
                with open(f'data/ngrams/{word}.csv', 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([date,count])
            except:
                pass
        start_time += delta
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print(f'Finished getting ngram timeseries!')
    print(f'Elapsed function time: {function_elapsed_time}')
    print(f'Elapsed process time: {process_elapsed_time}')

get_ngrams(start,end)

process_elapsed_time = time.time() - process_start_time
print(f'Finished script! Elapsed time: {process_elapsed_time}')
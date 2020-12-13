import json
import requests
import datetime
import progressbar
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

def get_files(path):
    files = []
    for (dirpath, dirnames, filenames) in walk(path):
        files.extend(filenames)
        break
    str_files = [str(f)[:-4] for f in files]
    return str_files

def get_dirs(path):
    directories = []
    for (dirpath, dirnames, filenames) in walk(path):
        directories.extend(dirnames)
        break
    str_directories = [str(d) for d in directories]
    return str_directories

def get_days(start_date, end_date, subreddit, api, process_start_time):
    function_start_time = time.time()
    n=1
    print()
    print(f'Querying r/{subreddit} API from {start_date} to {end_date}...')
    # Convert dates to datetime format
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    # Advance one day at a time
    date_list = [start_time + datetime.timedelta(days=x) for x in range(0, (end_time-start_time).days)]
    for search_time in progressbar.progressbar(date_list, redirect_stdout=True):
        cached=False
        # Convert to integer epoch for querying Pushshift API
        after_epoch = int(search_time.timestamp())
        before_epoch = int((search_time + datetime.timedelta(days=1)).timestamp())
        # Format current query date as string (for file naming, etc.)
        date = search_time.date().strftime("%Y-%m-%d")
        if date in get_dirs(f'subreddits/{subreddit}/data/posts/'):
            cached=True
            print(f'{date} already in data folder; skipping API query')
        if not cached:
            try:
                # Query API, specifying subreddit and time epoch
                posts = list(api.search_submissions(after=after_epoch, before=before_epoch,
                            subreddit=subreddit,
                            filter=['id','selftext'],
                            limit=100))
                post_count = len(posts)
                #print(f'Number of posts: {post_count}/100 on {date}')
                # Create a posts folder for each date
                try:
                    os.mkdir(f'subreddits/{subreddit}/data/posts/{date}')
                except:
                    #print(f'{date} folder exists')
                    pass
                removed = 0
                for post in posts: # For each post
                    try:
                        n = post.d_['id']
                        text = post.d_['selftext']
                        if (len(text)>1) and (text != '[deleted]') and (text != '[removed]'):
                            file = open(f'subreddits/{subreddit}/data/posts/{date}/{n}.txt',"w") # Save it in a text file
                            file.write(text)
                            file.close()
                        else:
                            removed+=1
                    except:
                        #print(f'Error saving post data from r/{subreddit} API response on {date} id {n}')
                        #print(f'Find detailed post data here: https://api.pushshift.io/reddit/search/submission/?ids={n}')
                        pass
                #if removed > 0: print(f'{removed}/{post_count} posts from {date} have since been removed')
                try:
                    with open(f'subreddits/{subreddit}/data/post_counts.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([date,post_count-removed])
                except:
                    print(f'Error writing post count for {date} to file {f"{subreddit}/data/post_counts.csv"}')
            except:
                with open(f'subreddits/{subreddit}/data/post_counts.csv', 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([date,'ERR'])
                print(f'Error querying r/{subreddit} on {date}')
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print()
    print(f'--- Finished querying r/{subreddit} API ---')
    print(f'Elapsed query function time: {np.around(function_elapsed_time, 1)}s ({np.around(function_elapsed_time/60, 2)} minutes)')
    print(f'Elapsed process time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')
        
        
def tokenize_files(start, end, subreddit, process_start_time):
    nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('english'))
    nltk.download('punkt', quiet=True)
    tokenizer = RegexpTokenizer(r'\w+')
    print()
    print(f'Tokenizing post files for {start} to {end}...')
    function_start_time = time.time()
    try: os.mkdir(f'subreddits/{subreddit}/data/tokens')
    except: print(f'subreddits/{subreddit}/data/tokens directory exists')
    # Get list of dates:
    dates = get_dirs(f'subreddits/{subreddit}/data/posts/')
    for date in progressbar.progressbar(dates, redirect_stdout=True):
        # Create a tokens folder for each date
        try:
            os.mkdir(f'subreddits/{subreddit}/data/tokens/{date}')
        except:
            #print(f'{date} folder exists')
            pass
        #print(f'Files in {date} posts folder: {get_files(f"data/posts/{date}")}')
        posts = get_files(f'subreddits/{subreddit}/data/posts/{date}')
        day_token_count = 0
        for post_id in posts:
            try:
                # Read the text data for each post
                path = f'subreddits/{subreddit}/data/posts/{date}/{post_id}.txt'
                file = open(path,"r")
                # Remove newlines and apostrophes; lowercase everything
                post_string = file.read().replace('\n', '').replace("'","").replace('_','').lower()
                # Tokenize string (creates an array of strings)
                word_tokens = tokenizer.tokenize(post_string)
                day_token_count = day_token_count + len(word_tokens)
                tokenized_post = []
                for w in word_tokens:
                    # Remove stopwords, digits, and underscore ngrams
                    if (w not in stop_words) and (not str(w)[0].isdigit()): 
                            tokenized_post.append(w)
                            pickle.dump(tokenized_post, open(f'subreddits/{subreddit}/data/tokens/{date}/{post_id}.pkl', 'wb'))
            except: print(f"Couldn't read {date} post id {post_id} at {path}")
        try:
            with open(f'subreddits/{subreddit}/data/token_counts.csv', 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([date,day_token_count])
        except:
            print(f'Error writing token count for {date} to file {f"{subreddit}/data/token_counts.csv"}')
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print()
    print('--- Finished tokenizing post files ---')
    print(f'Elapsed tokenize function time: {np.around(function_elapsed_time, 1)}s ({np.around(function_elapsed_time/60, 2)} minutes)')
    print(f'Elapsed process time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')
       
        
def count_words(start, end, subreddit, process_start_time):
    print()
    print(f'Getting wordcounts for {start} to {end}...')
    function_start_time = time.time()
    try: os.mkdir(f'subreddits/{subreddit}/data/wordcounts')
    except: print(f'subreddits/{subreddit}/data/wordcounts directory exists')
    dates = get_dirs(f'subreddits/{subreddit}/data/tokens/')
    token_counts = pd.read_csv(f'subreddits/{subreddit}/data/token_counts.csv',names=['token_count'])
    for date in progressbar.progressbar(dates, redirect_stdout=True):
        # Create a dataframe for the whole day
        day_df = pd.DataFrame(columns=['post_number','count','word'])
        day_token_count = token_counts.loc[date]['token_count']
        try:
            # Create a wordcounts folder for each date
            os.mkdir(f'subreddits/{subreddit}/data/wordcounts/{date}')
        except: pass #print(f'{date} folder exists')
        #print(f'Files in {date} token folder: {get_files(f"data/tokens/{date}")}')
        for post_id in get_files(f'subreddits/{subreddit}/data/tokens/{date}'):
            #try:
            path = f'subreddits/{subreddit}/data/tokens/{date}/{post_id}.pkl'
            # Load pickled token file for each post
            tokenized_post = pickle.load(open(path, 'rb'))
            post_token_count = len(tokenized_post)
            # Obtain the word counts for each token
            word_counts = FreqDist(tokenized_post)
            #print(dict(word_counts))
            # Save the word counts to a dataframe
            df = pd.DataFrame.from_dict(dict(word_counts), orient='index',
                       columns=['count']).sort_values(by='count', ascending=False).reset_index()
            df['freq'] = df['count']/post_token_count
            # Save the dataframe of token counts to a csv in the date folder
            df.to_csv(f'subreddits/{subreddit}/data/wordcounts/{date}/{post_id}.csv',index=False)
            # Add additional post data to the dataframe and format for integration into full day dataframe
            df['post_number']=post_id
            df.reset_index(inplace=True)
            df = df.rename(columns = {'index':'word'}).drop(columns=['level_0'])
            # Add this post's word count data to the whole day dataframe
            day_df = day_df.append(df, ignore_index=True)
            #except: print(f"Couldn't read {date} post #{post_id[:-4]} at path {path}")
        #print(day_df)
        # Aggregate all the wordcounts for the whole day
        agg_df = pd.DataFrame(day_df.groupby('word')['count'].sum()).reset_index()
        agg_df = agg_df.sort_values(by='count', ascending=False).dropna()
        agg_df['freq'] = agg_df['count']/day_token_count
        # Save the aggregations for the whole day directly into the wordcount folder
        agg_df.to_csv(f'subreddits/{subreddit}/data/wordcounts/{date}.csv',index=False)
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print()
    print('--- Finished counting words ---')
    print(f'Elapsed wordcount function time: {np.around(function_elapsed_time, 1)}s ({np.around(function_elapsed_time/60, 2)} minutes)')
    print(f'Elapsed process time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')
      
        
def get_ngrams(start, end, subreddit, process_start_time):
    print()
    print(f'Processing r/{subreddit} ngrams for {start} to {end}')
    function_start_time = time.time()
    try: os.mkdir(f'subreddits/{subreddit}/data/ngrams')
    except: print(f'subreddits/{subreddit}/data/ngrams directory exists')
    dates = get_files(f'subreddits/{subreddit}/data/wordcounts/')
    for date in progressbar.progressbar(dates, redirect_stdout=True):
        # Open the aggregations for this date
        agg_df = pd.read_csv(f'subreddits/{subreddit}/data/wordcounts/{date}.csv').set_index('word').dropna()
        for word in agg_df.index:
            word = str(word)
            try:
                count = agg_df.loc[word]['count']
                freq = agg_df.loc[word]['freq']
                with open(f'subreddits/{subreddit}/data/ngrams/{word}.csv', 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([date,count,freq])
            except:
                #print(f'Error processing ngram {word}')
                pass
    function_elapsed_time = time.time() - function_start_time
    process_elapsed_time = time.time() - process_start_time
    print()
    print('--- Finished getting ngram timeseries ---')
    print(f'Elapsed ngram function time: {np.around(function_elapsed_time, 1)}s ({np.around(function_elapsed_time/60, 2)} minutes)')
    print(f'Elapsed process time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')

def summarize_wordcounts(start, end, subreddit, process_start_time):
    print()
    print(f'Summarizing ngram counts for r/{subreddit} from {start} to {end}')
    function_start_time = time.time()
    try:
        data_files = get_files(f'subreddits/{subreddit}/data/')
        if 'word_counts.csv' in data_files:
            print('Word count summary is cached')
            summary = pd.read_csv(f'subreddits/{subreddit}/data/word_counts.csv')
        else:
            df = pd.DataFrame(columns=['word','count'])
            dates = get_files(f'subreddits/{subreddit}/data/wordcounts/')
            for date in progressbar.progressbar(dates, redirect_stdout=True):
                counts = pd.read_csv(f'subreddits/{subreddit}/data/wordcounts/{date}.csv').drop(columns=['freq'])
                counts['count'].astype(int, errors='ignore')
                df = pd.DataFrame(pd.concat([df, counts]).groupby('word').sum().reset_index()).sort_values('count',ascending=False)
            print(f'Summarizing wordcounts for {subreddit}...')
            summary = pd.DataFrame(df.groupby('word').sum().reset_index()).sort_values('count',ascending=False)
            summary.to_csv(f'subreddits/{subreddit}/data/word_counts.csv', index=False)
            print()
            function_elapsed_time = time.time() - function_start_time
            process_elapsed_time = time.time() - process_start_time
            print('--- Finished summarizing word counts ---')
            print(f'Elapsed summarizing function time: {np.around(function_elapsed_time, 1)}s ({np.around(function_elapsed_time/60, 2)} minutes)')
            print(f'Elapsed process time: {np.around(process_elapsed_time, 1)}s ({np.around(process_elapsed_time/60, 2)} minutes)')
    except:
        summary = pd.DataFrame(data={'word':['ERR'], 'count':[99999]})
        print('Error summarizing wordcounts!')
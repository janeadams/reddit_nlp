import os
from os import walk
import pandas as pd
import progressbar
import numpy as np

def get_files(path):
    files = []
    for (dirpath, dirnames, filenames) in walk(path):
        files.extend(filenames)
        break
    str_files = [str(f)[:-4] for f in files]
    return str_files

def get_thresholds(subreddit):
    for i in range(1,10):
        n = wordcounts[wordcounts['count']<i].shape[0]
        pct = np.around((n/wordcounts.shape[0])*100)
        print(f'There are {n} words used less than {i} times ({pct}%)')

def get_removal_list(subreddit,threshold):
    removal_list=list(wordcounts[wordcounts['count']<threshold]['word'])
    print(f'Found {len(removal_list)} words to remove out of {wordcounts.shape[0]} ({np.around((len(removal_list)/wordcounts.shape[0])*100)}%)')
    return removal_list

def remove_words(subreddit,threshold):
    removal_list = get_removal_list(subreddit,threshold)
    i=0
    for w in progressbar.progressbar(removal_list, redirect_stdout=True):
        try:
            os.remove(f'subreddits/{subreddit}/data/ngrams/{w}.csv')
            i+=1
        except:
            #print(f'"{w}" file does not exist' )
            pass
    print(f'Removed {i} ngrams from {subreddit} ngrams directory')
    
print("Which subreddit (case-sensitive) would you like to filter? (Don't include 'r/'):")
subreddit = input()
print()
wordcounts = pd.read_csv(f'subreddits/{subreddit}/data/word_counts.csv')
get_thresholds(subreddit)
print("Remove words that are used fewer than X times (recommended entry: 2; enter 0 to remove none)")
threshold = int(input())
remove_words(subreddit,threshold)
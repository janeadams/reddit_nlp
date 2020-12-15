import os
from os import walk
import pandas as pd
import progressbar
import numpy as np
from data import *

def get_thresholds(subreddit):
    for i in range(2,10):
        n = wordcounts[wordcounts['count']<i].shape[0]
        m = wordcounts[wordcounts['count']>i].shape[0]
        pct_n = np.around((n/wordcounts.shape[0])*100)
        pct_m = np.around((m/wordcounts.shape[0])*100)
        print(f'There are {n} words used less than {i} times ({pct_n}%)')
        print(f'and {m} words used more than {i} times ({pct_m}%)')
        print()

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
print(f'Subreddits available: {get_dirs("subreddits/")}')
subreddit = input()
print()
wordcounts = pd.read_csv(f'subreddits/{subreddit}/data/word_counts.csv')
get_thresholds(subreddit)
print("Remove words that are used fewer than X times (recommended entry: 2; enter 0 to remove none)")
threshold = int(input())
remove_words(subreddit,threshold)
from dashboard import *
import os
from os import walk

def get_dirs(path):
    directories = []
    for (dirpath, dirnames, filenames) in walk(path):
        directories.extend(dirnames)
        break
    str_directories = [str(d) for d in directories if not (str(d)[0] in ['.','_'])]
    return str_directories

print("Which subreddit would you like to visualize? (Don't include 'r/'):")
print(f"The directories available are {get_dirs(os.getcwd())}")
subreddit = input()

visualize(subreddit)
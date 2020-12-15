# Reddit NLP Project
A package for processing ngram data from the Pushshift API by subreddit and visualizing the timeseries as a Plotly Dash dashboard.

## Getting started

Clone the repository using:
`https://github.com/janeadams/reddit_nlp.git`

Navigate to the reddit_nlp folder:
`cd reddit_nlp`

Install the data processing package requirements:
`pip install -r data-requirements.txt`

If you're going to be visualizing the data, make sure you also install the visualization requirements:
`pip install -r requirements.txt`

### Pulling Data from the Pushshift.io API
Run the main data processing script (make sure you're running python 3.6 or higher, as scripts use fstrings):
`python main.py`

Follow the command-line prompts to enter the subreddit you want to query, and start and end dates (YYYY-MM-DD). Select the ngram threshold for which ngram files to save to disk; `1` is recommended (saving ngrams that are used more than once); entering `0` will save all ngrams, including ngrams used only once.

It's recommended that you query a small range at first, to make sure everything is working as expected. For example, enter `AskDocs`, then `2020-01-01` as the start date and `2020-01-10` as the end date to get the first ten days in January 2020 for the subreddit r/AskDocs. The command line will print out progress bars.

### Visualizing ngram data
Run the main visualization script using Python 3.6 or higher:
`python dashboard.py`

The script will look in the `subreddits` directory for a list of all subreddits for which you have pulled data. Dash will spin up a local server at `localhost:8050` - you can view the dashboard at `http://127.0.0.1:8050`

### Filtering ngram data
If you have saved a lot of ngrams to disk, and you'd like to remove those that are infrequently used, you can make use of the `remove_ngrams.py` script to filter out rarely used ngrams:
`python remove_ngrams.py`

Enter the subreddit directory you'd like to filter (e.g. `AskDocs`), then choose a threshold (you can get an idea of ngrams at each threshold from the automatic printout). This script will remove any ngrams that appear less than the entered number (so if you'd like to remove all ngrams that have only been used once, enter `2`).

### Removing date ranges
If you've downloaded some date ranges that contain little to no data, and you'd like to remove those ngrams and related files, you can make use of the `remove_days.py` script to filter out a range of dates:
`python remove_days.py`

Enter the subreddit directory you'd like to filter, then choose start and end dates (YYYY-MM-DD). This script will remove any posts, tokens, and wordcounts folders/files for those dates, remove those date entries from the ngram files, and recompute aggregated word counts.

### Running the dashboard on a server
In order to run the dashboard on a server, you'll need a server running uwsgi. A `wsgi.py` script is included for running the dashboard application. You don't need to upload the `posts/` or `tokens/` folders for each subreddit, but you will need to upload the `ngrams` directory for each subreddit in the original `subreddits/{subreddit}/data/` directory structure, along with the summary files `word_counts.csv` and `post_counts.csv`.

### Deleting whole subreddit data downloads
You can delete all data for a subreddit query from the `reddit_nlp` directory by entering:
`rm -r subreddit/{subreddit}`


## File structure

File structure is as follows (in the order of usage):

- `data_requirements.txt` : requirements for downloading new subreddit data
- `requirements.txt` : requirements for running the dashboard on the website
- `main.py` : wrapper script for running the main data processing function
- `dashboard.py` : wrapper script for running the visualization dashboard (runs on localhost:8051)
- `remove.py`: script for removing ngrams below a certain usage threshold
+ `subreddits`
    + `{subreddit}` (e.g. 'AskDocs')
        + `data`
            - `post_counts.csv`
            + `posts`
                + `{date}`
                    - `{post_id}.txt` (in base64): raw text from API `selftext` field
            - `token_counts.csv`
            + `tokens`
                + `{date}`
                    - `{post_id}.pkl` (in base64): pickle with list of tokens, e.g. `['word','and','word']`
            + `ngrams`
                - `{ngram}.csv`
            - `word_counts.csv`
            + `wordcounts`
                - `{date}.csv`: Word counts aggregated by day
                + `{date}`
                    - `{post_id}.csv` (in base64): word counts for each post
- `data.py` : contains all the data processing functions
- `dashboard.py` : contains all the visualization functions
- `wsgi.py`: uwsgi script for running the dashboard on a web server
- `assets`: css assets for the dash app



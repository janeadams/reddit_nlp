# Reddit NLP Project
A package for processing ngram data from the Pushshift API by subreddit and visualizing the timeseries as a Plotly Dash dashboard.

## File structure

File structure is as follows (in the order of usage):

+-- `data_requirements.txt` : requirements for downloading new subreddit data
+-- `requirements.txt` : requirements for running the dashboard on the website
+-- `main.py` : wrapper script for running the main data processing function
+-- `wsgi.py` : wrapper script for running the visualization dashboard
|-- `subreddits`
    |-- `{subreddit}` (e.g. 'AskDocs')
        |-- `data`
            +-- `post_counts.csv`
            |-- `posts`
                |-- `{date}`
                    +-- `{post_id}.txt` (in base64): raw text from API `selftext` field
            +-- `token_counts.csv`
            |-- `tokens`
                |-- `{date}`
                    +-- `{post_id}.pkl` (in base64): pickle with list of tokens, e.g. `['word','and','word']`
            |-- `ngrams`
                +-- `{ngram}.csv`
            +-- `word_counts.csv`
            |-- `wordcounts`
                +-- `{date}.csv`: Word counts aggregated by day
                |-- `{date}`
                    +-- `{post_id}.csv` (in base64): word counts for each post
+-- `data.py` : contains all the data processing functions
+-- `dashboard.py` : contains all the visualization functions


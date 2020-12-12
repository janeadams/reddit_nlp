import pandas as pd
from os import walk
import progressbar
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html

print("Which subreddit (case-sensitive) would you like to query? (Don't include 'r/'):")
subreddit = input()

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

def get_ngrams(subreddit):
    summ=pd.read_csv(f'{subreddit}/data/word_counts.csv')
    common=summ[summ['count']>5]['word']
    return common

common = get_ngrams(subreddit)

options = []
for n in common:
    options.append({'label': n, 'value': n})
    
def format_data(ngram):
    df = pd.read_csv(f'{subreddit}/data/ngrams/{ngram}.csv', names=['date','count'])
    df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)  
    df['WRA'] = df['count'].rolling(7, min_periods=1).mean()
    df['MRA'] = df['count'].rolling(30, min_periods=1).mean()
    df['ARA'] = df['count'].rolling(365, min_periods=1).mean()
    return df

def draw_line(ngram):
    df = format_data(ngram)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['count'],
                        mode='markers',
                        name='Daily',
                        marker_color='PowderBlue',
                        visible='legendonly'
                     ),
                 )
    fig.add_trace(go.Scatter(x=df['date'], y=df['WRA'],
                        mode='lines',
                        name='Weekly Moving Average',
                        line=dict(color='DarkTurquoise', width=2)
                     ),
                 )
    fig.add_trace(go.Scatter(x=df['date'], y=df['MRA'],
                        mode='lines',
                        name='Monthly Moving Average',
                        line=dict(color='RoyalBlue', width=4)
                     ),
                 )
    fig.add_trace(go.Scatter(x=df['date'], y=df['ARA'],
                        mode='lines',
                        name='Annual Moving Average',
                        line=dict(color='Crimson', width=2, dash='dash')
                     ),
                 )
    fig.update_layout(
        title=f'r/{subreddit}: {ngram}',
        xaxis_title="Date",
        yaxis_title="Ngram Count",
        template='plotly_white',
        height=500
    )
    return fig

app = dash.Dash()
app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown',
        options=options,
        value=common[0]
    ),
    dcc.Graph(id='plot')
])

@app.callback(
    dash.dependencies.Output('plot', 'figure'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_output(ngram):
    return draw_line(ngram)

app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter
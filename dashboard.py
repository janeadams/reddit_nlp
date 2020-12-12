import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq

def visualize(subreddit):
    
    def freq_to_odds(freq):
        try: return 1.0/freq
        except: return None

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
        
    if subreddit == "AskDocs":
        default_single = "flu"
        default_multi = ["flu","depression","covid"]
    else:
        default_single = common[0]
        default_multi = [common[0], common[1], common[2]]

    token_counts = pd.read_csv(f'{subreddit}/data/token_counts.csv',names=['token_count'])
    token_counts.index = pd.to_datetime(token_counts.index, infer_datetime_format=True)
    token_counts = token_counts.sort_index()

    post_counts = pd.read_csv(f'{subreddit}/data/post_counts.csv',names=['post_count'])
    post_counts.index = pd.to_datetime(post_counts.index, infer_datetime_format=True)
    post_counts = post_counts.sort_index()

    def format_data(ngram,metric):
        df = pd.read_csv(f'{subreddit}/data/ngrams/{ngram}.csv', names=['date','count','freq'])
        df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)
        df = df.sort_values(by=['date'])
        df['odds']=[freq_to_odds(f) for f in df['freq']]
        df['WMA'] = df[metric].rolling(7, min_periods=1).mean()
        df['MMA'] = df[metric].rolling(30, min_periods=1).mean()
        df['AMA'] = df[metric].rolling(365, min_periods=1).mean()
        return df

    def single_plot(ngram,metric):
        df = format_data(ngram,metric)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df[metric],
                            mode='markers',
                            name=f'Daily {metric.title()}',
                            marker_color='PowderBlue'
                            #visible='legendonly'
                         ),
                     )
        fig.add_trace(go.Scatter(x=df['date'], y=df['WMA'],
                            mode='lines',
                            name=f'Weekly Rolling Average {metric.title()}',
                            line=dict(color='DarkTurquoise', width=2)
                         ),
                     )
        fig.add_trace(go.Scatter(x=df['date'], y=df['MMA'],
                            mode='lines',
                            name=f'Monthly Rolling Average {metric.title()}',
                            line=dict(color='GoldenRod', width=3)
                         ),
                     )
        fig.add_trace(go.Scatter(x=df['date'], y=df['AMA'],
                            mode='lines',
                            name=f'Annual Rolling Average {metric.title()}',
                            line=dict(color='Crimson', width=2, dash='dash')
                         ),
                     )

        fig.add_trace(go.Bar(
            x = token_counts.index,
            y = token_counts['token_count'],
            name="Daily word count",
            yaxis='y2',
            marker_color='LightGrey',
            showlegend=False
        ))

        fig.update_layout(
            title=f'Subreddit r/{subreddit}: Usage {metric.title()} for "{ngram}"',
            xaxis_title="Date",
            yaxis_title=f'Ngram {metric}',
            template='plotly_white',
            height=500,
            yaxis=dict(
                overlaying='y2'
            ),
            yaxis2=dict(
                side = 'right'
            ),
            hovermode='x unified'
        )
        
        if metric == 'odds':
            fig.update_layout(yaxis=({'autorange':"reversed","type":"log"}))
        return fig
    
    def multi_plot(ngrams,metric):
        fig = go.Figure()
        colors = px.colors.qualitative.Dark2
        i=0
        for ngram in ngrams:
            df = format_data(ngram,metric)
            fig.add_trace(go.Scatter(x=df['date'], y=df['WMA'],
                                mode='lines',
                                name=f'"{ngram}" (7-day Avg.)',
                                opacity=0.3,
                                line=dict(color=colors[i]),
                                showlegend=False
                             ),
                         )
            fig.add_trace(go.Scatter(x=df['date'], y=df['MMA'],
                                mode='lines',
                                name=f'"{ngram}" 30-Day {metric.title()}',
                                line=dict(width=2, color=colors[i]),
                                hoverinfo='skip'
                             ),
                         )
            fig.add_trace(go.Scatter(x=df['date'], y=df['AMA'],
                                mode='lines',
                                name=f'Annual Moving Average {metric.title()}',
                                line=dict(width=1, dash='dash', color=colors[i]),
                                showlegend=False,
                                hoverinfo='skip'
                             ),
                         )
            i+=1
        fig.update_layout(
            title=f'Subreddit r/{subreddit}: Usage {metric.title()} for {ngrams}',
            xaxis_title="Date",
            yaxis_title=f'Ngram {metric}',
            template='plotly_white',
            height=500,
            hovermode='x unified'
        )
        if metric == 'odds':
            fig.update_layout(yaxis=({'autorange':"reversed","type":"log"}))
        return fig

    app = dash.Dash()
    app.layout = html.Div([
        dcc.Dropdown(
            id='single-dropdown',
            options=options,
            value=default_single
        ),
        daq.BooleanSwitch(
            id='switch',
            on=True
        ),
        dcc.Graph(id='single-plot'),
        dcc.Dropdown(
            id='multi-dropdown',
            options=options,
            multi=True,
            value=default_multi
        ),
        dcc.Graph(id='multi-plot')
    ], style={
        'width':1200,
        'justify-content': 'center'}
    )

    @app.callback(
        [dash.dependencies.Output('single-plot', 'figure'),
         dash.dependencies.Output('multi-plot', 'figure')],
        [dash.dependencies.Input('single-dropdown', 'value'),
         dash.dependencies.Input('multi-dropdown', 'value'),
         dash.dependencies.Input('switch', 'on')
        ])
    def update_output(single,multi,on):
        if on:
            metric='odds'
        else:
            metric='count'
        return single_plot(single,metric), multi_plot(multi,metric)

    try:
        app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter
    except:
        print('Is something already running? Check port :8050 using lsof -i:8050')
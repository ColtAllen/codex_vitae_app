# MIT LICENSE

import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np

def display_year(journal_tuples: list,
                 year: int,
                 fig=None,
                 row: int = None):

    days = [datetime.datetime.strptime(tup[0],'%Y-%m-%d') for tup in journal_tuples]
    daily_moods = [tup[1] for tup in journal_tuples]
    daily_entries = [tup[2].replace('.', '.<br>') for tup in journal_tuples]
    
    data = np.ones(max(len(daily_moods), 365)) * np.nan
    data[:len(daily_moods)] = daily_moods  

    d1 = datetime.date(year, 1, 1)
    d2 = datetime.date(year, 12, 31)

    delta = d2 - d1

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_days =   [31,    28,    31,     30,    31,     30,    31,    31,    30,    31,    30,    31]
    month_positions = (np.cumsum(month_days) - 15)/7

    days_in_year = [d1 + datetime.timedelta(i) for i in range(delta.days+1)] #gives me a list with datetimes for each day a year
    weekdays_in_year = [i.weekday() for i in days_in_year] #gives [0,1,2,3,4,5,6,0,1,2,3,4,5,6,…] (ticktext in xaxis dict translates this to weekdays
    
    weeknumber_of_dates = [int(i.strftime("%V")) if not (int(i.strftime("%V")) == 1 and i.month == 12) else 53
                           for i in days_in_year] #gives [1,1,1,1,1,1,1,2,2,2,2,2,2,2,…] name is self-explanatory

    data = [
        go.Heatmap(
            x=weeknumber_of_dates,
            y=weekdays_in_year,
            z=data,
            text=daily_entries,
            hoverinfo=['text','z'],
            #hovertext=['text',data],
            xgap=3, # this
            ygap=3, # and this is used to make the grid-like apperance
            showscale=False,
            colorscale=[(0,"blue"), (0.5,"white"),(1,"red")] 
        )
    ]
    
    kwargs = dict(
        mode='lines',
        line=dict(
            color='#9e9e9e',
            width=1
        ),
        hoverinfo='skip'
        
    )
    for date, dow, wkn in zip(days_in_year,
                                weekdays_in_year,
                                weeknumber_of_dates):
        if date.day == 1:
            data += [
                go.Scatter(
                    x=[wkn-.5, wkn-.5],
                    y=[dow-.5, 6.5],
                    **kwargs
                )
            ]
            if dow:
                data += [
                go.Scatter(
                    x=[wkn-.5, wkn+.5],
                    y=[dow-.5, dow - .5],
                    **kwargs
                ),
                go.Scatter(
                    x=[wkn+.5, wkn+.5],
                    y=[dow-.5, -.5],
                    **kwargs
                )
            ]
                    
                    
    layout = go.Layout(
        title='activity chart',
        height=250,
        yaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            autorange="reversed"
        ),
        xaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=month_names,
            tickvals=month_positions
        ),
        font={'size':10, 'color':'#9e9e9e'},
        plot_bgcolor=('#fff'),
        margin = dict(t=40),
        showlegend=False
    )

    if fig is None:
        fig = go.Figure(data=data, layout=layout)
    else:
        fig.add_traces(data, rows=[(row+1)]*len(data), cols=[1]*len(data))
        fig.update_layout(layout)
        fig.update_xaxes(layout['xaxis'])
        fig.update_yaxes(layout['yaxis'])

    return fig


def journal_calendar(journal_tuples):
    """

    Args:
        journal_tuples:
    Returns:
        fig:
    """

    years = list(set([int(tup[0].split('-')[0]) for tup in journal_tuples]))

    fig = make_subplots(rows=len(years), cols=1, subplot_titles=years)
    
    for i, year in enumerate(years):
        data = [tup for tup in journal_tuples if int(tup[0].split('-')[0]) == year]
        display_year(data, year=year, fig=fig,row=i)
        fig.update_layout(height=250*len(years))
    return fig

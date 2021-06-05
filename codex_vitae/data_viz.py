import datetime
import numpy as np
import json

import plotly.graph_objs as go
from plotly.subplots import make_subplots
from plotly.utils import PlotlyJSONEncoder

import pandas as pd


def annual_subplot(journal_tuples,
                 year,
                 fig,
                 row=None):
    """
    Plots one year of journal data in a calendar format.

    Args:
        journal_tuples: A list of tuples containing journal data.
        year: An int of the year to the plotted.
        fig: An existing Plotly graph object.
        row: int = A row index for updated the figure subplot.

    Returns:
        fig: Appended plotly graph object.
    """

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

    days_in_year = [d1 + datetime.timedelta(i) for i in range(delta.days+1)]

    days_in_year[:len(days)] = days

    week_num = [int(i.strftime("%V")) for i in days_in_year]

    weekday_num = [i.weekday() for i in days_in_year]
    
    hovertemplate = (
    "<b>Date:</b> %{customdata}<br>" +
    "<b>Mood:</b> %{z}<br>" +
    "<b>Journal:</b> %{text}<br><extra></extra>"
    )

    data = [
        go.Heatmap(
            x=week_num,
            y=weekday_num,
            z=data,
            text=daily_entries,
            hovertemplate = hovertemplate,
            customdata=[tup[0] for tup in journal_tuples], # Display date.
            xgap=3,
            ygap=3, 
            showscale=False,
            colorscale=[(0,"blue"), (0.5,"white"),(1,"red")],
            zmid=0,
            )
        ]
    
    # Create monthly separation lines.
    kwargs = dict(
        mode='lines',
        hoverinfo='skip',
        line=dict(
            color='#9e9e9e',
            width=1
            ),
        )

    for date, dow, wkn in zip(days_in_year,
                                weekday_num,
                                week_num):
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
        # title='activity chart',
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

    # Update Plotly graph object to append annual calendar subplot.
    fig.add_traces(data, rows=[(row+1)]*len(data), cols=[1]*len(data))
    fig.update_layout(layout)
    fig.update_xaxes(layout['xaxis'])
    fig.update_yaxes(layout['yaxis'])

    return fig


def journal_calendar(journal_tuples):
    """
    Plots a calendar of journal data with each year as a subplot.

    Args:
        journal_tuples: A list of tuples containing journal data.
    Returns:
        fig: A plotly graph object.
    """

    years = list(set([int(tup[0].split('-')[0]) for tup in journal_tuples]))

    fig = make_subplots(rows=len(years), cols=1, subplot_titles=years)
    
    for i, year in enumerate(years):
        data = [tup for tup in journal_tuples if int(tup[0].split('-')[0]) == year]
        annual_subplot(data, year=year,fig=fig,row=i)
        fig.update_layout(height=250*len(years))
    
    graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
    # TODO: Make this a CLI command as part of the javascript refactoring.
    # journal_json = json.loads(graphJSON)

    return graphJSON


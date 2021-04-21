from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from contextlib import closing
import json

from datetime import date
from dateutil.relativedelta import relativedelta

import pandas as pd

from db_module import to_tuple_list
from api_requests import authenticate_gmail_api, get_email_content, get_rescuetime_daily
from text_processing import reMarkableParsing, fitness_parsing, nutrition_parsing

    
def json_to_df(var_list, year):
    """Create a Pandas DF from a list of Exist json files.

    Args:
        var_list: A list identifying data variables of interest.
        year: A string specifying the year in the json name.
    
    Returns: 
        dataframe: A Pandas Dataframe containing a column for each json. 
        """

    # Write json file names to a list variable. 
    json_list = os.listdir()

    # Filter out weekly averages and correlations from file list.
    json_list = [match for match in json_list if "data" in match]

    # Filter files by year.
    json_list = [match for match in json_list if year in match]

    for json_list in var_list:
        json_ = json.load(open(f'data_{json_list}_{year}.json', "r"))
        df = pd.DataFrame(json_).rename(columns={"value": json_list.split(".")[0]})

        try:
            dataframe = dataframe.merge(df,on='date',how='outer')

        except UnboundLocalError:
            dataframe = pd.DataFrame(df).rename(columns={"value": json_list.split(".")[0]})
        
        finally:
            pass

    return dataframe


def exist_dataframes(filepath):
    """Creates a list of Pandas dataframes containing all Exist data.

    Args:
        filepath: A string containing the filepath to the Exist data extract.
    
    Returns: 
        df_list: A list of Pandas Dataframes containing all Exist data. 
        """
    
    filepath = os.chdir(f'{filepath}/exist_full_extract')

    # Specify years of data to retrieve as a list.
    year_list = ['2020', '2021']

    # Lists of desired datafields from Exist.
    # Each list will be inserted into its own database table.
    tags = ['alcohol',
            'bedsheets', 
            'cardio', 
            'cleaning',
            'drawing', 
            'eating_out', 
            'fasting', 
            'guitar', 
            'laundry',
            'learning', 
            'meal_prep', 
            'meditation', 
            'nap',
            'nutribullet',
            'piano',
            'powerdrive',
            'reading',
            'shopping',
            'tech',
            'travel',
            'tv',
            'walk',
            'writing',
            ]

    journal = ['mood','journal']

    productivity = ['productive_min','distracting_min','neutral_min']

    fitness = ['active_energy',
                'heartrate',
                'heartrate_max',
                'heartrate_resting',
                'steps',
                'weight',
                'sleep',
                'sleep_end',
                'sleep_start',
                ]

    # Create a master list of the above lists
    json_lists = [tags, journal, productivity, fitness]

    # Loop through the above list, naming the dataframes after their respective json lists and saving to a another list
    df_list = []

    for jsons in json_lists:
        df_years = [json_to_df(jsons,year) for year in year_list]
        df = pd.concat(df_years,axis=0)
        df['date'] = pd.to_datetime(df['date'])
        # df = df.sort_values(by='date',axis=0)
        df[df['date'] < '2020-04-06'] #raised KeyError
        df_list.append(df)
    
    return df_list


if __name__ == '__main__':

    _df_list = exist_dataframes(os.getenv['PATH'])

    # Convert dataframes into lists of tuples.
    _exist_tags = to_tuple_list(_df_list[0])
    _exist_journal = to_tuple_list(_df_list[1]) # TODO scale 1-9 in SQL insert statement
    _exist_rescuetime = to_tuple_list(_df_list[2]) # TODO convert min to hours in SQL insert statement
    _exist_garmin = to_tuple_list(_df_list[3])

    os.chdir(os.getenv['PATH'])

    _mood_charts = pd.read_csv('mood_charts.csv')
    _mood_charts = to_tuple_list(_mood_charts)
    # TODO: mood_charts.columns = [Date,Mood,Sleep,Cardio,Meditate,Mood_Note] #scale mood 1-7 in SQL insert statement
    
    _bullet_journal = pd.read_csv('bullet_journal.csv')
    _bullet_journal = to_tuple_list(_bullet_journal)
    # TODO: bullet_journal.columns - [Date,Mood,Sleep,Steps,Cardio,Meditate,Mood_Note,Fasting,Cheat Meals,Read,Draw,Learn,Write,Guitar] #scale mood 1-5
    
    with authenticate_gmail_api(os.getenv['CREDENTIALS']) as service:
        _remarkable = get_email_content(service,query="from:my@remarkable.com")
        _mynetdiary = get_email_content(service,query="from:no-reply@mynetdiary.net")
    
    with closing(open(os.getenv['API_KEY'], "r")) as file:
        _credentials = json.load(file)
        _KEY = _credentials.get('rescuetime').get('KEY')
        _rescuetime_tuple = get_rescuetime_daily(_KEY)

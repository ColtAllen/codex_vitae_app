from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from contextlib import closing
import json

from datetime import date
from dateutil.relativedelta import relativedelta

import pandas as pd

from db_module import db_create, db_historical, db_prod, db_insert
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
    tags = ['bedsheets', 
            'cardio', 
            'cleaning',
            'dating',
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
            'reading',
            'shopping',
            'tech',
            'travel',
            'tv',
            'walk',
            'writing',
            ]

    journal = ['mood','mood_note']

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
        #df['date'] = pd.to_datetime(df['date'])
        # df = df.sort_values(by='date',axis=0)
        df[df['date'] < '2020-04-06'] #raised KeyError
        df = df.dropna()
        df_list.append(df)
    
    return df_list

def to_tuple_gen(df):
    """Convert a pandas DF for database insertion.

    Args:
        df: The pandas dataframe to be converted
    
    Returns: 
        tuple_list: A list of tuples.
        """
    
    tuple_gen = list(df.itertuples(index=False,name=None))

    for tuple_ in tuple_gen:
        yield (tuple_,)

if __name__ == '__main__':

    _df_list = exist_dataframes(os.getenv('DIR'))

    # Convert dataframes into tuple lists.
    _exist_tags = list(_df_list[0].itertuples(index=False,name=None))
    _exist_journal = list(_df_list[1].itertuples(index=False,name=None))
    _exist_rescuetime = list(_df_list[2].itertuples(index=False,name=None))
    _exist_garmin = list(_df_list[3].itertuples(index=False,name=None))

    # Convert CSV files into tuple generators.
    os.chdir(os.getenv('DIR'))

    _mood_charts = pd.read_csv('mood_charts.csv')
    _mood_charts = list(_mood_charts.itertuples(index=False,name=None))
    
    _bullet_journal = pd.read_csv('bullet_journal.csv')
    _bullet_journal = list(_bullet_journal.itertuples(index=False,name=None))

    os.chdir(os.getenv('CONFIG'))

    # Perform API calls for production data.
    with authenticate_gmail_api(os.getenv('CREDENTIALS')) as service:
        _remarkable = get_email_content(service,query="from:my@remarkable.com")
        _mynetdiary = get_email_content(service,query="from:no-reply@mynetdiary.net")
    
    _rescuetime = get_rescuetime_daily(os.getenv('API_KEY'))

    # Convert reMarkable and MyNetDiary data into tuple generators.
    _remarkable = reMarkableParsing().run(_remarkable)
    _fitness = fitness_parsing(_mynetdiary)
    _nutrition = nutrition_parsing(_mynetdiary)

    _hist_list = [_exist_tags,
                 _exist_journal,
                 _exist_rescuetime, 
                 _exist_garmin,
                 _mood_charts,
                 _bullet_journal,
                ]

    _prod_list = [_rescuetime,
                 _remarkable,
                 _fitness,
                 _nutrition,
                ]

    # Create DB and perform insertions.
    db_create(os.getenv('DB_PATH'))
    db_historical(os.getenv('DB_PATH'), _hist_list)
    db_prod(os.getenv('DB_PATH'), _prod_list)

    # TODO: Add SQL update statements to fix bad entries.

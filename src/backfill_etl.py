from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import contextlib
import json

from datetime import date
from dateutil.relativedelta import relativedelta

import pandas as pd

from db_module import to_tuple_list
from api_requests import authenticate_gmail_api, get_email_content, get_rescuetime_daily
from text_processing import reMarkableParsing, fitness_parsing, nutrition_parsing

class ExistBackfill:
    """Converts specified data fields from Exist JSON files into format for database insertion.

    Attributes:
        filepath: A string containing the filepath to the Exist data extract.
        """

    def __init__(self, filepath):
        """Inits ExistBackfill class from filepath."""
        self.filepath = os.chdir(f'{filepath}/exist_full_extract')

        # Specify years of data to retrieve as a list:
        self.year_list = ['2020', '2021']

        # Create lists of desired data fields. 
        # Each list will be inserted into its own database table.
        self.tags = ['alcohol',
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

        self.journal = ['mood','journal']

        self.productivity = ['productive_min','distracting_min','neutral_min']

        self.fitness = ['active_energy',
                    'heartrate',
                    'heartrate_max',
                    'heartrate_resting',
                    'steps',
                    'weight',
                    'sleep',
                    'sleep_end',
                    'sleep_start',
                    ]

    def json_to_df(self, var_list, year):
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

            # TODO specify exception.
            except:
                dataframe = pd.DataFrame(df).rename(columns={"value": json_list.split(".")[0]})

        return dataframe

    def dataframe_list(self):
        """Create a Pandas DF from a list of Exist json files.

        Args:
            jsons: A list identifying data variables of interest.
            year: A string specifying the year in the json name.
        
        Returns: 
            df_list: A list of Pandas Dataframes containing all Exist data. 
            """

        # Create a master list of the above lists
        json_lists = [self.tags, self.journal, self.productivity, self.fitness]

        # Loop through the above list, naming the dataframes after their respective json lists and saving to a another list
        df_list = []

        for jsons in json_lists:
            df_years = [self.json_to_df(jsons,year) for year in self.year_list]
            df = pd.concat(df_years,axis=0)
            df['date'] = pd.to_datetime(df['date'])
            # df = df.sort_values(by='date',axis=0)
            df[df['date'] < '2020-04-06'] #raised KeyError
            df_list.append(df)
        
        return df_list


if __name__ == '__main__':

    # TODO: create_db_tables()

    exist = ExistBackfill(os.getenv['PATH'])

    df_list = exist.dataframe_list()
   
    # Convert dataframes into lists of tuples.
    exist_tags = to_tuple_list(df_list[0])
    exist_journal = to_tuple_list(df_list[1]) # TODO scale 1-9 in SQL insert statement
    exist_rescuetime = to_tuple_list(df_list[2]) # TODO convert min to hours in SQL insert statement
    exist_garmin = to_tuple_list(df_list[3])

    # TODO: Context Manager WITH statement
    mood_charts = pd.read_csv('mood_charts.csv')
    mood_charts = to_tuple_list(mood_charts)
    #mood_charts.columns = [Date,Mood,Sleep,Cardio,Meditate,Mood_Note] #scale mood 1-7 in SQL insert statement
    
    # TODO: Context Manager WITH statement
    bullet_journal = pd.read_csv('bullet_journal.csv')
    bullet_journal = to_tuple_list(mood_charts)
    #bullet_journal.columns - [Date,Mood,Sleep,Steps,Cardio,Meditate,Mood_Note,Fasting,Cheat Meals,Read,Draw,Learn,Write,Guitar] #scale mood 1-5
    
    # TODO: Context Manager WITH statement
    service = authenticate_gmail_api(os.getenv['CREDENTIALS'])
    remarkable = get_email_content(service,query="from:my@remarkable.com")
    mynetdiary = get_email_content(service,query="from:no-reply@mynetdiary.net")
    
    # TODO: Context Manager WITH statement
    with open(os.getenv['API_KEY'] "r") as file:
        credentials = json.load(file)
    KEY = credentials.get('rescuetime').get('KEY')

    rescuetime_tuple = get_rescuetime_daily(KEY)

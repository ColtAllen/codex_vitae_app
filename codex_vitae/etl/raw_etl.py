from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from contextlib import closing
import json

import datetime
import sqlite3

import pandas as pd

from sqlite_module import db_create, db_historical, db_prod
from api_requests import authenticate_gmail_api, get_email_content, get_rescuetime_daily
from text_processing import reMarkableParsing, fitness_parsing, nutrition_parsing


# Configure Environment Variables.
DATA_DIR = os.getenv('DATA_DIR')
CRED = os.getenv('CRED')
API_KEY = os.getenv('API_KEY')

    
def json_to_df(var_list, year):
    """
    Create a Pandas DF from a list of Exist json files.

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

    return dataframe


def exist_dataframes(filepath):
    """
    Creates a list of Pandas dataframes containing all Exist data.

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
        df = df[df['date'] > '2020-04-06']
        df_list.append(df)
    
    return df_list

def to_tuple_gen(df):
    """
    Convert a pandas DF for database insertion.

    Args:
        df: The pandas dataframe to be converted
    
    Returns: 
        tuple_list: A list of tuples.
    """
    
    tuple_gen = list(df.itertuples(index=False,name=None))

    for tuple_ in tuple_gen:
        yield (tuple_,)

if __name__ == '__main__':

    _df_list = exist_dataframes(DATA_DIR)

    # Change directory to where files will be written.
    os.chdir(DATA_DIR)

    # Convert dataframes into CSVs and tuple lists.
    _exist_rescuetime = _df_list[2].dropna()
    _exist_rescuetime.to_csv('exist_rescuetime.csv',index=False)
    _exist_rescuetime = list(_exist_rescuetime.itertuples(index=False,name=None))

    _df_list[3].to_csv('exist_garmin.csv',index=False)
    _exist_garmin = list(_df_list[3].itertuples(index=False,name=None))

    # Remove in nulls in Exist Journal DF before converting to CSV and tuple list.
    _exist_journal = _df_list[1].dropna()
    _exist_journal.to_csv('exist_journal.csv',index=False)
    _exist_journal = list(_exist_journal.itertuples(index=False,name=None))

    # Fill in nulls in Exist Tags DF before converting to CSV and tuple list.
    _exist_tags = _df_list[0].fillna(0)
    _exist_tags.to_csv('exist_tags.csv',index=False)
    _exist_tags = list(_exist_tags.itertuples(index=False,name=None))

    # Load CSVs, fill in nulls, and convert intointo tuple generators.
    _mood_charts = pd.read_csv('mood_charts.csv')
    _mood_charts = _mood_charts.fillna(0)
    _mood_charts.to_csv('mood_charts.csv',index=False)
    _mood_charts = list(_mood_charts.itertuples(index=False,name=None))
    
    _bullet_journal = pd.read_csv('bullet_journal.csv')
    _bullet_journal = _bullet_journal.fillna(0)
    _bullet_journal.to_csv('bullet_journal.csv',index=False)
    _bullet_journal = list(_bullet_journal.itertuples(index=False,name=None))

    # Perform API calls for production data.
    # GMail API calls only return 100 results, so multiple calls must be made and appended together
    date1_ = str(datetime.date(2021, 5, 1))
    date2_ = str(datetime.date(2021, 7, 18))
    date3_ = str(datetime.date(2021, 10, 25))
    date4_ = str(datetime.date(2022, 1, 18))
    
    with closing(authenticate_gmail_api(CRED)) as service:
        _remarkable = get_email_content(service,query=f"from:my@remarkable.com,before:{date1_}")
        _remarkable1 = get_email_content(service,query=f"from:my@remarkable.com,after:{date1_},before:{date2_}")
        _remarkable2 = get_email_content(service,query=f"from:my@remarkable.com,after:{date2_},before:{date3_}")
        _remarkable3 = get_email_content(service,query=f"from:my@remarkable.com,after:{date3_},before:{date4_}")
        _remarkable.extend(_remarkable1)
        _remarkable.extend(_remarkable2)
        _remarkable.extend(_remarkable3)
        _mynetdiary = get_email_content(service,query=f"from:no-reply@mynetdiary.net")
    
    _rescuetime = get_rescuetime_daily(API_KEY)

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
    db = f'{DATA_DIR}/db'
    db_create(db)
    db_prod(db, _prod_list)
    db_historical(db, _hist_list)

    os.chdir(DATA_DIR)

    # Update entries.
    con = sqlite3.connect(db)
    cur = con.cursor()

    rsctm_update = """
            INSERT INTO rescuetime
            (date, prd_hours, dst_hours, neut_hours)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET date = excluded.date
            """

    jrnl_update = """
            UPDATE remarkable
                SET mood = ? ,
                    entry = ?
                WHERE date = ?
            """

    fitness_update = """
            UPDATE fitness
                SET pulse = ? ,
                    sleep = ? ,
                    deep_sleep = ? ,
                    light_sleep = ? ,
                    rem_sleep = ? ,
                    awakes = ? ,
                    daily_steps = ?,
                    calories_out = ?
                WHERE date = ?
            """

    # Read backfill files for RescueTime, Journal, and Fitness
    updt_rsctm = [(day,p,d,n) for (day,p,d,n) in json.load(open('rt_backfill.json', 'r'))]
    updte_jrnl = [(mood,entry,day) for (mood,entry,day) in json.load(open('journal_backfill.json', 'r'))]
    updt_ftnss = [(p,s,ds,ls,rs,a,ds,c,day) for (p,s,ds,ls,rs,a,ds,c,day) in json.load(open('fitness_backfill.json', 'r'))]

    cur.executemany(rsctm_update,updt_rsctm)
    cur.executemany(jrnl_update,updte_jrnl)
    cur.executemany(fitness_update,updt_ftnss)

    # Convert production tables to CSVs
    _rescuetime = pd.read_sql('select * from rescuetime order by date', con)
    _rescuetime.to_csv('rescuetime.csv',index=False)

    _remarkable = pd.read_sql('select * from remarkable order by date', con)
    _remarkable.to_csv('remarkable.csv',index=False)

    _fitness = pd.read_sql('select * from fitness order by date', con)
    _fitness.to_csv('fitness.csv',index=False)

    _nutrition = pd.read_sql('select * from nutrition order by date', con)
    _nutrition.to_csv('nutrition.csv',index=False)

    _journal_prod = pd.read_sql('select * from journal_view order by date', con)
    _journal_prod.to_csv('journal_prod.csv',index=False)

    _rescuetime_prod = pd.read_sql('select * from rescuetime_view order by date', con)
    _rescuetime_prod.to_csv('rescuetime_prod.csv',index=False)

    con.commit()
    con.close()

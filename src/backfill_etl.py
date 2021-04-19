import os
import json
import pandas as pd






os.chdir(os.getenv['PATH'])

def exist_dataframes(var_list, year):
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

        except:
            dataframe = pd.DataFrame(df).rename(columns={"value": json_list.split(".")[0]})

    return dataframe

    
if __name__ == '__main__':

    # Specify years of data to retrieve as a list:
    year_list = ['2020', '2021']

    # Create lists of desired data fields. 
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
        df_years = [exist_dataframes(jsons,year) for year in year_list]
        df = pd.concat(df_years,axis=0)
        df['date'] = pd.to_datetime(df['date'])
        # df = df.sort_values(by='date',axis=0)
        df[df['Effective Date'] < '2020-04-06']
        df_list.append(df)

    #SQLite Tuple conversions Go HERE
    df_list[0] = exist_tags
    df_list[1] = exist_journal # scale 1-9
    df_list[2] = exist_productivity # convert min to hours
    df_list[3] = exist_fitness
        

 
    


    # Search the last two weeks of emails for MyNetDiary nutrition reports.
    date_ = str(date.today()-relativedelta.relativedelta(days=14))
    service = authenticate_email_api_local()
    mynetdiary = get_email_bodies(service,query=f"from:no-reply@mynetdiary.net,after:{date_}")

    #Confirm two weekly reports were returned.
    assert(len(mynetdiary) == 2)















    dir() #displays all attributes of an object
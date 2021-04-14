import os
import json
import requests
import logging

# from datetime import date
# from dateutil import relativedelta

import pandas as pd



def rescuetime_get_daily(KEY):
    """Use the RescueTime API to get daily totals for time spent on personal digital devices.
    Args:
        KEY: RescueTime API Key.
    Returns:
        rescuetime_dict: A dictionary of days and total, productive, distracting, and neutral hours.

    """
    
    # Consider only querying for yesterday in the future. For now we are returning the past two weeks.
    #yesterday = str(date.today()-relativedelta.relativedelta(days=1))
    #assert(iter_result[0].get('date')== yesterday)

    url = f'https://www.rescuetime.com/anapi/daily_summary_feed?key={KEY}'

    r = requests.get(url) # Make Request
    iter_result = r.json()

    rescuetime_dict = {}

    days = [day.get('date') for day in iter_result]
    all_hours = [day.get('total_hours') for day in iter_result]
    prod_hours = [day.get('all_productive_hours') for day in iter_result]
    dist_hours = [day.get('all_distracting_hours') for day in iter_result]
    neut_hours = [day.get('neutral_hours') for day in iter_result]
    
    rescuetime_dict['date'] = days
    rescuetime_dict['all_hours'] = all_hours
    rescuetime_dict['prod_hours'] = prod_hours
    rescuetime_dict['dist_hours'] = dist_hours
    rescuetime_dict['neut_hours'] = neut_hours

    return rescuetime_dict


if __name__ == '__main__':

    logger = logging.getLogger(__name__)

    os.chdir('/mnt/c/Users/colta/portfolio/codex_vitae_app/config')

    with open("rescuetime_cred.json", "r") as file:
        credentials = json.load(file)
        KEY = credentials.get('rescuetime').get('KEY')

    rescuetime_dict = rescuetime_get_daily(KEY)

    rescuetime_dict = pd.DataFrame(rescuetime_dict)

    logger.info(rescuetime_dict.info())

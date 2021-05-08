from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
from dateutil.parser import parse

from datetime import date
from dateutil.relativedelta import relativedelta

import pandas as pd

class reMarkableParsing:
    """Extract date, mood rating, and journal entry from raw email bodies."""

    def clean_emails(self, text: str) -> str:
        """Removes HTML and CSS syntax, line breaks, and footer from journal entries.

        Args:
            text: A string of raw email text.

        Returns:
            clean_text: A string of clean text data.
        """

        # Remove HTML tags
        tag_re = re.compile(r'<[^>]+>')
        text = tag_re.sub('', text)
        # Remove line breaks
        text = text.replace("\\r\\n","")
        # Remove apostrophe breaks
        text = text.replace("\\'","")
        # Remove CSS syntx
        text = text.replace("b'p, li { white-space: pre-wrap; }","")
        # Remove Remarkable Footer
        clean_text = text.replace(" --Sent from my reMarkable paper tabletGet yours at www.remarkable.comPS: You cannot reply to this email'","")

        return clean_text

    def mood_rating(self, text: str) -> float:
        """Extracts mood rating from journal entry, accounting for spacing inconsistencies.

        Args:
            text: A string of cleaned text containing mood rating.

        Returns:
            rating: Mood rating as a float.
        """

        try:
            p = re.compile(r'Mood: \d')
            rating =  float(p.search(text).group().split(":")[1])
        except AttributeError:
            p = re.compile(r'Mood:\d')
            rating =  float(p.search(text).group().split(":")[1])
        
        finally:
            pass

        return rating

    def journal_date(self, text: str):
        """Extracts date of journal entry and converts to datetime format.

        Args:
            text: A string of cleaned text containing date.
        Returns:
            date: Date as datetime type.
        """

        date_ = parse(text.split("Mood")[0]).date()

        return date_

    def journal_entry(self, text: str) -> str:
        """Extracts journal entry from cleaned text.

        Arguments:
            text: A string of cleaned text.
        Returns:
            entry: A string of journal entry.
        """

        entry = str(text.split(":")[1])[2:]

        return entry
    
    def run(self, email_list):
        """Arranges all journal data in format required for database insertion.

        Returns:
            email_list: A list of strings containing raw emails to be processed.
            journal_tuple: A list of tuples containing parsed journal data.
        """

        # Emails containing PDF attachments instead of text must be removed.
        for entry in email_list:
            if entry == "b'6\\x89\\xde'":
                email_list.remove(entry)

        clean_text = [self.clean_emails(entry) for entry in email_list]
        mood = [self.mood_rating(entry) for entry in clean_text]
        date_ = [self.journal_date(entry) for entry in clean_text]
        journal = [self.journal_entry(entry) for entry in clean_text]

        journal_tuple = [(day,m,j) for (day,m,j) in zip(date_, mood,journal)]
        
        return journal_tuple

def fitness_parsing(email_list: list) -> list:
    """Use Pandas functions to parse fitness data from MyNetDiary emails for database insertion.

    Arguments:
        email_list: List of strings containing raw HTML from MyNetDiary emails.
    Returns:
        fitness_tuples: A list of tuples containing pertinent fitness data.
    """

    df_list = []

    for email_ in email_list:

        # Get substring of Fitness table.
        fitness_table = email_.split("Measurements")[1].replace("\\r\\n","").split("Nutrition")[0]
        fitness_df = pd.read_html(fitness_table)[0]

        # Fix mislabled sleep data columns and add a REM sleep column.
        fitness_df['Deep Sleep'] = fitness_df['Awakes,']
        fitness_df['Awakes'] = fitness_df['Deep Sleep,']
        fitness_df['REM Sleep'] = fitness_df['Sleep,'] - fitness_df['Deep Sleep'] - fitness_df['Light Sleep,']

        # Select pertinent columns and append to df list for concatenation.
        fitness_df = fitness_df[[
            'Date', 
            'Weight, lbs', 
            'BMR, cals',
            'Pulse,', 
            'Sleep,',
            'Deep Sleep', 
            'Light Sleep,',
            'REM Sleep',
            'Awakes',
            'Daily Steps,',
            'Calories Out, cals'
            ]]

        df_list.append(fitness_df)

    fitness_df = pd.concat(df_list,axis=0)
    
    # Convert dataframe into list of tuples.
    fitness_tuples = list(fitness_df.itertuples(index=False,name=None))

    return fitness_tuples

def nutrition_parsing(email_list: list) -> list:
    """Use Pandas functions to parse nutrition data from MyNetDiary emails for database insertion.

    Arguments:
        email_list: List of strings containing raw HTML from MyNetDiary emails.
    Returns:
        nutrition_tuples: A list of tuples containing pertinent nutrition data.
    """

    df_list = []

    for email_ in email_list:

        # Get substring of Nutrition table.
        nutrition_table = email_.split("Measurements")[1].replace("\\r\\n","").split("Nutrition")[1].split("Activities")[0]

        # Find the indices of the days of the week for date assignments.
        mon_idx = nutrition_table.find('Monday')
        tue_idx = nutrition_table.find('Tuesday')
        wed_idx = nutrition_table.find('Wednesday')
        thu_idx = nutrition_table.find('Thursday')
        fri_idx = nutrition_table.find('Friday')
        sat_idx = nutrition_table.find('Saturday')
        sun_idx = nutrition_table.find('Sunday')

        day_find = [mon_idx,tue_idx,wed_idx,thu_idx,fri_idx,sat_idx,sun_idx]

        # Find date strings in HTML table and format as dates.
        date_list = [parse(nutrition_table[day:].split("</span")[0]).date() for day in day_find if day is not -1]

        # Revert to previous year for NYE week.
        date_list = [(day - relativedelta(years=1) if date.today().strftime("%m%d") < day.strftime("%m%d") else day) for day in date_list]

        nutrition_df = pd.read_html(nutrition_table,parse_dates=True,header=1)

        # Retrieve rows containing daily totals.
        nutrition_df = nutrition_df[0][nutrition_df[0]['Unnamed: 0'].isnull()].reset_index()
        nutrition_df['Date'] = date_list

        # Select pertinent columns and append to df list for concatenation.
        nutrition_df = nutrition_df[[
            'Date',
            'Calories',
            'Total Fat,\xa0g',
            'Total Carbs,\xa0g',
            'Protein,\xa0g',
            'Saturated Fat,\xa0g',
            'Sodium,\xa0mg',
            'Net Carbs,\xa0g',
            ]]
        
        df_list.append(nutrition_df)

    nutrition_df = pd.concat(df_list,axis=0)

    nutrition_tuples = list(nutrition_df.itertuples(index=False,name=None))

    return nutrition_tuples





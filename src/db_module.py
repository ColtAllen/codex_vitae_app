from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from contextlib import closing

import sqlite3

def create_db_tables(db_path):
    """Create all SQLite tables.

    Args:
        db_path: A string containing the full directory and database name.
    """

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    con.execute('SELECT SQLITE_VERSION()')
    data = cur.fetchone()
    print("SQLite version: %s" % data) 
    cur.close()

    #save a CREATE TABLE statement to a variable

    #Create the table
    con.executescript("""
        DROP TABLE IF EXISTS rescuetime;
        DROP TABLE IF EXISTS remarkable;
        DROP TABLE IF EXISTS fitness;
        DROP TABLE IF EXISTS nutrition;
        DROP TABLE IF EXISTS exist_tags;
        DROP TABLE IF EXISTS exist_journal;
        DROP TABLE IF EXISTS exist_time;
        DROP TABLE IF EXISTS exist_fitness;
        DROP TABLE IF EXISTS mood_charts;
        DROP TABLE IF EXISTS bullet_journal;
        DROP VIEW IF EXISTS journal_view;

        CREATE TABLE rescuetime (
            date text PRIMARY KEY,
            prd_hours float NOT NULL,
            dst_hours float NOT NULL,
            neut_hours float NOT NULL
        );

        CREATE TABLE remarkable (
            date text PRIMARY KEY,
            mood float NOT NULL,
            entry text NOT NULL
        );

        CREATE TABLE fitness (
            date text PRIMARY KEY,
            weight float,
            bmr float,
            pulse float,
            sleep float,
            deep_sleep float,
            light_sleep float,
            rem_sleep float,
            awakes float,
            daily_steps float,
            calories_out float
        );

        CREATE TABLE nutrition (
            date text PRIMARY KEY,
            calories float,
            total_fat float,
            total_carbs float,
            protein float,
            trans_fat float,
            sat_fat float,
            sodium float,
            net_carbs float,
            fiber float
        );

        CREATE TABLE exist_tags (
            date text PRIMARY KEY,
            alcohol integer,
            bedsheets integer,
            cardio integer,
            cleaning integer,
            drawing integer,
            eating_out integer,
            fasting integer,
            guitar integer,
            laundry integer,
            learning integer,
            meal_prep integer,
            meditation integer,
            nap integer,
            nutribullet integer,
            piano integer,
            powerdrive integer,
            reading integer,
            shopping integer,
            tech integer,
            travel integer,
            tv integer,
            walk integer,
            writing integer
        );

        CREATE TABLE exist_journal (
            date text PRIMARY KEY,
            mood float,
            entry text
        );

        CREATE TABLE exist_time (
            date text PRIMARY KEY,
            prd_hours float,
            dst_hours float,
            neut_hours float
        );

        CREATE TABLE exist_fitness (
            date text PRIMARY KEY,
            active_cal float,
            pulse float,
            pulse_max float,
            pulse_rest float,
            steps float,
            weight float,
            sleep float,
            sleep_end float,
            sleep_start float,
        );

        CREATE TABLE mood_charts (
            date text PRIMARY KEY,
            mood float,
            sleep float,
            cardio integer,
            meditate integer,
            mood_note text
        );

        CREATE TABLE bullet_journal (
            date text PRIMARY KEY,
            mood float,
            sleep float,
            steps float,
            cardio integer,
            meditate integer,
            mood_note text,
            fasting integer,
            cheat_meals integer,
            read integer,
            draw integer,
            learn integer,
            write integer,
            guitar integer
        );

        CREATE VIEW journal_view (
            SELECT date, (mood-4)/3 as mood, mood_note FROM mood_chart
            UNION
            SELECT date, (mood-5)/4 as mood, mood_note FROM bullet_journal
            UNION
            SELECT date, (mood-3)/2 as mood, entry FROM exist_journal
            UNION
            SELECT date, (mood-5)/4 as mood, entry FROM remarkable
        )

    """)

    con.close()


def row_generator(tuple_list):
    for tuple_ in tuple_list:
        yield (tuple_,)


sql = """
INSERT INTO rescuetime
    (date, prod_hours, dist_hours, neut_hours)
VALUES (?, ?, ?, ?)
ON CONFLICT(date) DO UPDATE SET date = excluded.date
"""

def insert_rescuetime(db_path, sql):
    con = sqlite3.connect(db_path) 
    con.row_factory = sqlite3.Row

    with con:
            con.executemany(sql,(row[0],row_generator()))
    
    con.close()
    return cur.lastrowid


def insert_journal(journal_tuple):
    con = sqlite3.connect("/mnt/c/Users/colta/portfolio/codex_vitae_app/data/testdb.sqlite") # connect to the database
    cur = con.cursor() # instantiate a cursor obj to execute SQL statements
    sql = """
        INSERT INTO journal
            (date, mood, entry)
        VALUES (?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """
    con.row_factory = sqlite3.Row
    for row in journal_tuple:
        cur.execute(sql,(row[0],row[1],row[2]))
    con.close()
    return cur.lastrowid

def to_tuple_list(df):
    """Convert a pandas DF into a list of tuples for database insertion.

    Args:
        df: The pandas dataframe to be converted
    
    Returns: 
        tuple_list: A list of tuples.
        """
    
    tuple_list = list(df.itertuples(index=False,name=None))

    return tuple_list
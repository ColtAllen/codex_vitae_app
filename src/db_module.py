from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from contextlib import closing

import sqlite3

def create_db_tables(db_path):
    """Create all SQLite tables.

    Args:
        db_path: A string containing the full directory and database name
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
        DROP TABLE IF EXISTS ;
        DROP TABLE IF EXISTS ;
        DROP TABLE IF EXISTS ;
        DROP TABLE IF EXISTS ;
        DROP TABLE IF EXISTS ;
        DROP TABLE IF EXISTS ;
        DROP TABLE IF EXISTS ;
        DROP TABLE IF EXISTS ;
        DROP TABLE IF EXISTS ;
        DROP TABLE IF EXISTS ;
        DROP TABLE IF EXISTS ;

        CREATE TABLE rescuetime_emails (
            date text PRIMARY KEY,
            prd_hours float,
            dst_hours float,
            neut_hours float
        );

        CREATE TABLE journal_emails (
            date text PRIMARY KEY,
            mood float,
            entry text;
        );

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
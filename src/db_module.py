from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from contextlib import closing
import sqlite3

def db_create(db_path):
    """Create all SQLite database tables and views.

    Args:
        db_path: A string containing the full directory and database name.
    
    Returns:
        db_ver: A string containing the SQLite3 version.    
    """

    con = sqlite3.connect(db_path)

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
        DROP VIEW IF EXISTS rescuetime_view;

        CREATE TABLE rescuetime(
            date text PRIMARY KEY,
            prd_hours float NOT NULL,
            dst_hours float NOT NULL,
            neut_hours float NOT NULL
        );

        CREATE TABLE remarkable(
            date text PRIMARY KEY,
            mood float NOT NULL,
            entry text NOT NULL
        );

        CREATE TABLE fitness(
            date text PRIMARY KEY,
            weight float,
            bmr float,
            pulse integer,
            sleep float,
            deep_sleep float,
            light_sleep float,
            rem_sleep float,
            awakes float,
            daily_steps integer,
            calories_out integer
        );

        CREATE TABLE nutrition(
            date text PRIMARY KEY,
            calories integer,
            total_fat integer,
            total_carbs integer,
            protein integer,
            sat_fat integer,
            sodium integer,
            net_carbs integer
        );

        CREATE TABLE exist_tags(
            alcohol integer,
            date text PRIMARY KEY,
            bedsheets integer,
            cardio integer,
            cleaning integer,
            dating integer,
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
            reading integer,
            shopping integer,
            tech integer,
            travel integer,
            tv integer,
            walk integer,
            writing integer
        );

        CREATE TABLE exist_journal(
            mood float,
            date text PRIMARY KEY,
            entry text
        );

        CREATE TABLE exist_time(
            prd_mins float,
            date text PRIMARY KEY,
            dst_mins float,
            neut_mins float
        );

        CREATE TABLE exist_fitness(
            active_cal float,
            date text PRIMARY KEY,
            pulse integer,
            pulse_max integer,
            pulse_rest integer,
            steps integer,
            weight float,
            sleep float,
            sleep_end float,
            sleep_start float
        );

        CREATE TABLE mood_charts(
            date text PRIMARY KEY,
            mood float,
            sleep integer,
            cardio integer,
            meditate integer,
            mood_note text
        );

        CREATE TABLE bullet_journal(
            date text PRIMARY KEY,
            mood float,
            sleep integer,
            steps integer,
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

        CREATE VIEW journal_view(date, mood, entry)
        AS
            SELECT date, (mood-4)/3 as mood, mood_note FROM mood_charts
            UNION
            SELECT date, (mood-3)/2 as mood, mood_note FROM bullet_journal
            UNION
            SELECT date, (mood-5)/4 as mood, entry FROM exist_journal
            UNION
            SELECT date, (mood-5)/4 as mood, entry FROM remarkable
        ;

        CREATE VIEW rescuetime_view(date, prd_hours, dst_hours, neut_hours)
        AS
            SELECT
            date, 
            prd_mins/60 as prd_hours,
            dst_mins/60 as dst_hours,
            neut_mins/60 as neut_hours
            FROM exist_time
            UNION
            SELECT * FROM rescuetime
        ;

        """)

    ver = con.execute('SELECT SQLITE_VERSION()').fetchone()
    db_ver = f"SQLite version: {ver}"
    con.close()

    return db_ver


def db_insert(db_path, sql, tuple_gen):
    """Insert data into a SQLite DB table.

    Args:
        db_path: String containing the full directory and database name. 
        sql: String containing SQL insertion statement.
        tuple_gen: Generator object containing date tuples to be inserted.
    """

    con = sqlite3.connect(db_path)
    # TODO: Does row_factory have any impact on performance?
    con.row_factory = sqlite3.Row
    
    with con:
        con.executemany(sql,tuple_gen)
        # cur = con.cursor()
        # row_count = cur.lastrowid
    con.close()
    
    # TODO: Add row_count to logger rather than returned by function.
    # return row_count


def db_historical(db_path, gen_list):
    """Insert data into historical DB tables.

    Args:
        db_path: String containing the full directory and database name. 
        gen_list: List of generator objects containing date tuples to be inserted.
    """

    tags_sql = """
        INSERT INTO exist_tags (
            alcohol,
            date,
            bedsheets,
            cardio,
            cleaning,
            dating,
            drawing,
            eating_out,
            fasting,
            guitar,
            laundry,
            learning,
            meal_prep,
            meditation,
            nap,
            nutribullet,
            piano,
            reading,
            shopping,
            tech,
            travel,
            tv,
            walk,
            writing)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    exist_mood_sql = """
        INSERT INTO exist_journal
            (mood, date, entry)
        VALUES (?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    exist_time_sql = """
        INSERT INTO exist_time
            (prd_mins, date, dst_mins, neut_mins)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    exist_fit_sql = """
        INSERT INTO exist_fitness (
            active_cal,
            date,
            pulse,
            pulse_max,
            pulse_rest,
            steps,
            weight,
            sleep,
            sleep_end,
            sleep_start)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    mood_charts_sql = """
        INSERT INTO mood_charts (
            date,
            mood,
            sleep,
            cardio,
            meditate,
            mood_note)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    bullet_sql = """
        INSERT INTO bullet_journal (
            date,
            mood,
            sleep,
            steps,
            cardio,
            meditate,
            mood_note,
            fasting,
            cheat_meals,
            read,
            draw,
            learn,
            write,
            guitar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """
    
    sql_list = [tags_sql,
                exist_mood_sql,
                exist_time_sql,
                exist_fit_sql,
                mood_charts_sql,
                bullet_sql,
                ]

    for sql, gen in zip(sql_list, gen_list):
        db_insert(db_path, sql, gen)


def db_prod(db_path, gen_list):
    """Insert data into production DB tables.
    
    Args:
        db_path: String containing the full directory and database name. 
        gen_list: Generator object containing date tuples to be inserted.
    """

    rt_sql = """
        INSERT INTO rescuetime
        (date, prd_hours, dst_hours, neut_hours)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    rmrkble_sql = """
        INSERT INTO remarkable
            (date, mood, entry)
        VALUES (?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    fit_sql = """
        INSERT INTO fitness (
            date,
            weight,
            bmr,
            pulse,
            sleep,
            deep_sleep,
            light_sleep,
            rem_sleep,
            awakes,
            daily_steps,
            calories_out)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    ntrtn_sql = """
        INSERT INTO nutrition (
            date,
            calories,
            total_fat,
            total_carbs,
            protein,
            sat_fat,
            sodium,
            net_carbs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    sql_list = [rt_sql,
                rmrkble_sql,
                fit_sql,
                ntrtn_sql,
                ]

    for sql, gen in zip(sql_list, gen_list):
        db_insert(db_path, sql, gen)


def db_backup(db_path):
    """Query entire database and save as .pkl and json objects.

    Args:
        db_path: String containing the full directory and database name. 

    Returns:
        Pickle and json files for each DB table.
    """

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Query from views
    cur.execute("select * from journal_view order by date")
    cur.execute("select * from rescuetime_view order by date")

    # Query from historical tables
    cur.execute("select * from exist_tags order by date")
    cur.execute("select * from exist_journal order by date")
    cur.execute("select * from exist_time order by date")
    cur.execute("select * from exist_fitness order by date")
    cur.execute("select * from mood_charts order by date")
    cur.execute("select * from bullet_journal order by date")

    # Query from production tables
    cur.execute("select * from rescuetime order by date")
    cur.execute("select * from remarkable order by date")
    cur.execute("select * from fitness order by date")
    cur.execute("select * from nutrition order by date")

    # TODO: Add this to each execution and create a list for pkl and jsonification
    results = cur.fetchall()

    con.close()

    pass

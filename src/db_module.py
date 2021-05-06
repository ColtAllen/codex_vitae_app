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
            pulse float,
            sleep float,
            deep_sleep float,
            light_sleep float,
            rem_sleep float,
            awakes float,
            daily_steps float,
            calories_out float
        );

        CREATE TABLE nutrition(
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

        CREATE TABLE exist_tags(
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

        CREATE TABLE exist_journal(
            date text PRIMARY KEY,
            mood float,
            entry text
        );

        CREATE TABLE exist_time(
            date text PRIMARY KEY,
            prd_hours float,
            dst_hours float,
            neut_hours float
        );

        CREATE TABLE exist_fitness(
            date text PRIMARY KEY,
            active_cal float,
            pulse float,
            pulse_max float,
            pulse_rest float,
            steps float,
            weight float,
            sleep float,
            sleep_end float,
            sleep_start float
        );

        CREATE TABLE mood_charts(
            date text PRIMARY KEY,
            mood float,
            sleep float,
            cardio integer,
            meditate integer,
            mood_note text
        );

        CREATE TABLE bullet_journal(
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

        CREATE VIEW journal_view(date, mood, entry)
        AS
            SELECT date, (mood-4)/3 as mood, mood_note FROM mood_chart
            UNION
            SELECT date, (mood-3)/2 as mood, mood_note FROM bullet_journal
            UNION
            SELECT date, (mood-5)/4 as mood, entry FROM exist_journal
            UNION
            SELECT date, (mood-5)/4 as mood, entry FROM remarkable
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
        gen_list: Generator object containing date tuples to be inserted.
    """

    tags_sql = """
        INSERT INTO exist_tags (
            date,
            alcohol,
            bedsheets,
            cardio,
            cleaning,
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
            powerdrive,
            reading,
            shopping,
            tech,
            travel,
            tv,
            walk,
            writing)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? ,?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? ,?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    exist_mood_sql = """
        INSERT INTO exist_journal
            (date, mood, entry)
        VALUES (?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    exist_time_sql = """
        INSERT INTO exist_time (
            date, prd_hours, dst_hours, neut_hours)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET date = excluded.date
        """

    exist_fit_sql = """
        INSERT INTO exist_fitness (
            date,
            active_cal,
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
            trans_fat,
            sat_fat,
            sodium,
            net_carbs,
            fiber)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    """Query entire database and save as .pkl objects.

    Args:
        db_path: String containing the full directory and database name. 

    Returns:
        Pickle files for each DB table.
    """

    # TODO: Create a new git branch for this addition.

    pass
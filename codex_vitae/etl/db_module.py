import os
import csv
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy import Column, Text, Float, Integer, Date

from etl.orm_models import Base, MoodCharts, BulletJournal, ExistJournal, reMarkable, JournalProd, RescueTimeProd

# Declare environment variables.
DB_URL = os.getenv('DB_URL')
DIR = os.getenv('DIR')

def orm_init():
    """Create SQLAlchemy session for DB activities."""
    
    return create_engine(DB_URL)


def insert_mood_charts(engine=orm_init()):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(f"{DIR}/mood_charts.csv", 'r') as f:
        csv_reader = csv.DictReader(f)

        for row in csv_reader:
            db_record = MoodCharts(
                date = datetime.datetime.strptime(row['Date'],"%Y-%m-%d"),
                mood = row['Mood'],
                sleep = row['Sleep'],
                cardio = row['Cardio'],
                mood_note = row['Mood_Note'],
            )
            session.add(db_record)

    session.commit()
    session.close()


def insert_bullet_journal(engine=orm_init()):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(f"{DIR}/bullet_journal.csv", 'r') as f:
        csv_reader = csv.DictReader(f)

        for row in csv_reader:
            db_record = BulletJournal(
                date = datetime.datetime.strptime(row['Date'],"%Y-%m-%d"),
                mood = row['Mood'],
                sleep = row['Sleep'],
                steps = row['Steps'],
                cardio = row['Cardio'],
                meditate = row['Meditate'],
                mood_note = row['Mood_Note'],
                fasting = row['Fasting'],
                cheat_meals = row['Cheat_Meals'],
                read = row['Read'],
                draw = row['Draw'],
                learn = row['Learn'],
                write = row['Write'],
                guitar = row['Guitar'],
            )
            session.add(db_record)

    session.commit()
    session.close()


def insert_exist_journal(engine=orm_init()):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(f"{DIR}/exist_journal.csv", 'r') as f:
        csv_reader = csv.DictReader(f)

        for row in csv_reader:
            db_record = ExistJournal(
                date = datetime.datetime.strptime(row['date'],"%Y-%m-%d"),
                mood = row['mood'],
                entry = row['mood_note'],
            )
            session.add(db_record)

    session.commit()
    session.close()


def insert_remarkable(engine=orm_init()):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(f"{DIR}/remarkable.csv", 'r') as f:
        csv_reader = csv.DictReader(f)

        for row in csv_reader:
            db_record = reMarkable(
                date = datetime.datetime.strptime(row['date'],"%Y-%m-%d"),
                mood = row['mood'],
                entry = row['entry'],
            )
            session.add(db_record)

    session.commit()
    session.close()


def insert_journal_prod(engine=orm_init()):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(f"{DIR}/journal_prod.csv", 'r') as f:
        csv_reader = csv.DictReader(f)

        for row in csv_reader:
            db_record = JournalProd(
                date = datetime.datetime.strptime(row['date'],"%Y-%m-%d"),
                mood = row['mood'],
                entry = row['entry'],
            )
            session.add(db_record)

    session.commit()
    session.close()


def insert_rescuetime_prod(engine=orm_init()):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(f"{DIR}/rescuetime_prod.csv", 'r') as f:
        csv_reader = csv.DictReader(f)

        for row in csv_reader:
            db_record = RescueTimeProd(
                date = datetime.datetime.strptime(row['date'],"%Y-%m-%d"),
                prd_hours = row['prd_hours'],
                dst_hours = row['dst_hours'],
                neut_hours = row['neut_hours'],
            )
            session.add(db_record)

    session.commit()
    session.close()

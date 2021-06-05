import os
import csv
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Float, Integer, Date

from orm_models import Base, MoodCharts, BulletJournal, ExistJournal, reMarkable

# Declare environment variables.
DB_URL = os.getenv('DB_URL')
os.chdir(os.getenv('DIR'))

# Create SQLAlchemy engine, DB schema, and session
engine = create_engine(DB_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

with open('mood_charts.csv', 'r') as f:
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

with open('bullet_journal.csv', 'r') as f:
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

with open('exist_journal.csv', 'r') as f:
    csv_reader = csv.DictReader(f)

    for row in csv_reader:
        db_record = ExistJournal(
            date = datetime.datetime.strptime(row['date'],"%Y-%m-%d"),
            mood = row['mood'],
            entry = row['mood_note'],
        )
        session.add(db_record)

with open('remarkable.csv', 'r') as f:
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



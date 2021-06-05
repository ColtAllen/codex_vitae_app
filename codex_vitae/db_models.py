import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Float, Integer, Date

DB_URL = os.getenv('DB_URL')

# create an engine
engine = create_engine(DB_URL)

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()

Base = declarative_base()

class RescueTime(Base):
    __tablename__ = 'rescuetime'

    date = Column(Date, primary_key=True)
    prd_hours = Column(Float)
    dst_hours = Column(Float)
    neut_hours = Column(Float)

    def __init__(self, date, prd_hours, dst_hours, neut_hours):
        self.date = date
        self.prd_hours = prd_hours
        self.dst_hours = dst_hours
        self.neut_hours = neut_hours


class reMarkable(Base):
    __tablename__ = 'remarkable'

    date = Column(Date, primary_key=True)
    mood = Column(Float)
    entry = Column(Text)

    def __init__(self, date, mood, entry):
        self.date = date
        self.mood = mood
        self.entry = entry


class Fitness(Base):
    __tablename__ = 'fitness'

    date = Column(Date, primary_key=True)
    weight = Column(Float)
    bmr = Column(Float)
    pulse = Column(Integer)
    sleep = Column(Float)
    deep_sleep = Column(Float)
    light_sleep = Column(Float)
    rem_sleep = Column(Float)
    awakes = Column(Float)
    daily_steps = Column(Integer)
    calories_out = Column(Integer)
    
    def __init__(self,
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
                 calories_out,
                 ):

        self.date = date
        self.weight = weight
        self.bmr = bmr
        self.pulse = pulse
        self.sleep = sleep
        self.deep_sleep = deep_sleep
        self.light_sleep = light_sleep
        self.rem_sleep = rem_sleep
        self.awakes = awakes
        self.daily_steps = daily_steps
        self.calories_out = calories_out


class Nutrition(Base):
    __tablename__ = 'nutrition'

    date = Column(Date, primary_key=True)
    calories = Column(Integer)
    total_fat = Column(Integer)
    total_carbs = Column(Integer)
    protein = Column(Integer)
    sat_fat = Column(Integer)
    sodium = Column(Integer)
    net_carbs = Column(Integer)

    def __init__(self,
                 date,
                 calories, 
                 total_fat, 
                 total_carbs, 
                 protein, 
                 sat_fat, 
                 sodium,
                 net_carbs,
                 ):

        self.date = date
        self.calories = calories
        self.total_fat = total_fat
        self.total_carbs = total_carbs
        self.protein = protein
        self.sat_fat = sat_fat
        self.sodium = sodium
        self.net_carbs = net_carbs


class ExistTags(Base):
    __tablename__ = 'exist_tags'

    alcohol = Column(Integer)
    date = Column(Date, primary_key=True)
    bedsheets = Column(Integer)
    cardio = Column(Integer)
    cleaning = Column(Integer)
    dating = Column(Integer)
    drawing = Column(Integer)
    eating_out = Column(Integer)
    fasting = Column(Integer)
    guitar = Column(Integer)
    laundry = Column(Integer)
    learning = Column(Integer)
    meal_prep = Column(Integer)
    meditation = Column(Integer)
    nap = Column(Integer)
    nutribullet = Column(Integer)
    piano = Column(Integer)
    reading = Column(Integer)
    shopping = Column(Integer)
    tech = Column(Integer)
    travel = Column(Integer)
    tv = Column(Integer)
    walk = Column(Integer)
    writing = Column(Integer)

    def __init__(self,
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
                 writing,
                 ):

        self.alcohol = alcohol
        self.date = date
        self.bedsheets = bedsheets
        self.cardio = cardio
        self.cleaning = cleaning
        self.dating = dating
        self.drawing = drawing
        self.eating_out = eating_out
        self.fasting = fasting
        self.guitar = guitar
        self.laundry = laundry
        self.learning = learning
        self.meal_prep = meal_prep
        self.meditation = meditation
        self.nap = nap
        self.nutribullet = nutribullet
        self.piano = piano
        self.reading = reading
        self.shopping = shopping
        self.tech = tech
        self.travel = travel
        self.tv = tv
        self.walk = walk
        self.writing = writing


class ExistJournal(Base):
    __tablename__ = 'exist_journal'

    mood = Column(Float)
    date = Column(Date, primary_key=True)
    entry = Column(Text)

    def __init__(self, mood, date, entry):
        self.mood = mood
        self.date = date
        self.entry = entry


class ExistTime(Base):
    __tablename__ = 'exist_time'

    prd_hours = Column(Float)
    date = Column(Date, primary_key=True)
    dst_hours = Column(Float)
    neut_hours = Column(Float)

    def __init__(self, prd_hours, date, dst_hours, neut_hours):
        self.prd_hours = prd_hours
        self.date = date
        self.dst_hours = dst_hours
        self.neut_hours = neut_hours


class ExistFitness(Base):
    __tablename__ = 'exist_fitness'

    active_cal = Column(Float)
    date = Column(Date, primary_key=True)
    pulse = Column(Integer)
    pulse_max = Column(Integer)
    pulse_rest = Column(Integer)
    steps = Column(Integer)
    weight = Column(Float)
    sleep = Column(Float)
    sleep_end = Column(Float)
    sleep_start = Column(Float)
    
    def __init__(self,
                 active_cal,
                 date,
                 pulse,
                 pulse_max,
                 pulse_rest,
                 steps,
                 weight,
                 sleep,
                 sleep_end,
                 sleep_start,
                 ):

        self.active_cal = active_cal
        self.date = date
        self.pulse = pulse
        self.pulse_max = pulse_max
        self.pulse_rest = pulse_rest
        self.steps = steps
        self.weight = weight
        self.sleep = sleep
        self.sleep_end = sleep_end
        self.sleep_start = sleep_start


class MoodCharts(Base):
    __tablename__ = 'mood_charts'

    date = Column(Date, primary_key=True)
    mood = Column(Float)
    sleep = Column(Integer)
    cardio = Column(Integer)
    meditate = Column(Integer)
    mood_note = Column(Text)

    def __init__(self, 
                 date,
                 mood, 
                 sleep,
                 cardio,
                 meditate,
                 mood_note,
                 ):
                 
        self.date = date
        self.mood = mood
        self.sleep = sleep
        self.cardio = cardio
        self.meditate = meditate
        self.mood_note = mood_note


class BulletJournal(Base):
    __tablename__ = 'bullet_journal'

    date = Column(Date, primary_key=True)
    mood = Column(Float)
    sleep = Column(Integer)
    steps = Column(Integer)
    cardio = Column(Integer)
    meditate = Column(Integer)
    mood_note = Column(Text)
    fasting = Column(Integer)
    cheat_meals = Column(Integer)
    read = Column(Integer)
    draw = Column(Integer)
    learn = Column(Integer)
    write = Column(Integer)
    guitar = Column(Integer)

    def __init__(self, 
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
                 guitar,
                 ):

        self.date = date
        self.mood = mood
        self.sleep = sleep
        self.steps = steps
        self.cardio = cardio
        self.meditate = meditate
        self.mood_note = mood_note
        self.fasting = fasting
        self.cheat_meals = cheat_meals
        self.read = read
        self.draw = draw
        self.learn = learn
        self.write = write
        self.guitar = guitar

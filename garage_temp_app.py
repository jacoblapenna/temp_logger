#! /usr/bin/python

from datetime import datetime as dt
import matplotlib.pyplot as plt
from sense_hat import SenseHat
from flask import Flask
import psycopg2 as db
import time

app = Flask(__name__)

conn = db.connect("dbname=garage_temps")
cur = conn.cursor()

table = "test"
cur.execute(f"CREATE TABLE IF NOT EXISTS {table} (time float, temp float);")

sense = SenseHat()

def get_temp():
    """ get temp from sensors, averages, and converts to Fahrenheit """

    # get temp from humidity sensor
    h_temp = sense.get_temperature_from_humidity()
    # get te,p from pressure sensor
    p_temp = sense.get_temperature_from_pressure()

    # get average of two sensors, convert, and return
    return round(((h_temp + p_temp) / 2)*(9/5) + 32, 2)

def insert_temp():
    """ get's current temp and time and inserts into database """

    # get temp data and present time
    temp = get_temp()
    timestamp = time.time()

    # insert new temp with time of temp data
    cur.execute(f"INSERT INTO {table} (time, temp) VALUES ({timestamp}, {temp});")

    # commit entry to database
    conn.commit()

def record_data():
    """ run in another process to log data """

    while True:
        try:
            insert_temp()
            time.sleep(1)
        except KeyboardInterrupt:
            break

"""
One child process to log data
One child process to plot logged data
main process serves page that shows plot
"""

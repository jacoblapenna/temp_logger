#! /usr/bin/python

from datetime import datetime as dt
import matplotlib.pyplot as plt
from sense_hat import SenseHat
from flask import Flask, render_template
from flask_socketio import SocketIO
import psycopg2 as db
import time

app = Flask(__name__)
socketio = SocketIO(app)

conn = db.connect("dbname=garage_temps")
cur = conn.cursor()

table = "test"
cur.execute(f"CREATE TABLE IF NOT EXISTS {table} (time float, temp float);")

sense = SenseHat()

def get_ip_address():
    """ get the server's ip """

    ip_address = '127.0.0.1'  # Default to localhost
    s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM) # setup a socket object

    try:
        s.connect(('1.1.1.1', 1))  # does not have to be reachable
        ip_address = s.getsockname()[0]
    finally:
	    s.close()

    return ip_address

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

@app.route("/")
def homepage():
    return render_template("index.html")

if __name__ == "__main__":
    ip = get_ip_address()
    print("Attempting to serve page on %s:%d" % (ip, 8080))
    socketio.run(app,
                 host=ip,
                 port=8080,
                 use_reloader=True,
                 debug=False,
                 extra_files=['templates/index.html'])

"""
One child process to log data
One child process to plot logged data
main process serves page that shows plot
"""

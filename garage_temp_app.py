#! /usr/bin/python

from matplotlib.dates import RRuleLocator, DAILY, HOURLY, rrulewrapper, DateFormatter
from flask import Flask, render_template
from flask_socketio import SocketIO
from multiprocessing import Process
import matplotlib.dates as pltdt
import matplotlib.pyplot as plt
from sense_hat import SenseHat
import socket as sock
import psycopg2 as pg
import pandas as pd
import numpy as np
import time

app = Flask(__name__)
socketio = SocketIO(app)

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

def insert_temp(connection, cursor, table):
    """ get's current temp and time and inserts into database """

    # get temp data and present time
    temp = get_temp()
    timestamp = time.time()

    # insert new temp with time of temp data
    cursor.execute(f"INSERT INTO {table} (time, temp) VALUES ({timestamp}, {temp});")

    # commit entry to database
    connection.commit()

def record_data(table):
    """ run in another process to log data """

    logger_conn = pg.connect("dbname=garage_temps")
    logger_curs = logger_conn.cursor()

    logger_curs.execute(f"CREATE TABLE IF NOT EXISTS {table} (time float, temp float);")

    while True:
        try:
            insert_temp(logger_conn, logger_curs, table)
            time.sleep(1)
        except KeyboardInterrupt:
            break

def plot_data():
    """ create png of plotted data for page to serve """

    plotter_conn = pg.connect("dbname=garage_temps")
    plotter_curs = plotter_conn.cursor()

    plotter_curs.execute(f"SELECT * FROM {table};")
    data = pd.DataFrame(np.array(plotter_curs.fetchall()), columns=["time", "temp"])
    critical_temp = 65

    x = [pltdt.epoch2num(t) for t in data["time"]]
    y = list(data["temp"])
    thresh = [critical_temp for n in range(len(x))]
    t_above = [True if t > critical_temp else False for t in y]
    t_below = [not b for b in t_above]

    fig, ax = plt.subplots(figsize=(8,5), dpi=300)
    plt.plot_date(x, y, '-', color="black", label="Temperature ($^\circ$F)")
    plt.plot_date(x, thresh, '--', color="grey", alpha=0.5, label=f"{critical_temp} $^\circ$F Threshold")
    plt.ylim(20, 100)
    plt.yticks([t for t in range(20, 101, 5)])
    plt.fill_between(x, thresh, y, where=t_above, interpolate=True, color="green", alpha=0.5)
    plt.fill_between(x, thresh, y, where=t_below, interpolate=True, color="red", alpha=0.5)
    plt.title("Garage Temperature vs Time Historian")
    plt.ylabel("Temperature ($^\circ$F)")
    plt.xlabel("Time")
    major_rule = rrulewrapper(DAILY, interval=1)
    major_locator = RRuleLocator(major_rule)
    ax.xaxis.set_major_locator(major_locator)
    major_formatter = DateFormatter("%a")
    ax.xaxis.set_major_formatter(major_formatter)
    minor_rule = rrulewrapper(HOURLY, interval=6)
    minor_locator = RRuleLocator(minor_rule)
    ax.xaxis.set_minor_locator(minor_locator)
    plt.legend()
    plt.grid(which="both")
    fig.savefig("static/img/temperature_vs_time.png", bbox_inches="tight")
    plt.close()

    plotter_conn.commit()
    plotter_conn.close()

@app.route("/")
def homepage():
    return render_template("index.html")

@socketio.on("update_plot")
def update_plot():
    """ update plot """

    time.sleep(5)
    plot_data()

    print("plot updated")
    socketio.emit("plot_updated")

if __name__ == "__main__":

    table = "test"

    logger = Process(target=record_data, args=(table,))
    logger.start()

    ip = get_ip_address()
    print("Attempting to serve page on %s:%d" % (ip, 8080))
    socketio.run(app,
                 host=ip,
                 port=8080,
                 use_reloader=True,
                 debug=False,
                 extra_files=['templates/index.html'])

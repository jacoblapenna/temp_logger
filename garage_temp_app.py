#! /usr/bin/python

from matplotlib.dates import DateFormatter, HourLocator
from flask import Flask, render_template
from flask_socketio import SocketIO
from multiprocessing import Process
from datetime import datetime as dt
import matplotlib.dates as pltdt
import matplotlib.pyplot as plt
import socket as sock
import psycopg2 as pg
import pandas as pd
import numpy as np
import time

app = Flask(__name__)
socketio = SocketIO(app)

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

def plot_data():
    """ create png of plotted data for page to serve """

    plotter_conn = pg.connect("dbname=garage_temps")
    plotter_curs = plotter_conn.cursor()

    plotter_curs.execute(f"SELECT * FROM {table};")
    data = pd.DataFrame(np.array(plotter_curs.fetchall()), columns=["time", "temp"])
    critical_temp = 65

    x = [pltdt.date2num(dt.fromtimestamp(t)) for t in data["time"]]
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
    major_locator = HourLocator(byhour=[0])
    ax.xaxis.set_major_locator(major_locator)
    major_formatter = DateFormatter("%a")
    ax.xaxis.set_major_formatter(major_formatter)
    minor_locator = HourLocator(byhour=[6, 12, 18])
    ax.xaxis.set_minor_locator(minor_locator)
    minor_formatter = DateFormatter("%H")
    ax.xaxis.set_major_formatter(minor_formatter)
    plt.legend()
    plt.grid(which="both")
    fig.savefig("/home/pi/Projects/Garage_Temp_Logger/static/img/temperature_vs_time.png", bbox_inches="tight")
    plt.close()

    plotter_conn.commit()
    plotter_conn.close()

@app.route("/")
def homepage():
    plot_data()
    return render_template("index.html")

if __name__ == "__main__":

    global table

    table = "initial_primer"

    ip = get_ip_address()
    print("Attempting to serve page on %s:%d" % (ip, 8080))
    socketio.run(app,
                 host=ip,
                 port=8080,
                 use_reloader=True,
                 debug=False,
                 extra_files=['templates/index.html'])

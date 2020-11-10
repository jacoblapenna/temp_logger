from sense_hat import SenseHat
import psycopg2 as pg
import time

sense = SenseHat()

table = "initial_primer"

logger_conn = pg.connect("dbname=garage_temps")
logger_curs = logger_conn.cursor()

logger_curs.execute(f"CREATE TABLE IF NOT EXISTS {table} (time float, temp float);")

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
    logger_curs.execute(f"INSERT INTO {table} (time, temp) VALUES ({timestamp}, {temp});")

    # commit entry to database
    logger_conn.commit()

def record_data():
    """ run in another process to log data """

    while True:
        try:
            insert_temp()
            time.sleep(60)
        except:
            logger_conn.close()
            break

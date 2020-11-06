from sense_hat import SenseHat
import psycopg2 as db

conn = db.connect("dbname=garage_temps")
cur = conn.cursor()

sense = SenseHat()

def get_temp():

    h_temp = sense.get_temperature_from_humidity()
    p_temp = sense.get_temperature_from_pressure()

    return round(((h_temp + p_temp) / 2)*(9/5) + 32, 2)

print(get_temp())

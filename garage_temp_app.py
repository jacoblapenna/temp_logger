from sense_hat import SenseHat
import psycopg2 as db

conn = db.connect("dbname=garage_temps")
cur = conn.cursor()

sense = SenseHat()

print(sense.get_temperature_from_humidity(), sense.get_temperature_from_pressure())

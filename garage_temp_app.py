from sense_hat import SenseHat
from flask import Flask
import matplotlib.pyplot as plt

sense = SenseHat()

print(sense.get_temperature())

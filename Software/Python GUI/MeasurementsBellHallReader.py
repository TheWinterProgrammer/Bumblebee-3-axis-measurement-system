
import time
import csv
from datetime import datetime
import numpy as np

# This script is used to measure the Hallbach gradient field with the help of the measure robot and the metrolab Hall sensor connected to the arduino.
# It is designed for the Bell 9900

class MeasurementsBellHallReader():
    def __init__(self):
        pass

def getValueofdata(data):
        try:
            data = data.decode("utf-8")
            #data = data.split()
            channel = int(data[2])
            sign = data[5]
            unfiltedB = data[6:11]
            factChecker = data[12:14]

            unfiltedB = float(unfiltedB)
            if factChecker == 'mT':
                 unfiltedB = unfiltedB*10**-3
            elif factChecker == 'µT':
                 unfiltedB = unfiltedB*10**-6
            elif factChecker == 'uT':
                 unfiltedB = unfiltedB*10**-6
            else:
                 unfiltedB = unfiltedB
            if sign == '-':
                unfiltedB = -unfiltedB
            else:
                 unfiltedB = unfiltedB
            rightValue = True
        except:
            unfiltedB = 0
            channel = 0
            rightValue = False
        return unfiltedB,channel,rightValue

#Test function to get the serial data
def getValueofdataTest(data):
     print(data)

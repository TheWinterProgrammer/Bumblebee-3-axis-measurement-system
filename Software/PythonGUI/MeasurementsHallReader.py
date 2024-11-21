import serial
import time
import csv
from datetime import datetime
import numpy as np

# This script is used to measure the Hallbach gradient field with the help of the measure robot and the metrolab Hall sensor connected to the arduino.
# It is designed for the arduino Hall box designed by Pavel

# It can be changed for other hall sensors if the structure of the arrow data stays the same

class Hallreader():
    def __init__(self):
        pass

def getValueofdata(data):
        data = data.split()
        totalB,totalBFac,vBx,vBxFac,vBy,vByFac,vBz,vBzFac = float(data[2]),data[3],float(data[5]),data[6],float(data[9]),data[10],float(data[13]),data[14]
        if totalBFac == b'mT,':
            totalBFac = 0.001
        else:
            totalBFac = 1
        if vBxFac == b'mT,':
            vBxFac =  0.001
        else:
            vBxFac = 1
        if vByFac == b'mT,':
            vByFac =  0.001
        else:
            vByFac = 1
        if vBzFac == b'mT,':
            vBzFac =  0.001
        else:
            vBzFac = 1
        totalB = totalB*totalBFac
        vBx = vBx*vBxFac
        vBy = vBy*vByFac
        vBz = vBz*vBzFac
        data = [vBx,vBy,vBz,totalB]
        return(data)
    
